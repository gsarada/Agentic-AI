from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

class HandleToolErrors(AgentMiddleware):
    """Hand tool failures back to the model as a message so it can recover, rather than
    crashing."""

    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as e:
            return ToolMessage(content="Tool call failed with {e}. Try another approach", tool_call_id=request.tool_call["id"])
