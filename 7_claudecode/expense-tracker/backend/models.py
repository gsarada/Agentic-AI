"""Pydantic models shared across the API."""
from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    FOOD = "Food"
    TRANSPORTATION = "Transportation"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    OTHER = "Other"


class ExpenseInput(BaseModel):
    """Payload for creating or updating an expense."""

    date: date
    amount: float = Field(gt=0, le=1_000_000, description="Amount in dollars")
    category: Category
    description: str = Field(min_length=1, max_length=120)

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, value: date) -> date:
        if value > datetime.now(timezone.utc).date():
            raise ValueError("date cannot be in the future")
        return value

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("description cannot be empty")
        return stripped

    @field_validator("amount")
    @classmethod
    def round_amount(cls, value: float) -> float:
        return round(value, 2)


class Expense(ExpenseInput):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class CategoryTotal(BaseModel):
    category: Category
    total: float


class MonthlyTotal(BaseModel):
    month: str
    total: float


class Summary(BaseModel):
    total: float
    month_total: float
    count: int
    average_per_expense: float
    top_category: Optional[CategoryTotal]
    by_category: List[CategoryTotal]
    by_month: List[MonthlyTotal]
