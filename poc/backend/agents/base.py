from backend.utils.llm import LLMService


class BaseAgent:
    name = "base_agent"

    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService()
