"use client";

import { createContext, useContext } from "react";
import { useExpenses, type UseExpensesResult } from "./useExpenses";

const ExpensesContext = createContext<UseExpensesResult | null>(null);

export function ExpensesProvider({ children }: { children: React.ReactNode }) {
  const value = useExpenses();
  return (
    <ExpensesContext.Provider value={value}>
      {children}
    </ExpensesContext.Provider>
  );
}

export function useExpensesContext(): UseExpensesResult {
  const ctx = useContext(ExpensesContext);
  if (!ctx) {
    throw new Error("useExpensesContext must be used within ExpensesProvider");
  }
  return ctx;
}
