import uuid
import asyncio
from typing import Annotated, TypedDict, Dict, Any, Optional, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import aiosqlite
import tools
from tools import get_all_tools
from prompts import worker_system_prompt, evaluator_system_prompt, evaluator_user_prompt, evaluator_user_prompt_ext
from logger import logger

class EvaluatorOutput(BaseModel):
    feedback: str = Field(None, description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(False, description="whether the success criteria has been met")
    user_input_needed: bool = Field(False, description="True if more input or clarification is needed from user or if assistant is stuck")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    success_criteria: Optional[str]
    eval_result: EvaluatorOutput

class Assistants():
    def __init__(self):
        self.worker_with_tools = None
        self.evaluator_llm = None
        self.tools = None
        self.graph = None
        self.memory = None
        self.run_id = str(uuid.uuid4())

    async def setup(self):
        self.tools = await get_all_tools()
        worker_llm = ChatOpenAI(model="gpt-5.4-mini") #"llama3.2", base_url="http://127.0.0.1:11434/v1", api_key="ollama")
        self.worker_with_tools = worker_llm.bind_tools(self.tools)
        evaluator_llm = ChatOpenAI(model="gpt-5.4-mini") #model="llama3.2", base_url="http://127.0.0.1:11434/v1", api_key="ollama")
        self.evaluator_llm = evaluator_llm.with_structured_output(EvaluatorOutput)
        self.memory = InMemorySaver()
        await self.build_graph()
        logger.debug("Assistant setup completed")

    async def build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("worker", self.worker_agent)
        graph_builder.add_node("evaluator", self.evaluator_agent)
        graph_builder.add_node("tools", ToolNode(self.tools))

        graph_builder.add_edge(START, "worker")
        graph_builder.add_conditional_edges("worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_conditional_edges("evaluator", self.evaluator_router, {"END": END, "worker": "worker"})
        graph_builder.add_edge("tools", "worker")
        self.graph = graph_builder.compile(self.memory)
        logger.debug(self.graph.get_graph().draw_mermaid())

    def worker_agent(self, state: State) -> Dict[str, Any]:
        logger.debug(f"Input to worker agent - {state}")
        criteria = state["success_criteria"]
        criteria = criteria if criteria else "Response should be accurate or relevant"
        system_message = worker_system_prompt.format(success_criteria=criteria)
        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = self.worker_with_tools.invoke(messages)
        logger.debug(f" Worker agent output - {response}")
        return {"messages": [response]}

    def format_conversation(self, messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation
    def evaluator_agent(self, state: State) -> State:
        logger.debug(f"Input to evaluator agent - {state}")
        system_message = f"{evaluator_system_prompt}"
        history = self.format_conversation(state["messages"])
        last_message = state["messages"][-1].content
        previous_feedback = state["eval_result"].feedback if state["eval_result"] else None
        if previous_feedback:
            ext = evaluator_user_prompt_ext.format(feedback=previous_feedback)
        else:
            ext = ""
        user_message = evaluator_user_prompt.format(history=history, success_criteria=state["success_criteria"],
                                                    last_response=last_message, previous_feedback=ext)
        prompt = [SystemMessage(content=system_message), HumanMessage(content=user_message)]
        eval_result = self.evaluator_llm.invoke(prompt)
        logger.debug(f" Evaluator agent output - {eval_result}")

        new_state = {
            "messages": [
                {
                    "role": "assistant",
                    "content": f"Evaluator Feedback on this answer: {eval_result.feedback}",
                }
            ],
            "eval_result": eval_result
        }
        return new_state

    def worker_router(self, state: State) -> str:
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"

    def evaluator_router(self, state: State) -> str:
        eval_result = state["eval_result"]
        if eval_result.success_criteria_met or eval_result.user_input_needed:
            return "END"
        else:
            return "worker"


    async def run(self, message, success_criteria, history):
        try:
            config = {"configurable": {"thread_id": self.run_id}}
            state = {
                "messages": message,
                "success_criteria": success_criteria,
                "eval_result": EvaluatorOutput()
            }
            logger.debug(f"Input to run - {state}")
            response = await self.graph.ainvoke(state, config=config)
            logger.debug(response)
            user = {"role": "user", "content": message}
            reply = {"role": "assistant", "content": response["messages"][-2].content}
            feedback = {"role": "assistant", "content": response["messages"][-1].content}
            return history + [user, reply, feedback]
        except Exception as e:
            logger.error(f"Exception {e} occurred")
            user = {"role": "user", "content": message}
            reply = {"role": "assistant", "content": "Encountered error. Please try again"}
            feedback = {"role": "assistant", "content": ""}
            return history + [user, reply, feedback]


    def cleanup(self):
        if tools.ASYNC_BROWSER or tools.PLAYWRIGHT_CONTEXT:
            logger.debug("Cleaning up Playwright structures...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(tools.close_playwright())
