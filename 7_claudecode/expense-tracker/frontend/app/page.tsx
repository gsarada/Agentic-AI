"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Plus, Download, Sparkles, ArrowRight } from "lucide-react";
import { useExpensesContext } from "@/hooks/ExpensesContext";
import { useExpenseDialogs } from "@/hooks/useExpenseDialogs";
import { useToast } from "@/components/Toast";
import { computeSummary, expensesToCsv, sortByDateDesc } from "@/lib/analytics";
import { downloadFile } from "@/lib/download";
import { todayISO } from "@/lib/format";
import { PageHeader } from "@/components/PageHeader";
import { SummaryCards } from "@/components/SummaryCards";
import { SpendingCharts } from "@/components/SpendingCharts";
import { ExpenseList } from "@/components/ExpenseList";
import { DashboardSkeleton } from "@/components/Skeleton";

export default function DashboardPage() {
  const { expenses, loading, seedSampleData } = useExpensesContext();
  const { openAdd, startEdit, requestDelete, dialogs } = useExpenseDialogs();
  const { notify } = useToast();

  const summary = useMemo(() => computeSummary(expenses), [expenses]);
  const recent = useMemo(
    () => sortByDateDesc(expenses).slice(0, 5),
    [expenses]
  );

  const exportCsv = () => {
    if (expenses.length === 0) {
      notify("Nothing to export yet.", "info");
      return;
    }
    downloadFile(
      `expenses-${todayISO()}.csv`,
      expensesToCsv(sortByDateDesc(expenses))
    );
    notify("CSV exported.", "success");
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Dashboard" subtitle="Loading your finances…" />
        <DashboardSkeleton />
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="An overview of your spending at a glance."
      >
        <button onClick={exportCsv} className="btn-secondary">
          <Download className="h-4 w-4" />
          Export CSV
        </button>
        <button onClick={openAdd} className="btn-primary">
          <Plus className="h-4 w-4" />
          Add expense
        </button>
      </PageHeader>

      {expenses.length === 0 ? (
        <EmptyDashboard
          onAdd={openAdd}
          onSeed={() => {
            seedSampleData();
            notify("Sample data loaded.", "success");
          }}
        />
      ) : (
        <div className="space-y-6">
          <SummaryCards summary={summary} />
          <SpendingCharts summary={summary} />

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">
                Recent expenses
              </h2>
              <Link
                href="/expenses"
                className="flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <ExpenseList
              expenses={recent}
              onEdit={startEdit}
              onDelete={requestDelete}
            />
          </section>
        </div>
      )}

      {dialogs}
    </>
  );
}

function EmptyDashboard({
  onAdd,
  onSeed,
}: {
  onAdd: () => void;
  onSeed: () => void;
}) {
  return (
    <div className="card flex flex-col items-center justify-center px-6 py-20 text-center">
      <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
        <Sparkles className="h-7 w-7" />
      </span>
      <h2 className="text-xl font-semibold text-slate-900">
        Welcome to Expensa
      </h2>
      <p className="mt-2 max-w-sm text-sm text-slate-500">
        Start tracking your spending by adding your first expense, or load some
        sample data to explore the app.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <button onClick={onAdd} className="btn-primary">
          <Plus className="h-4 w-4" />
          Add your first expense
        </button>
        <button onClick={onSeed} className="btn-secondary">
          <Sparkles className="h-4 w-4" />
          Load sample data
        </button>
      </div>
    </div>
  );
}
