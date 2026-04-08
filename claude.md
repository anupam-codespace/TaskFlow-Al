# claude.md — AI Agent Constraints for TaskFlow

This document defines rules and constraints for any AI coding assistant (Claude, Copilot, Cursor, etc.) working on this repository.

---

## 1. Identity

This project is **TaskFlow** — a task management API for software teams.
- Backend: Flask 3.x, SQLAlchemy, SQLite, Marshmallow, Python 3.9+
- Frontend: React 18, Vite, Vanilla CSS (no Tailwind)
- AI: OpenAI GPT-4o-mini with heuristic fallback

Do NOT rename, rebrand, or restructure the project without explicit instruction.

---

## 2. Layer Rules (Backend) — STRICT

```
Route handler → Schema (validate) → Service (mutate) → Model (ORM)
```

- **Routes** (`app/routes/`): Validate input, delegate to service, return response. No direct `db.session` access.
- **Services** (`app/services/`): Business logic only. No `flask` imports. No `request`/`jsonify`.
- **Models** (`app/models/`): ORM definitions only. No business logic.
- **Schemas** (`app/schemas/`): Marshmallow schemas for validation and serialisation only.

Violating these boundaries makes the codebase unpredictable and harder to test.

---

## 3. Forbidden Actions

- ❌ `print()` for logging → use `logger = logging.getLogger(__name__)` or `current_app.logger`
- ❌ Raw SQL strings → SQLAlchemy ORM queries only
- ❌ `db.session.commit()` outside a try/except with `db.session.rollback()` in the except block
- ❌ Secrets or `.env` files committed to git
- ❌ `fetch()` calls directly in React components → use `src/services/api.js`
- ❌ `useState`/`useEffect` bypass → no Redux, Zustand, MobX
- ❌ Inline CSS for tokens already defined in `src/index.css`
- ❌ Breaking existing tests without adding replacement coverage

---

## 4. Error Handling

Every route handler must catch all exceptions and return:

```python
return jsonify({"error": "descriptive message"}), <status_code>
```

Use correct HTTP status codes:
- `400` — validation failure (Marshmallow error)
- `404` — resource not found
- `409` — conflict (e.g., duplicate name)
- `500` — unexpected server error

---

## 5. AI Feature Rules

The AI service uses graceful degradation (OpenAI → heuristic). When extending:

1. **Never make AI a hard dependency.** The heuristic must always provide a useful answer.
2. **Cache on the model.** Use `task.ai_summary` to avoid redundant API calls.
3. **Log AI failures at WARNING**, not ERROR. They are expected degradation.
4. **Test without real API calls.** Tests must use `TestingConfig` with no `OPENAI_API_KEY`.

---

## 6. CSS / Frontend

- Design tokens are in `src/index.css`. Use `var(--token-name)` — do not hardcode colours or spacing.
- All component styles go in `src/App.css`. No external CSS frameworks.
- Use semantic class names (`.task-card`, `.btn-primary`) not utility classes.
- All form inputs must have `id` attributes for testability.

---

## 7. Testing Contract

Before submitting any change:

```bash
cd backend && python -m pytest tests/ -v
```

All 37 tests must pass. New functionality requires new tests covering:
- Happy path (201/200 response)
- Validation rejection (400)
- Not-found handling (404)
