"""Aggregation helpers for the summary endpoint and CSV export."""
from __future__ import annotations

import csv
import io
from collections import defaultdict
from datetime import datetime, timezone
from typing import List

from models import (
    Category,
    CategoryTotal,
    Expense,
    MonthlyTotal,
    Summary,
)


def compute_summary(expenses: List[Expense]) -> Summary:
    now = datetime.now(timezone.utc)
    month_key = f"{now.year}-{now.month:02d}"

    total = 0.0
    month_total = 0.0
    by_category: dict[Category, float] = defaultdict(float)
    by_month: dict[str, float] = defaultdict(float)

    for e in expenses:
        total += e.amount
        by_category[e.category] += e.amount
        m = e.date.strftime("%Y-%m")
        by_month[m] += e.amount
        if m == month_key:
            month_total += e.amount

    category_totals = sorted(
        (
            CategoryTotal(category=c, total=round(t, 2))
            for c, t in by_category.items()
            if t > 0
        ),
        key=lambda c: c.total,
        reverse=True,
    )

    monthly_totals = [
        MonthlyTotal(month=m, total=round(by_month[m], 2))
        for m in sorted(by_month)
    ][-6:]

    return Summary(
        total=round(total, 2),
        month_total=round(month_total, 2),
        count=len(expenses),
        average_per_expense=round(total / len(expenses), 2) if expenses else 0.0,
        top_category=category_totals[0] if category_totals else None,
        by_category=category_totals,
        by_month=monthly_totals,
    )


def expenses_to_csv(expenses: List[Expense]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Date", "Category", "Description", "Amount"])
    for e in sorted(expenses, key=lambda x: x.date, reverse=True):
        writer.writerow(
            [e.date.isoformat(), e.category.value, e.description, f"{e.amount:.2f}"]
        )
    return buffer.getvalue()
