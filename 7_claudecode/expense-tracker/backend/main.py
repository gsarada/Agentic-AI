"""FastAPI backend for the Expensa expense tracker.

Provides a complete REST API mirroring the frontend's data model:
CRUD over expenses, an aggregated summary endpoint, and CSV export.
Data is persisted to a local JSON file (see storage.py).

Run with:  uvicorn main:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""
from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

import storage
from analytics import compute_summary, expenses_to_csv
from models import Expense, ExpenseInput, Summary

app = FastAPI(
    title="Expensa API",
    description="REST API for the Expensa expense tracker.",
    version="1.0.0",
)

# Allow the Next.js dev server (and common local ports) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/expenses", response_model=List[Expense])
def list_expenses() -> List[Expense]:
    return storage.list_expenses()


@app.post(
    "/api/expenses",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(payload: ExpenseInput) -> Expense:
    expense = Expense(**payload.model_dump())
    return storage.add_expense(expense)


@app.get("/api/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: str) -> Expense:
    expense = storage.get_expense(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/api/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: str, payload: ExpenseInput) -> Expense:
    existing = storage.get_expense(expense_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    updated = Expense(
        id=existing.id,
        created_at=existing.created_at,
        **payload.model_dump(),
    )
    result = storage.update_expense(expense_id, updated)
    assert result is not None
    return result


@app.delete("/api/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str) -> Response:
    if not storage.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/summary", response_model=Summary)
def summary() -> Summary:
    return compute_summary(storage.list_expenses())


@app.get("/api/export.csv", response_class=PlainTextResponse)
def export_csv() -> PlainTextResponse:
    csv_text = expenses_to_csv(storage.list_expenses())
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="expenses.csv"'},
    )
