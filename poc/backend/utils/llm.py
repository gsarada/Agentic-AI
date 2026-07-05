import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from backend.config import Settings, get_settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: ChatOpenAI | None = None

    @property
    def client(self) -> ChatOpenAI | None:
        if self.settings.llm_provider != "openai":
            return None
        if not self.settings.openai_api_key:
            return None
        if self._client is None:
            self._client = ChatOpenAI(
                model=self.settings.model,
                api_key=self.settings.openai_api_key,
                temperature=0.2,
            )
        return self._client

    def structured_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: type[BaseModel],
        fallback: BaseModel,
    ) -> BaseModel:
        client = self.client
        if client is None:
            logger.warning("llm_unavailable_using_fallback", model=output_model.__name__)
            return fallback

        try:
            structured = client.with_structured_output(output_model)
            result = structured.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            return result
        except Exception as exc:
            logger.error("llm_structured_completion_failed", error=str(exc))
            return fallback

    def text_completion(self, system_prompt: str, user_prompt: str, fallback: str = "") -> str:
        client = self.client
        if client is None:
            return fallback or "LLM is not configured. Set OPENAI_API_KEY in .env."

        try:
            response = client.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            return str(response.content)
        except Exception as exc:
            logger.error("llm_text_completion_failed", error=str(exc))
            return fallback


def serialize_list(values: list[str] | None) -> str:
    return json.dumps(values or [])


def deserialize_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def to_json(data: Any) -> str:
    return json.dumps(data, default=str)
