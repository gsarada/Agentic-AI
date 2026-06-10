"""Simple JSON-file persistence for expenses.

This keeps the demo backend dependency-free (no database needed) while still
persisting data across restarts. A thread lock guards concurrent writes from
uvicorn's worker threads.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict, List, Optional

from models import Expense

DATA_FILE = Path(__file__).parent / "data" / "expenses.json"
_lock = threading.Lock()


def _ensure_file() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def _read_raw() -> List[dict]:
    _ensure_file()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_raw(items: List[dict]) -> None:
    _ensure_file()
    DATA_FILE.write_text(
        json.dumps(items, indent=2, default=str), encoding="utf-8"
    )


def list_expenses() -> List[Expense]:
    with _lock:
        return [Expense(**item) for item in _read_raw()]


def get_expense(expense_id: str) -> Optional[Expense]:
    return next((e for e in list_expenses() if e.id == expense_id), None)


def add_expense(expense: Expense) -> Expense:
    with _lock:
        items = _read_raw()
        items.append(json.loads(expense.model_dump_json()))
        _write_raw(items)
    return expense


def update_expense(expense_id: str, updated: Expense) -> Optional[Expense]:
    with _lock:
        items = _read_raw()
        for i, item in enumerate(items):
            if item.get("id") == expense_id:
                items[i] = json.loads(updated.model_dump_json())
                _write_raw(items)
                return updated
    return None


def delete_expense(expense_id: str) -> bool:
    with _lock:
        items = _read_raw()
        remaining = [i for i in items if i.get("id") != expense_id]
        if len(remaining) == len(items):
            return False
        _write_raw(remaining)
        return True


def replace_all(expenses: List[Expense]) -> List[Expense]:
    with _lock:
        _write_raw([json.loads(e.model_dump_json()) for e in expenses])
    return expenses
