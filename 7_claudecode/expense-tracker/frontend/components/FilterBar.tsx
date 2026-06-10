"use client";

import { Search, X } from "lucide-react";
import type { Category, ExpenseFilters } from "@/lib/types";
import { CATEGORIES } from "@/lib/types";

interface FilterBarProps {
  filters: ExpenseFilters;
  onChange: (filters: ExpenseFilters) => void;
}

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const set = <K extends keyof ExpenseFilters>(
    key: K,
    value: ExpenseFilters[K]
  ) => onChange({ ...filters, [key]: value });

  const isDirty =
    filters.search !== "" ||
    filters.category !== "All" ||
    filters.startDate !== "" ||
    filters.endDate !== "";

  const reset = () =>
    onChange({ search: "", category: "All", startDate: "", endDate: "" });

  return (
    <div className="card p-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-12">
        <div className="md:col-span-4">
          <label className="mb-1 block text-xs font-medium text-slate-500">
            Search
          </label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={filters.search}
              onChange={(e) => set("search", e.target.value)}
              placeholder="Description or category…"
              className="input-field pl-9"
            />
          </div>
        </div>

        <div className="md:col-span-3">
          <label className="mb-1 block text-xs font-medium text-slate-500">
            Category
          </label>
          <select
            value={filters.category}
            onChange={(e) =>
              set("category", e.target.value as Category | "All")
            }
            className="input-field"
          >
            <option value="All">All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="mb-1 block text-xs font-medium text-slate-500">
            From
          </label>
          <input
            type="date"
            value={filters.startDate}
            max={filters.endDate || undefined}
            onChange={(e) => set("startDate", e.target.value)}
            className="input-field"
          />
        </div>

        <div className="md:col-span-2">
          <label className="mb-1 block text-xs font-medium text-slate-500">
            To
          </label>
          <input
            type="date"
            value={filters.endDate}
            min={filters.startDate || undefined}
            onChange={(e) => set("endDate", e.target.value)}
            className="input-field"
          />
        </div>

        <div className="flex items-end md:col-span-1">
          <button
            onClick={reset}
            disabled={!isDirty}
            className="btn-ghost w-full justify-center disabled:opacity-40"
            title="Clear filters"
          >
            <X className="h-4 w-4" />
            <span className="md:hidden">Clear</span>
          </button>
        </div>
      </div>
    </div>
  );
}
