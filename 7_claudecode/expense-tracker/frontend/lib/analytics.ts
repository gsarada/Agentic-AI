import type { Category, Expense, ExpenseFilters } from "./types";
import { CATEGORIES } from "./types";

export interface CategoryTotal {
  category: Category;
  total: number;
}

export interface MonthlyTotal {
  /** YYYY-MM */
  month: string;
  /** Human label, e.g. "Mar 2026" */
  label: string;
  total: number;
}

export interface Summary {
  total: number;
  monthTotal: number;
  count: number;
  averagePerExpense: number;
  topCategory: CategoryTotal | null;
  byCategory: CategoryTotal[];
  byMonth: MonthlyTotal[];
}

function currentMonthKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function applyFilters(
  expenses: Expense[],
  filters: ExpenseFilters
): Expense[] {
  const term = filters.search.trim().toLowerCase();
  return expenses.filter((e) => {
    if (filters.category !== "All" && e.category !== filters.category) {
      return false;
    }
    if (filters.startDate && e.date < filters.startDate) return false;
    if (filters.endDate && e.date > filters.endDate) return false;
    if (term) {
      const haystack = `${e.description} ${e.category}`.toLowerCase();
      if (!haystack.includes(term)) return false;
    }
    return true;
  });
}

export function sortByDateDesc(expenses: Expense[]): Expense[] {
  return [...expenses].sort((a, b) => {
    if (a.date !== b.date) return a.date < b.date ? 1 : -1;
    return a.createdAt < b.createdAt ? 1 : -1;
  });
}

export function computeSummary(expenses: Expense[]): Summary {
  const monthKey = currentMonthKey();

  let total = 0;
  let monthTotal = 0;
  const categoryMap = new Map<Category, number>();
  const monthMap = new Map<string, number>();

  for (const e of expenses) {
    total += e.amount;
    categoryMap.set(e.category, (categoryMap.get(e.category) ?? 0) + e.amount);

    const m = e.date.slice(0, 7); // YYYY-MM
    monthMap.set(m, (monthMap.get(m) ?? 0) + e.amount);
    if (m === monthKey) monthTotal += e.amount;
  }

  const byCategory: CategoryTotal[] = CATEGORIES.map((category) => ({
    category,
    total: categoryMap.get(category) ?? 0,
  }))
    .filter((c) => c.total > 0)
    .sort((a, b) => b.total - a.total);

  const byMonth: MonthlyTotal[] = [...monthMap.entries()]
    .sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .slice(-6)
    .map(([month, t]) => {
      const [y, mo] = month.split("-");
      const label = new Date(Number(y), Number(mo) - 1, 1).toLocaleDateString(
        "en-US",
        { month: "short", year: "numeric" }
      );
      return { month, label, total: t };
    });

  return {
    total,
    monthTotal,
    count: expenses.length,
    averagePerExpense: expenses.length ? total / expenses.length : 0,
    topCategory: byCategory[0] ?? null,
    byCategory,
    byMonth,
  };
}

export function expensesToCsv(expenses: Expense[]): string {
  const header = ["Date", "Category", "Description", "Amount"];
  const escape = (v: string) => `"${v.replace(/"/g, '""')}"`;
  const rows = expenses.map((e) =>
    [e.date, e.category, escape(e.description), e.amount.toFixed(2)].join(",")
  );
  return [header.join(","), ...rows].join("\n");
}
