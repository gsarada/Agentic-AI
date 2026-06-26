import asyncio
from dotenv import load_dotenv
from dataclasses import dataclass
from langchain_community.utilities import SerpAPIWrapper
from autogen_core import message_handler, RoutedAgent, MessageContext, AgentId
from autogen_core import SingleThreadedAgentRuntime
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime, GrpcWorkerAgentRuntimeHost

@dataclass
class Message:
    content: str

@dataclass
class Instruction:
    main_instruction: str
    sub_instruction: str | list

def search(query: str) -> str:
    """Use for searching on the internet"""
    serper = SerpAPIWrapper()
    return serper.run(query)

def get_client(model: str):
    if model == "llama3.2":
        model_client = OllamaChatCompletionClient(model=model)
    else:
        model_client = OpenAIChatCompletionClient(model=model)
    return model_client

class SubAgent(RoutedAgent):
    def __init__(self, name: str, model: str, tools: list) -> None:
        super().__init__(name)
        model_client = get_client(model)
        if tools:
            self._delegate = AssistantAgent(name, model_client, tools=tools, reflect_on_tool_use=True)
        else:
            self._delegate = AssistantAgent(name, model_client)

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages(messages=[text_message], cancellation_token=ctx.cancellation_token)
        return Message(content=response.chat_message.content)

class JudgeAgent(RoutedAgent):
    def __init__(self, name: str, model: str, instructions: Instruction) -> None:
        super().__init__(name)
        model_client = get_client(model)
        self._delegate = AssistantAgent(name, model_client)
        self._system_prompt = instructions.main_instruction
        self._agent_prompt = instructions.sub_instruction

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> Message:
        p1 = AgentId("Agent1", "default")
        p2 = AgentId("Agent2", "default")
        if isinstance(self._agent_prompt, str):
            agent_message = Message(content=self._agent_prompt)
            p1_response = await self.send_message(agent_message, p1)
            p2_response = await self.send_message(agent_message, p2)
        elif isinstance(self._agent_prompt, list):
            agent1_message = Message(content=self._agent_prompt[0])
            agent2_message = Message(content=self._agent_prompt[1])
            p1_response = await self.send_message(agent1_message, p1)
            p2_response = await self.send_message(agent2_message, p2)
        agents_responses = f"Agent1: {p1_response.content}\n Agent2: {p2_response.content}\n"
        text_message = TextMessage(content=f"{self._system_prompt}{agents_responses}Who wins? {message.content}", source="user")
        response = await self._delegate.on_messages(messages=[text_message], cancellation_token=ctx.cancellation_token)
        return Message(content=agents_responses + response.chat_message.content)

async def standalone():
    instructions = Instruction(
        sub_instruction="You are playing rock, paper, scissors. Respond only with the one word among the following - rock, paper, scisoors",
        main_instruction="You are judging a game of rock, paper, scissors. The players have made these choices -\n"
    )
    try:
        runtime = SingleThreadedAgentRuntime()
        runtime.start()
        await SubAgent.register(runtime, 'Agent1', lambda: SubAgent('Player1', model="gpt-4o-mini", tools=None))
        await SubAgent.register(runtime, 'Agent2', lambda: SubAgent('Player2', model="llama3.2", tools=None))
        await JudgeAgent.register(runtime, 'Judge', lambda: JudgeAgent('Judge', model="llama3.2",
                                                                       instructions=instructions))
        agent_id = AgentId("Judge", "default")
        message = Message(content="Go")
        response = await runtime.send_message(message, agent_id)
        print(response.content)
    except Exception as e:
        print(f"Exception {e} occurred")
    finally:
        await runtime.stop()
        await runtime.close()

distributed_instructions = {
    "instruction1": "To help with a decision whether to use claude code in a new software project, \
                    Please research and briefly respond with reasons in favor of choosing Claude code; the pros of claude code",
    "instruction2": "To help with a decision whether to use claude code in a new software project, \
                    Please research and briefly respond with reasons against choosing Claude code; the cons of claude code",
    "judge_instruction": "You must make a decision on whether to use Claude code for a software project. \
                         Your research team has come up with the following reasons for and against \
                         Based purely on the research from your team, please respond with your decision and a brief rationale \n"
}
async def distributed():

    try:
        instructions = Instruction(
            sub_instruction=[distributed_instructions["instruction1"], distributed_instructions["instruction2"]],
            main_instruction=distributed_instructions["judge_instruction"]
        )
        search_tool = FunctionTool(
            func=search,
            description="Use to search for latest/current information.",
            strict=True
        )
        agent_tools = [search_tool]
        host = GrpcWorkerAgentRuntimeHost(address="localhost:50052")
        host.start()
        runtime1 = GrpcWorkerAgentRuntime(host_address="localhost:50052")
        await runtime1.start()
        await SubAgent.register(runtime1, 'Agent1', lambda: SubAgent('Researcher1', model="gpt-4o-mini", tools=agent_tools))
        await SubAgent.register(runtime1, 'Agent2', lambda: SubAgent('Researcher2', model="gpt-4o-mini", tools=agent_tools))
        runtime2 = GrpcWorkerAgentRuntime(host_address="localhost:50052")
        await runtime2.start()
        await JudgeAgent.register(runtime2, 'Judge', lambda: JudgeAgent('Judge', model="llama3.2",
                                                                       instructions=instructions))
        agent_id = AgentId("Judge", "default")
        message = Message(content="Go")
        response = await runtime2.send_message(message, agent_id)
        print(response.content)
    except Exception as e:
        print(f"Exception {e} occurred")
    finally:
        await runtime1.stop()
        await runtime1.close()
        await runtime2.stop()
        await runtime2.close()
        await host.stop()

if __name__ == "__main__":
    load_dotenv(override=True)
    #asyncio.run(standalone())
    asyncio.run(distributed())
