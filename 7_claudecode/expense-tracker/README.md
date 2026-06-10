# 💸 Expensa — Personal Expense Tracker

A modern, professional expense tracking web app. Track spending, visualize
patterns, filter and search your history, and export to CSV.

- **Frontend:** Next.js 14 (App Router) · TypeScript · Tailwind CSS · Recharts
- **Backend:** Python · FastAPI (optional REST API)
- **Persistence:** `localStorage` in the browser (per the demo spec). The
  FastAPI backend provides an equivalent REST API + server-side CSV export.

The frontend is fully functional **on its own** — it stores data in
`localStorage`, so you can run and use the whole app without the backend. The
FastAPI service is included to satisfy the full-stack requirement and is ready
to wire in if you want shared, server-persisted data.

---

## ✨ Features

- **Add / edit / delete expenses** with date, amount, category & description
- **Form validation** — required fields, positive amounts, no future dates
- **Dashboard** — summary cards (total, this month, average, top category)
- **Charts** — category breakdown (donut) and monthly spending (bar)
- **Filter & search** — by text, category, and date range
- **Currency formatting** via `Intl.NumberFormat`
- **CSV export** — export all or just your filtered view
- **Responsive** — adaptive table/card layouts for desktop and mobile
- **Polished UX** — toasts, modals, loading skeletons, empty states
- **Sample data** — one-click seed to explore the app instantly

Categories: `Food`, `Transportation`, `Entertainment`, `Shopping`, `Bills`, `Other`.

---

## 🚀 Running the app

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ (only needed for the optional backend)

### 1. Frontend (required)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**.

Production build:

```bash
npm run build && npm run start
```

### 2. Backend (optional)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API root: **http://localhost:8000**
- Interactive docs (Swagger UI): **http://localhost:8000/docs**

Data is persisted to `backend/data/expenses.json` (created on first write).

#### API endpoints

| Method | Path                       | Description                       |
| ------ | -------------------------- | --------------------------------- |
| GET    | `/health`                  | Health check                      |
| GET    | `/api/expenses`            | List all expenses                 |
| POST   | `/api/expenses`            | Create an expense                 |
| GET    | `/api/expenses/{id}`       | Get one expense                   |
| PUT    | `/api/expenses/{id}`       | Update an expense                 |
| DELETE | `/api/expenses/{id}`       | Delete an expense                 |
| GET    | `/api/summary`             | Aggregated spending summary       |
| GET    | `/api/export.csv`          | Download all expenses as CSV      |

---

## 🧪 Testing all features (manual walkthrough)

1. **First run** → Dashboard shows a welcome screen. Click **Load sample data**
   to populate ~12 expenses, or **Add your first expense**.
2. **Add expense** → Click **Add expense**, try submitting empty / negative /
   future-dated values to see validation, then add a valid one. A toast confirms.
3. **Dashboard** → Verify the summary cards, the category donut, and the
   monthly bar chart update.
4. **Expenses page** → Use the navbar. Try the search box, category dropdown,
   and the From/To date range. The count + filtered total update live.
5. **Edit** → Hover a row (desktop) and click the pencil; change a value and save.
6. **Delete** → Click the trash icon; confirm in the dialog.
7. **Export CSV** → Click **Export CSV** on either page (the Expenses page
   exports your *filtered* view). A `.csv` file downloads.
8. **Persistence** → Refresh the page — your data is still there (localStorage).
9. **Responsive** → Narrow the window / open dev tools mobile view; the table
   becomes stacked cards and the navbar collapses to icons.

### Verifying the backend

With the backend running:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-06-01","amount":42.5,"category":"Food","description":"Groceries"}'
curl http://localhost:8000/api/summary
curl http://localhost:8000/api/export.csv
```

Or just explore everything interactively at http://localhost:8000/docs.

---

## 📁 Project structure

```
expense-tracker/
├── frontend/
│   ├── app/                # App Router pages (dashboard + expenses) & layout
│   ├── components/         # UI: Navbar, ExpenseForm, ExpenseList, charts, toasts…
│   ├── hooks/              # useExpenses, shared context, dialog flows
│   └── lib/                # types, formatting, storage, analytics, CSV
└── backend/
    ├── main.py             # FastAPI app & routes
    ├── models.py           # Pydantic models + validation
    ├── storage.py          # JSON-file persistence
    └── analytics.py        # summary aggregation + CSV
```

---

## 🛠️ Tech notes & decisions

- **Why localStorage as the source of truth?** The spec asked for localStorage
  persistence for the demo *and* a FastAPI backend. To keep the app usable with
  zero setup, the browser is the source of truth; the backend is a complete,
  independently-runnable parallel API. The frontend data layer
  (`lib/storage.ts`) is isolated, so swapping it to call the API is a small change.
- **No heavy state library** — React hooks + a single Context
  (`ExpensesProvider`) keep both pages in sync.
- **Charts** use Recharts; **icons** use lucide-react; the **date picker** is a
  native, validated `<input type="date">`.
