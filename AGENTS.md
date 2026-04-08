# AGENTS.md — AI Agent Guidance for TaskFlow

This file constrains how AI coding agents (Copilot, Claude, Cursor, etc.)
should behave when working on this repository. Read this before generating
or modifying any code.

---

## 1. Project Identity

**TaskFlow** is an AI-powered task management API built with:
- **Backend**: Python 3.9+ / Flask 3.x / SQLAlchemy / SQLite
- **Frontend**: React 18 / Vite / vanilla CSS
- **AI**: OpenAI GPT-4o-mini with deterministic heuristic fallback

The target audience is software teams managing sprint tasks.

---

## 2. Architectural Rules

### 2.1 Backend Layer Separation (STRICT — do not violate)
```
Routes   → validate request (Marshmallow schema)
Services → execute business logic + DB mutations
Models   → SQLAlchemy ORM definitions
Schemas  → Marshmallow validation/serialisation
```
- Routes MUST NOT contain raw SQL or direct `db.session` calls.
- Services MUST NOT import from `flask` (no `request`, `jsonify`).
- All DB mutations MUST be wrapped in try/except with `db.session.rollback()`.

### 2.2 Always Use Existing Patterns
- Adding a new resource: follow the Project model/schema/service/route pattern exactly.
- Adding a new endpoint: register it in the correct Blueprint, not directly in `run.py`.
- Adding configuration: add to `config.py`, not as hard-coded strings in routes.

### 2.3 Error Handling
- Every route handler MUST return `{"error": "message"}` on failure.
- Never let unhandled exceptions reach the user — always wrap in try/except.
- Log errors with `current_app.logger.error(...)`, not `print()`.
- Use correct HTTP codes: 400 (validation), 404 (missing), 409 (conflict), 500 (unexpected).

---

## 3. What You Must NOT Do

- ❌ Do NOT add Redis, Celery, or Docker unless explicitly requested.
- ❌ Do NOT use `print()` for logging — use `current_app.logger` or `logging`.
- ❌ Do NOT introduce new state management libraries (Redux, Zustand) in the frontend.
- ❌ Do NOT add raw SQL strings — use SQLAlchemy ORM queries only.
- ❌ Do NOT commit secrets, API keys, or `.env` files.
- ❌ Do NOT bypass schema validation in route handlers.
- ❌ Do NOT break existing tests — run pytest before submitting.
- ❌ Do NOT use `SELECT *` style ORM queries where specific fields suffice.

---

## 4. Frontend Rules

### 4.1 CSS Strategy
- Use vanilla CSS with the design token system defined in `src/index.css`.
- Do NOT add inline styles for spacing/colour that already have a token.
- Do NOT add Tailwind — the project uses CSS custom properties.

### 4.2 State Management
- Use React `useState` and `useEffect` only.
- All API interactions go through `src/services/api.js` — never write `fetch` calls in components.

### 4.3 Component Patterns
- Forms must have `id` attributes on all inputs for testability.
- Error states must be visible to the user (not just `console.error`).
- Destructive actions (delete) must be clearly labelled.

---

## 5. Testing Requirements

- All new backend functionality MUST have corresponding pytest tests.
- Tests MUST use the `client` fixture from `conftest.py` (in-memory DB).
- Tests MUST NOT make real network requests (no live DB, no real OpenAI calls).
- Aim for: happy path + validation rejection + 404 behaviour per resource.

---

## 6. AI Integration Guidelines

The AI feature (`app/services/ai_service.py`) follows a graceful degradation pattern:
1. Try OpenAI API.
2. On any failure (no key, quota, timeout), fall back to deterministic heuristic.

When extending AI features:
- NEVER make the feature non-functional without an API key.
- Cache results on the model (`ai_summary` column) to avoid redundant API calls.
- Log all AI failures at `WARNING` level, not `ERROR`.

---

## 7. Adding a New Model (Checklist)

When adding a new database model (e.g. `Comment`):
- [ ] Create `app/models/comment.py` following the `Task` model pattern.
- [ ] Add to `app/models/__init__.py`.
- [ ] Create `app/schemas/comment_schema.py` with Create/Update/Response schemas.
- [ ] Create `app/services/comment_service.py` with full error handling.
- [ ] Create `app/routes/comment.py` Blueprint with proper status codes.
- [ ] Register Blueprint in `app/__init__.py`.
- [ ] Write tests in `tests/test_comments.py`.
