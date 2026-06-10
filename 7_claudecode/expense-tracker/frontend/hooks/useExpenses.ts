"use client";

import { useCallback, useEffect, useState } from "react";
import type { Expense, ExpenseInput } from "@/lib/types";
import {
  generateId,
  loadExpenses,
  saveExpenses,
} from "@/lib/storage";

export interface UseExpensesResult {
  expenses: Expense[];
  loading: boolean;
  addExpense: (input: ExpenseInput) => void;
  updateExpense: (id: string, input: ExpenseInput) => void;
  deleteExpense: (id: string) => void;
  seedSampleData: () => void;
  clearAll: () => void;
}

/**
 * Single source of truth for expense data, persisted to localStorage.
 * The `loading` flag covers the initial hydration read so the UI can show
 * skeletons and avoid a server/client markup mismatch.
 */
export function useExpenses(): UseExpensesResult {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  // Hydrate once on mount.
  useEffect(() => {
    setExpenses(loadExpenses());
    setLoading(false);
  }, []);

  // Persist whenever data changes (after initial load).
  useEffect(() => {
    if (!loading) saveExpenses(expenses);
  }, [expenses, loading]);

  const addExpense = useCallback((input: ExpenseInput) => {
    const expense: Expense = {
      ...input,
      id: generateId(),
      createdAt: new Date().toISOString(),
    };
    setExpenses((prev) => [expense, ...prev]);
  }, []);

  const updateExpense = useCallback((id: string, input: ExpenseInput) => {
    setExpenses((prev) =>
      prev.map((e) => (e.id === id ? { ...e, ...input } : e))
    );
  }, []);

  const deleteExpense = useCallback((id: string) => {
    setExpenses((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const clearAll = useCallback(() => setExpenses([]), []);

  const seedSampleData = useCallback(() => {
    setExpenses(buildSampleData());
  }, []);

  return {
    expenses,
    loading,
    addExpense,
    updateExpense,
    deleteExpense,
    seedSampleData,
    clearAll,
  };
}

function buildSampleData(): Expense[] {
  const now = new Date();
  const iso = (daysAgo: number) => {
    const d = new Date(now);
    d.setDate(d.getDate() - daysAgo);
    const tz = d.getTimezoneOffset() * 60000;
    return new Date(d.getTime() - tz).toISOString().slice(0, 10);
  };
  const samples: Array<[number, number, Expense["category"], string]> = [
    [1, 42.5, "Food", "Grocery run at Whole Foods"],
    [2, 18.0, "Transportation", "Uber to downtown"],
    [3, 64.99, "Shopping", "New running shoes"],
    [5, 120.0, "Bills", "Electricity bill"],
    [6, 32.75, "Entertainment", "Movie night + snacks"],
    [9, 15.4, "Food", "Lunch with team"],
    [12, 80.0, "Bills", "Internet & phone"],
    [18, 9.99, "Entertainment", "Streaming subscription"],
    [22, 55.2, "Shopping", "Household supplies"],
    [28, 27.6, "Transportation", "Gas refill"],
    [34, 48.0, "Food", "Dinner out"],
    [40, 200.0, "Bills", "Rent share top-up"],
  ];
  return samples.map(([daysAgo, amount, category, description], i) => ({
    id: `sample-${i}`,
    date: iso(daysAgo),
    amount,
    category,
    description,
    createdAt: new Date(now.getTime() - i * 1000).toISOString(),
  }));
}
