# TaskFlow — Walkthrough Script

**Format**: 10–15 minute walkthrough
**Audience**: Engineering assessment panel at Bettrsw

---

## 0. Opening (1 min)

> "I built TaskFlow — a sprint task management API designed for software teams. The brief asked for Python + Flask, React, and a relational database. The interesting constraint was to demonstrate engineering judgement, not just working code. So every decision I made was about: what makes this easy to extend without causing widespread change?"

Demo the running app briefly: sidebar with projects, task board, AI summarise button.

---

## 1. Architecture Walk (3 min)

### Show the folder structure

```
backend/
  app/
    models/    ← SQLAlchemy ORM — the schema lives here
    schemas/   ← Marshmallow — the validation gate
    services/  ← Business logic — no Flask imports allowed
    routes/    ← Thin HTTP handlers
  tests/       ← pytest, 37 tests, in-memory SQLite
```

> "Every layer has a single job. Routes validate and delegate. Services mutate data and know nothing about HTTP. Models own the schema. This means adding a new resource — say, Comments — is a mechanical checklist, not an architectural decision."

### Point out `AGENTS.md`

> "I also wrote AGENTS.md — a constraint file for AI coding agents. It explicitly forbids things like raw SQL in routes, print() statements, and Redux in the frontend. Any AI I pair-program with reads this first."

---

## 2. Structure: Layer Enforcement (2 min)

### Open `app/routes/projects.py`

> "Routes are intentionally thin. Three steps: validate the input with a Marshmallow schema, delegate to the service, serialise the result. No business logic lives here."

Show: `project_create_schema.load()` → `create_project(payload)` → `project_response_schema.dump(project)`

### Open `app/services/project_service.py`

> "Services own the DB mutation. Every commit is wrapped in try/except with a rollback — the database never ends up in a half-written state. The service has no Flask imports — it doesn't know it's running in an HTTP context."

### Open `app/schemas/project_schema.py`

> "Invalid data — wrong status value, missing name — gets rejected here, at the API boundary, before it touches the database. This is interface safety."

---

## 3. Correctness: Tests (2 min)

Run: `python -m pytest tests/ -v`

> "37 tests, 0 failures. Each resource has: happy path, validation rejection, and 404 behaviour. Tests use an in-memory SQLite database — each test gets a clean slate, there's no shared state."

Point out `test_create_project_rejects_invalid_status`:

> "This test confirms that the schema rejects bad enum values. The Marshmallow schema and the SQLAlchemy model both enforce the enum — two layers of defence."

---

## 4. AI Integration (2 min)

### Show `app/services/ai_service.py`

> "The AI feature follows graceful degradation. First, it tries OpenAI GPT-4o-mini. If there's no API key, quota error, or timeout — anything — it falls back to a deterministic keyword-scoring algorithm. The feature always works."

Show: `_try_openai_summary` → falls back to `_heuristic_summary`

> "Results are cached on the `Task.ai_summary` column. If you hit 'Summarise' twice, the second call returns instantly without hitting the API. AI failures are logged at WARNING, not ERROR — they're expected degradation, not bugs."

### Demo in the frontend

Click "AI Summarise" on a task → summary appears.
Click "Suggest Priority" → shows suggestion vs current, lets user apply.

---

## 5. Observability (1 min)

### Show `GET /api/health`

> "The health endpoint checks DB connectivity and returns a structured JSON response. It never throws — even if the DB is down, it returns 503 with a clear message. Deployment platforms and monitoring tools can poll this."

Show structured log output:

> "Logs use a timestamp + level + module format. AI fallbacks log at WARNING so they're visible but don't pollute the error stream. All errors include enough context to identify the failing resource."

---

## 6. Change Resilience (1 min)

> "The architecture is designed so that new features don't cause widespread impact. Adding authentication is a new middleware — no route handlers change. Switching from SQLite to PostgreSQL is changing one environment variable. Adding a Comment model is a 7-step checklist — the AGENTS.md file documents it."

> "The frontend centralises all API calls in `src/services/api.js`. If we add auth headers or switch to a different base URL, it's one file, three lines."

---

## 7. Known Weaknesses (1 min)

> "I want to be transparent about the tradeoffs:
> 1. **No auth** — the API is open. JWT middleware would be the next addition.
> 2. **SQLite under concurrency** — fine for a demo, for production you'd point DATABASE_URL at PostgreSQL.
> 3. **Heuristic AI is keyword-matching** — it handles obvious priority signals well but won't understand nuanced context. Real usage benefits from the OpenAI key.
> 4. **No frontend tests** — Vitest + Testing Library would cover component behaviour.
> 5. **No real-time** — task updates don't push to other clients. SSE or WebSocket could add this without architectural disruption."

---

## 8. Extension Approach (1 min)

> "If I were to extend this for a real team:
> - **Auth**: Add a `User` model and JWT middleware — routes stay unchanged.
> - **Comments**: Follow the 7-step checklist in AGENTS.md.
> - **Sprint planning**: Add a `Sprint` model with a many-to-many to `Task` — the service layer owns the association logic.
> - **Notifications**: An event bus (could be simple Python `threading.Event`) that services publish to — decoupled from the HTTP layer."

---

## Closing (30s)

> "The goal wasn't to build the most feature-rich task manager. It was to demonstrate that every line of code has a reason, every decision has a tradeoff, and the system can be extended by someone who has never seen it before — including an AI agent."
