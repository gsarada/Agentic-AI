"use client";

import { Pencil, Trash2, Inbox } from "lucide-react";
import type { Expense } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/format";
import { CategoryBadge } from "./CategoryBadge";

interface ExpenseListProps {
  expenses: Expense[];
  onEdit: (expense: Expense) => void;
  onDelete: (expense: Expense) => void;
}

export function ExpenseList({ expenses, onEdit, onDelete }: ExpenseListProps) {
  if (expenses.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center px-6 py-16 text-center">
        <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
          <Inbox className="h-6 w-6" />
        </span>
        <p className="font-medium text-slate-700">No expenses found</p>
        <p className="mt-1 text-sm text-slate-400">
          Try adjusting your filters, or add a new expense.
        </p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      {/* Desktop table */}
      <table className="hidden w-full text-left text-sm sm:table">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-5 py-3 font-medium">Date</th>
            <th className="px-5 py-3 font-medium">Description</th>
            <th className="px-5 py-3 font-medium">Category</th>
            <th className="px-5 py-3 text-right font-medium">Amount</th>
            <th className="px-5 py-3 text-right font-medium">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {expenses.map((e) => (
            <tr key={e.id} className="group transition hover:bg-slate-50">
              <td className="whitespace-nowrap px-5 py-3 text-slate-500">
                {formatDate(e.date)}
              </td>
              <td className="px-5 py-3 font-medium text-slate-800">
                {e.description}
              </td>
              <td className="px-5 py-3">
                <CategoryBadge category={e.category} />
              </td>
              <td className="whitespace-nowrap px-5 py-3 text-right font-semibold text-slate-900">
                {formatCurrency(e.amount)}
              </td>
              <td className="px-5 py-3">
                <div className="flex justify-end gap-1 opacity-0 transition group-hover:opacity-100">
                  <RowActions
                    onEdit={() => onEdit(e)}
                    onDelete={() => onDelete(e)}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Mobile cards */}
      <ul className="divide-y divide-slate-100 sm:hidden">
        {expenses.map((e) => (
          <li key={e.id} className="flex items-start justify-between gap-3 p-4">
            <div className="min-w-0">
              <p className="truncate font-medium text-slate-800">
                {e.description}
              </p>
              <div className="mt-1.5 flex items-center gap-2">
                <CategoryBadge category={e.category} />
                <span className="text-xs text-slate-400">
                  {formatDate(e.date)}
                </span>
              </div>
            </div>
            <div className="flex shrink-0 flex-col items-end gap-2">
              <span className="font-semibold text-slate-900">
                {formatCurrency(e.amount)}
              </span>
              <div className="flex gap-1">
                <RowActions
                  onEdit={() => onEdit(e)}
                  onDelete={() => onDelete(e)}
                />
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RowActions({
  onEdit,
  onDelete,
}: {
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <>
      <button
        onClick={onEdit}
        className="rounded-lg p-1.5 text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
        aria-label="Edit expense"
      >
        <Pencil className="h-4 w-4" />
      </button>
      <button
        onClick={onDelete}
        className="rounded-lg p-1.5 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
        aria-label="Delete expense"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </>
  );
}
