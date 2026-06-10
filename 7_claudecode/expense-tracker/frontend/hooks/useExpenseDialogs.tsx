"use client";

import { useCallback, useState } from "react";
import type { Expense, ExpenseInput } from "@/lib/types";
import { Modal } from "@/components/Modal";
import { ExpenseForm } from "@/components/ExpenseForm";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { useExpensesContext } from "./ExpensesContext";
import { useToast } from "@/components/Toast";
import { formatCurrency } from "@/lib/format";

/**
 * Centralizes the add / edit / delete dialog flows so any page can trigger
 * them and render a single shared set of dialogs.
 */
export function useExpenseDialogs() {
  const { addExpense, updateExpense, deleteExpense } = useExpensesContext();
  const { notify } = useToast();

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Expense | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Expense | null>(null);

  const openAdd = useCallback(() => {
    setEditing(null);
    setFormOpen(true);
  }, []);

  const startEdit = useCallback((expense: Expense) => {
    setEditing(expense);
    setFormOpen(true);
  }, []);

  const requestDelete = useCallback((expense: Expense) => {
    setPendingDelete(expense);
  }, []);

  const closeForm = useCallback(() => {
    setFormOpen(false);
    setEditing(null);
  }, []);

  const handleSubmit = useCallback(
    (input: ExpenseInput) => {
      if (editing) {
        updateExpense(editing.id, input);
        notify("Expense updated.", "success");
      } else {
        addExpense(input);
        notify("Expense added.", "success");
      }
      closeForm();
    },
    [editing, addExpense, updateExpense, notify, closeForm]
  );

  const confirmDelete = useCallback(() => {
    if (pendingDelete) {
      deleteExpense(pendingDelete.id);
      notify("Expense deleted.", "info");
      setPendingDelete(null);
    }
  }, [pendingDelete, deleteExpense, notify]);

  const dialogs = (
    <>
      <Modal
        open={formOpen}
        title={editing ? "Edit expense" : "Add expense"}
        onClose={closeForm}
      >
        <ExpenseForm
          initial={editing ?? undefined}
          onSubmit={handleSubmit}
          onCancel={closeForm}
        />
      </Modal>

      <ConfirmDialog
        open={!!pendingDelete}
        title="Delete expense?"
        message={
          pendingDelete
            ? `"${pendingDelete.description}" (${formatCurrency(
                pendingDelete.amount
              )}) will be permanently removed.`
            : ""
        }
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </>
  );

  return { openAdd, startEdit, requestDelete, dialogs };
}
