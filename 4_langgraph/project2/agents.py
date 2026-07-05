import uuid
from pydantic import BaseModel, Field
from typing import Optional, Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_agent.agent import create_agent
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langchain.agents.middleware import PIIMiddleware, TodoListMiddleware, HumanInTheLoopMiddleware
from langchain_mcp_adapters.client import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver
from tools import get_all_tools, get_mcp_client
from prompts import worker_system_prompt, evaluator_system_prompt
from logger import logger
from utils import HandleToolErrors

MAX_ATTEMPTS = 1
class EvaluatorOutput(BaseModel):
    feedback: str = Field(None, description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(False, description="whether the success criteria has been met")
    user_input_needed: bool = Field(False, description="True if more input or clarification is needed from user or if assistant is stuck")

class Agents():
    def __init__(self,):
        self.memory = None
        self.run_id = None
        self.client = None
        self.eval_agent = None
        self.task = None
        self.success_criteria = None
        self.attempts = 0
        self.todos = []
        self.paused = False
        self.tools = []
        self.worker = None

    async def setup(self):
        self.memory = InMemorySaver()
        self.run_id = str(uuid.uuid4())
        self.client = get_mcp_client()
        self.eval_agent = ChatOpenAI(model="gpt-5.4-mini").with_structured_output(EvaluatorOutput)
        self.tools.extend(get_all_tools())
        self.tools.extend(await self.client.get_tools())

    async def init_worker(self, session):
        self.tools.extend(await load_mcp_tools(session))
        self.worker = create_agent(
            model="openai:gpt-5.4-mini",
            tools=self.tools,
            system_prompt=worker_system_prompt,
            middleware=[PIIMiddleware("email"), TodoListMiddleware(),HandleToolErrors(),
                        HumanInTheLoopMiddleware(interrupt_on={"email": True, "request_human_help": True})],
            checkpointer=self.memory,
        )

    async def evaluate(self, message: str, success_criteria: str, last_reply: str, tools_used: list[str]):
        prompt = evaluator_system_prompt.format(
            success_criteria=success_criteria,
            message=message, last_reply=last_reply, tools_used=", ".join(tools_used)
        )
        return await self.eval_agent.ainvoke(prompt)

    async def run(self, message: str, success_criteria: str, history: list) -> list:
        self.task = message
        self.success_criteria = success_criteria or "The answer should be clear, correct and complete"
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{message}\n\nThe success criteria for this task are: {self.success_criteria}",
                }
            ]
        }
        async with self.client.session("playwright") as session:
            await self.init_worker(session)
            return await self._advance(payload, history + [{"role": "user", "content": message}])

    async def resume(self, history: list) -> list:
        """Approve the actions the worker paused on, and continue the turn."""
        payload = Command(resume={"decisions": [{"type": "approve"}] * self.pending_actions})
        return await self._advance(payload, history)

    async def _advance(self, payload, history: list) -> list:
        config = {"configurable": {"thread_id": self.run_id}}
        while True:
            result = None
            async for result in self.worker.astream(payload, config=config, stream_mode="values"):
                self.todos = result.get("todos", self.todos)

            if "__interrupt__" in result:
                actions = result["__interrupt__"][0].value["action_requests"]
                self.paused = True
                self.pending_actions = len(actions)
                described = "\n".join(action["description"] for action in actions)
                return history + [{"role": "assistant", "content": f"Waiting for your approval:\n{described}"}]

            self.paused = False
            reply = result["messages"][-1].content
            tools_used = [
                call["name"] for m in result["messages"] for call in (getattr(m, "tool_calls", None) or [])
            ]
            self.attempts += 1
            verdict = await self.evaluate(self.task, self.success_criteria, reply, tools_used)
            if verdict.success_criteria_met or verdict.user_input_needed or self.attempts >= MAX_ATTEMPTS:
                return history + [
                    {"role": "assistant", "content": reply},
                    {"role": "assistant", "content": f"Evaluator: {verdict.feedback}"},
                ]
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Your last response did not meet the success criteria. "
                                   f"Here is the feedback: {verdict.feedback}. Please keep working and address it.",
                    }
                ]
            }
