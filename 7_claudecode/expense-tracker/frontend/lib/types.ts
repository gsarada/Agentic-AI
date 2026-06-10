export const CATEGORIES = [
  "Food",
  "Transportation",
  "Entertainment",
  "Shopping",
  "Bills",
  "Other",
] as const;

export type Category = (typeof CATEGORIES)[number];

export interface Expense {
  id: string;
  /** ISO date string (YYYY-MM-DD) */
  date: string;
  /** Stored in major currency units (e.g. dollars) */
  amount: number;
  category: Category;
  description: string;
  /** ISO timestamp of when the record was created */
  createdAt: string;
}

/** Shape submitted by the expense form (no id / createdAt yet). */
export type ExpenseInput = Omit<Expense, "id" | "createdAt">;

export interface ExpenseFilters {
  search: string;
  category: Category | "All";
  startDate: string; // YYYY-MM-DD or ""
  endDate: string; // YYYY-MM-DD or ""
}
