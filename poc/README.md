# AI Personal Stylist & Virtual Try-On (POC)

Proof of concept for an AI-powered personal stylist platform with product scraping, multi-agent recommendations, virtual try-on, and chat.

## Project Structure

```
poc/
├── backend/           # FastAPI app, agents, services
├── frontend/          # React + Vite + Tailwind UI
├── images/
│   ├── uploads/       # User body images
│   └── generated/     # Try-on outputs
├── database.sqlite    # Created on first run
├── requirements.txt
└── .env.example
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Optional: `OPENAI_API_KEY` for LLM-powered agents (fallback logic works without it)
- Optional: Playwright browsers for JS-heavy product pages

## Setup

### 1. Backend

```bash
cd poc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
SECRET_KEY=your-secret-key
TRYON_PROVIDER=mock
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...   # optional but recommended
```

Install Playwright browser (optional, for Nike/Zara/etc.):

```bash
playwright install chromium
```

Run API:

```bash
cd poc
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd poc/frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create user profile |
| POST | `/login` | Login and receive JWT |
| GET | `/profile` | Get profile dashboard data |
| PUT | `/profile` | Update profile |
| POST | `/upload-images` | Upload front/side/back images |
| POST | `/analyze-product` | Scrape + run agent workflow |
| POST | `/recommend-size` | Size recommendation |
| POST | `/generate-tryon` | Virtual try-on image |
| POST | `/chat` | Stylist conversation |
| GET | `/history` | Chat history |

## Agents (LangGraph)

Workflow order:

1. Product Knowledge Agent
2. Customer Profile Agent
3. Review Intelligence Agent
4. Size Recommendation Agent

Conversation and Virtual Try-On agents are invoked separately via API.

## Virtual Try-On Providers

Configure in `.env`:

```env
TRYON_PROVIDER=mock        # default, works offline
TRYON_PROVIDER=idm-vton    # requires IDM_VTON_API_URL
```

Architecture uses a `VirtualTryOnProvider` interface so providers can be swapped for Google TryOn, OpenAI Images, or FASHN AI later.

## Local Workflow

1. Register and log in
2. Complete profile measurements and preferences
3. Upload front (and optional side/back) images
4. Paste a product URL and analyze
5. Request size recommendation and try-on preview
6. Ask follow-up questions in chat

## Notes

- Scraping behavior varies by retailer; some sites block bots or require Playwright.
- Without `OPENAI_API_KEY`, agents use deterministic fallback responses so the full flow still works.
- Storage is local filesystem + SQLite by design for easy migration to S3/PostgreSQL later.
