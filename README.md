# TaskFlow — AI-Powered Task Management

An AI-powered sprint task management tool for software teams. Built with Python/Flask, React, and SQLite — with an optional OpenAI integration that degrades gracefully to a local heuristic when no API key is set.

---

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optionally add your OPENAI_API_KEY
python run.py
```

The API starts at `http://127.0.0.1:5000`. The SQLite database (`taskflow.db`) is created automatically with seed data on first run.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173`.

### 3. Run Tests

```bash
cd backend
source venv_new/bin/activate
python -m pytest tests/ -v
```

37 tests · 0 failures

---

## Architecture

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM — single source of truth for DB schema
│   │   ├── schemas/         # Marshmallow — validation & serialisation gate
│   │   ├── services/        # Business logic — no Flask imports
│   │   └── routes/          # Thin HTTP handlers (validate → service → serialise)
│   ├── tests/               # pytest with in-memory SQLite
│   ├── config.py            # Environment-based configuration
│   └── run.py               # Minimal entry point
└── frontend/
    ├── src/
    │   ├── services/api.js  # Centralised HTTP client
    │   ├── hooks/           # Custom React hooks
    │   └── App.jsx          # Component tree
    └── index.css            # Design token system
```

---

## Key Technical Decisions

### 1. Strict Layer Separation

The backend enforces a 4-layer architecture with hard rules:

| Layer | Responsibility | Forbidden |
|-------|---------------|-----------|
| Routes | Validate input, return HTTP responses | Raw SQL, `db.session` calls |
| Services | Business logic, DB mutations | `flask`, `request`, `jsonify` |
| Models | ORM schema definition | Business logic |
| Schemas | Validation & serialisation | DB access |

**Why:** Each layer has a single reason to change. Adding a new resource (e.g. Comments) is a mechanical checklist — no architectural decisions needed.

### 2. SQLite as the Relational Database

SQLite was chosen over PostgreSQL/MySQL for zero-setup simplicity. The `DATABASE_URL` environment variable follows SQLAlchemy's URI format, so switching to PostgreSQL is a single env change requiring no code modification.

### 3. Marshmallow for Schema Validation

All request data passes through Marshmallow schemas before reaching services. Invalid `status` or `priority` enum values are rejected at the API boundary with a `400` response — they never reach the database layer.

### 4. AI Graceful Degradation

The AI service (`app/services/ai_service.py`) tries OpenAI first, then falls back to a deterministic heuristic algorithm. This means:
- The feature works out of the box with no API key.
- Results are cached on the `Task.ai_summary` column — no redundant API calls.
- AI failures are logged at `WARNING` level (not `ERROR`) to keep noise low.

### 5. Application Factory Pattern

`create_app()` in `app/__init__.py` creates isolated Flask instances per environment. Tests get their own in-memory SQLite DB — no shared state, no cleanup friction.

### 6. Centralised API Client (Frontend)

All `fetch` calls are in `src/services/api.js`. Components never call `fetch` directly. This means:
- Adding an auth token is a 3-line change in one file.
- Changing the base URL is a 1-line change.
- Easy to mock in component tests.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health + DB status |
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/:id` | Get project + stats |
| PATCH | `/api/projects/:id` | Update project |
| DELETE | `/api/projects/:id` | Delete project (cascades) |
| GET | `/api/tasks/project/:id` | List tasks for project |
| POST | `/api/tasks` | Create task |
| PATCH | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |
| POST | `/api/ai/summarise/:id` | Generate/return cached AI summary |
| POST | `/api/ai/prioritise/:id` | Suggest priority level |
| POST | `/api/ai/bulk-summarise/:id` | Summarise all tasks in project |

---

## Tradeoffs & Known Weaknesses

- **No authentication**: The API is open. A real deployment would need JWT or session auth.
- **SQLite for dev only**: SQLite has write-locking issues under high concurrency. The DATABASE_URL config makes upgrading trivial.
- **Heuristic AI is keyword-matching**: It works well for obvious cases (e.g. "production outage" → critical) but won't handle nuanced language.
- **No real-time updates**: Task boards don't auto-refresh when another user makes changes. Server-Sent Events or WebSocket could add this without architectural disruption.
- **Frontend has no tests**: Component/interaction tests (Vitest + Testing Library) would be the next step.

---

## AI Guidance Files

- `AGENTS.md` — Comprehensive constraints for AI coding agents: layer rules, forbidden patterns, testing requirements, and a checklist for adding new models.
- `claude.md` — Structural and aesthetic guidelines for AI agents working on this codebase.

---

## Author

Anupam Saha — [linktr.ee/anupamsaha]([https://linktr.ee/helloanupam])
