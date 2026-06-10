"use client";

import { ToastProvider } from "./Toast";
import { ExpensesProvider } from "@/hooks/ExpensesContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ToastProvider>
      <ExpensesProvider>{children}</ExpensesProvider>
    </ToastProvider>
  );
}
