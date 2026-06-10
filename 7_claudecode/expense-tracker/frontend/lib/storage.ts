import type { Expense } from "./types";
import { CATEGORIES } from "./types";

const STORAGE_KEY = "expense-tracker:expenses:v1";

function isValidExpense(value: unknown): value is Expense {
  if (typeof value !== "object" || value === null) return false;
  const e = value as Record<string, unknown>;
  return (
    typeof e.id === "string" &&
    typeof e.date === "string" &&
    typeof e.amount === "number" &&
    typeof e.description === "string" &&
    typeof e.category === "string" &&
    (CATEGORIES as readonly string[]).includes(e.category as string)
  );
}

/** Read all expenses from localStorage. Safe to call on the server (returns []). */
export function loadExpenses(): Expense[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isValidExpense);
  } catch {
    return [];
  }
}

export function saveExpenses(expenses: Expense[]): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(expenses));
  } catch {
    // Quota errors are non-fatal for this demo.
  }
}

/** Generate a unique id without external deps. */
export function generateId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}
