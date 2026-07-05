"""Run the Microsoft Agent Framework worker against the board as a subprocess.
Given a task id and a shared board path, the same worker joins the agent loop:
it points its board and file tools at the shared board and site, claims that
one task, builds what the task asks, and exits, leaving the rest of the board alone.

"""

from __future__ import annotations

import asyncio
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=r".*experimental.*")  # quiet MAF's import-time notices

from dotenv import load_dotenv  # noqa: E402
from agent_framework import Agent, MCPStdioTool  # noqa: E402
from agent_framework.openai import OpenAIChatClient  # noqa: E402

import board  # noqa: E402

load_dotenv(override=True)

MODEL = os.environ.get("WORKER_MODEL", "gpt-5.4-mini")
TASK_ID = int(sys.argv[1]) if len(sys.argv) > 2 else None
WORK_DIR = Path(sys.argv[2]).resolve()

client = OpenAIChatClient(model=MODEL)


def show_todos() -> list[dict]:
    """List every todo on the board. A goal has parent_id None; a step has parent_id set to its goal's id."""
    return board.list_todos()


def plan_steps(goal_id: int, steps: list[str]) -> dict:
    """Break a goal into an ordered checklist of steps on the board. Pass the goal's id and a short list of step descriptions."""
    return {"goal_id": goal_id, "step_ids": [board.add_step(goal_id, step) for step in steps]}


def complete_task(task_id: int, result: str) -> dict:
    """Mark a todo (a step or the goal) with this id as done and record a short result summary."""
    board.complete_todo(task_id, result)
    return {"task_id": task_id, "status": "done"}


INSTRUCTIONS = """
You are a careful worker with a shared todo board and a set of file tools.

Take the pending goal and see it through. Begin by laying out a short plan: the handful of concrete steps the work itself breaks down into, added to the board under the goal. Then carry them out with your file tools, marking each step done as you finish it. Once the steps are all done, close the goal. Your files live in the single folder your tools are allowed to use.
"""


async def main() -> None:
    board.claim_todo(TASK_ID)  # light up this one task on the shared board
    message = (
        f"You have claimed task #{TASK_ID} on the shared board. Work only that task and its steps. "
        f"When the work is built and checked, mark task #{TASK_ID} itself done with complete_task, then stop."
    )

    filesystem = MCPStdioTool(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(WORK_DIR)],
        cwd=str(WORK_DIR),  # start the server in the work dir so relative file names resolve there
    )
    async with filesystem:
        worker = Agent(
            client=client,
            instructions=INSTRUCTIONS,
            tools=[show_todos, plan_steps, complete_task, filesystem],
        )
        await worker.run(message)


if __name__ == "__main__":
    asyncio.run(main())
