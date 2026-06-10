"use client";

import { useMemo, useState } from "react";
import { Plus, Download } from "lucide-react";
import { useExpensesContext } from "@/hooks/ExpensesContext";
import { useExpenseDialogs } from "@/hooks/useExpenseDialogs";
import { useToast } from "@/components/Toast";
import {
  applyFilters,
  expensesToCsv,
  sortByDateDesc,
} from "@/lib/analytics";
import { downloadFile } from "@/lib/download";
import { formatCurrency, todayISO } from "@/lib/format";
import type { ExpenseFilters } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { FilterBar } from "@/components/FilterBar";
import { ExpenseList } from "@/components/ExpenseList";
import { ListSkeleton } from "@/components/Skeleton";

const EMPTY_FILTERS: ExpenseFilters = {
  search: "",
  category: "All",
  startDate: "",
  endDate: "",
};

export default function ExpensesPage() {
  const { expenses, loading } = useExpensesContext();
  const { openAdd, startEdit, requestDelete, dialogs } = useExpenseDialogs();
  const { notify } = useToast();
  const [filters, setFilters] = useState<ExpenseFilters>(EMPTY_FILTERS);

  const filtered = useMemo(
    () => sortByDateDesc(applyFilters(expenses, filters)),
    [expenses, filters]
  );

  const filteredTotal = useMemo(
    () => filtered.reduce((sum, e) => sum + e.amount, 0),
    [filtered]
  );

  const exportCsv = () => {
    if (filtered.length === 0) {
      notify("No expenses match your filters.", "info");
      return;
    }
    downloadFile(`expenses-${todayISO()}.csv`, expensesToCsv(filtered));
    notify(`Exported ${filtered.length} expense(s).`, "success");
  };

  return (
    <>
      <PageHeader
        title="Expenses"
        subtitle="Search, filter, edit, and export your records."
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

      <div className="space-y-4">
        <FilterBar filters={filters} onChange={setFilters} />

        {!loading && (
          <div className="flex items-center justify-between px-1 text-sm text-slate-500">
            <span>
              {filtered.length} expense{filtered.length === 1 ? "" : "s"}
            </span>
            <span>
              Total:{" "}
              <span className="font-semibold text-slate-800">
                {formatCurrency(filteredTotal)}
              </span>
            </span>
          </div>
        )}

        {loading ? (
          <ListSkeleton />
        ) : (
          <ExpenseList
            expenses={filtered}
            onEdit={startEdit}
            onDelete={requestDelete}
          />
        )}
      </div>

      {dialogs}
    </>
  );
}
