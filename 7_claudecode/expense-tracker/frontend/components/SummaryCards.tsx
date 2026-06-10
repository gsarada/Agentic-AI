import {
  TrendingUp,
  CalendarDays,
  Receipt,
  Crown,
} from "lucide-react";
import type { Summary } from "@/lib/analytics";
import { formatCurrency } from "@/lib/format";

export function SummaryCards({ summary }: { summary: Summary }) {
  const cards = [
    {
      label: "Total spending",
      value: formatCurrency(summary.total),
      sub: `${summary.count} expense${summary.count === 1 ? "" : "s"}`,
      icon: TrendingUp,
      tint: "bg-brand-50 text-brand-600",
    },
    {
      label: "This month",
      value: formatCurrency(summary.monthTotal),
      sub: new Date().toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
      }),
      icon: CalendarDays,
      tint: "bg-emerald-50 text-emerald-600",
    },
    {
      label: "Avg / expense",
      value: formatCurrency(summary.averagePerExpense),
      sub: "across all records",
      icon: Receipt,
      tint: "bg-amber-50 text-amber-600",
    },
    {
      label: "Top category",
      value: summary.topCategory ? summary.topCategory.category : "—",
      sub: summary.topCategory
        ? formatCurrency(summary.topCategory.total)
        : "no data yet",
      icon: Crown,
      tint: "bg-purple-50 text-purple-600",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((c) => (
        <div
          key={c.label}
          className="card p-5 transition hover:shadow-card-hover"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-500">{c.label}</p>
            <span
              className={`flex h-9 w-9 items-center justify-center rounded-lg ${c.tint}`}
            >
              <c.icon className="h-5 w-5" />
            </span>
          </div>
          <p className="mt-3 text-2xl font-semibold tracking-tight text-slate-900">
            {c.value}
          </p>
          <p className="mt-1 text-xs text-slate-400">{c.sub}</p>
        </div>
      ))}
    </div>
  );
}
