import type { Category } from "./types";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatCurrency(amount: number): string {
  return currencyFormatter.format(Number.isFinite(amount) ? amount : 0);
}

/** Compact currency for charts / tight spaces, e.g. $1.2k */
export function formatCurrencyCompact(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number.isFinite(amount) ? amount : 0);
}

export function formatDate(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Returns today's date as YYYY-MM-DD in local time. */
export function todayISO(): string {
  const d = new Date();
  const tzOffset = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 10);
}

export const CATEGORY_COLORS: Record<Category, string> = {
  Food: "#f59e0b",
  Transportation: "#3b66f5",
  Entertainment: "#a855f7",
  Shopping: "#ec4899",
  Bills: "#ef4444",
  Other: "#64748b",
};

export const CATEGORY_BADGE: Record<Category, string> = {
  Food: "bg-amber-100 text-amber-800",
  Transportation: "bg-brand-100 text-brand-800",
  Entertainment: "bg-purple-100 text-purple-800",
  Shopping: "bg-pink-100 text-pink-800",
  Bills: "bg-red-100 text-red-800",
  Other: "bg-slate-100 text-slate-700",
};
