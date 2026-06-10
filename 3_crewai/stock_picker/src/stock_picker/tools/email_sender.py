from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class EmailSenderToolInput(BaseModel):
    """Input schema for EmailSenderTool."""
    company: str = Field(..., description="Name of the company.")
    ticker: str = Field(description="Stock ticker of the company")
    rationale: str = Field(description="Rationale behind picking this company for investment")

class EmailSenderTool(BaseTool):
    name: str = "Notifier"
    description: str = (
        "Use this tool to push notification to the user with the decision and 1 sentence rationale "
    )
    args_schema: Type[BaseModel] = EmailSenderToolInput

    def _run(self, company: str, ticker: str, rationale: str) -> str:
        print(f"User notification content : {company}:{ticker}:{rationale}")
        return "Email notification sent to user."
