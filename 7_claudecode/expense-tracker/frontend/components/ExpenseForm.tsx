"use client";

import { useState } from "react";
import type { Category, Expense, ExpenseInput } from "@/lib/types";
import { CATEGORIES } from "@/lib/types";
import { todayISO } from "@/lib/format";

interface ExpenseFormProps {
  initial?: Expense;
  onSubmit: (input: ExpenseInput) => void;
  onCancel: () => void;
}

interface FormErrors {
  amount?: string;
  date?: string;
  description?: string;
  category?: string;
}

export function ExpenseForm({ initial, onSubmit, onCancel }: ExpenseFormProps) {
  const [amount, setAmount] = useState(
    initial ? String(initial.amount) : ""
  );
  const [date, setDate] = useState(initial?.date ?? todayISO());
  const [category, setCategory] = useState<Category>(
    initial?.category ?? "Food"
  );
  const [description, setDescription] = useState(initial?.description ?? "");
  const [errors, setErrors] = useState<FormErrors>({});

  function validate(): FormErrors {
    const next: FormErrors = {};
    const parsed = Number(amount);
    if (!amount.trim()) {
      next.amount = "Amount is required.";
    } else if (Number.isNaN(parsed)) {
      next.amount = "Enter a valid number.";
    } else if (parsed <= 0) {
      next.amount = "Amount must be greater than 0.";
    } else if (parsed > 1_000_000) {
      next.amount = "Amount seems too large.";
    }

    if (!date) {
      next.date = "Date is required.";
    } else if (date > todayISO()) {
      next.date = "Date cannot be in the future.";
    }

    if (!description.trim()) {
      next.description = "Description is required.";
    } else if (description.trim().length > 120) {
      next.description = "Keep it under 120 characters.";
    }

    if (!CATEGORIES.includes(category)) {
      next.category = "Pick a category.";
    }
    return next;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length > 0) return;

    onSubmit({
      amount: Math.round(Number(amount) * 100) / 100,
      date,
      category,
      description: description.trim(),
    });
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Amount" error={errors.amount}>
          <div className="relative">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              $
            </span>
            <input
              type="number"
              inputMode="decimal"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="input-field pl-7"
              aria-invalid={!!errors.amount}
              autoFocus
            />
          </div>
        </Field>

        <Field label="Date" error={errors.date}>
          <input
            type="date"
            value={date}
            max={todayISO()}
            onChange={(e) => setDate(e.target.value)}
            className="input-field"
            aria-invalid={!!errors.date}
          />
        </Field>
      </div>

      <Field label="Category" error={errors.category}>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value as Category)}
          className="input-field"
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Description" error={errors.description}>
        <input
          type="text"
          placeholder="e.g. Lunch with team"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="input-field"
          maxLength={140}
          aria-invalid={!!errors.description}
        />
      </Field>

      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Cancel
        </button>
        <button type="submit" className="btn-primary">
          {initial ? "Save changes" : "Add expense"}
        </button>
      </div>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs font-medium text-red-600">{error}</p>}
    </div>
  );
}
