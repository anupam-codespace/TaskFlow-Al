# Clarity Pulse - Project Walkthrough

## 1. Product Pivot & Architecture
We successfully pivoted from an Expense Tracker into **Clarity Pulse**, a sophisticated enterprise status board. This application fits the real-world corporate environment much better by creating a seamless feed connecting teammates with live project blocker information. 
- **Frontend** built with React using a bespoke, premium dark-mode aesthetic. 
- **Backend** acts as the server, powered by Flask. 
- **Database**: We use **Supabase** (PostgreSQL) hosted remotely. 

## 2. File Structure Boundaries
Maintaining clear separation of concerns:
- **`/backend/`**: Contains the server logic (`app.py`, `requirements.txt`), Supabase DB setup (`schema.sql`), and environment secrets (`.env`).
- **`/frontend/`**: Contains the React ecosystem (`src/`, `App.jsx`, `index.css`).
- Communication exclusively happens across standard HTTP methods via `http://127.0.0.1:5000/api/initiatives`.

## 3. Technical Decisions & Interface Safety
- **High-End UI**: Abandoned standard bright colors to invoke a focus-heavy "dark mode office" feel. Employs crisp 1px borders via `rgba` to separate information hierarchy (similar to Linear). 
- **Graceful Error Handling**: Supabase initialization issues do not kill the server. The python script actively catches initialization faults during `require_db()` meaning the API stays alive simply to inform the Frontend UI it is disconnected. The Frontend UI intercepts that string and cleanly produces a red warning box over the feed without crashing.

## 4. Change Resilience & Verification
- State is compartmentalized cleanly within React. Changing how priorities render won't break Form submitting paths elsewhere.
- Verification occurs via strict API response handling (`if response.ok`). Try-catch blocks ensure client-side exceptions do not crash the component silently. Backend validation guarantees fields like "status" are populated before they touch Postgres.

## 5. Observability
- All errors are distinctly visible. Failed frontend fetches log strictly to `console.error()`.
- Failed backend executions return verbose `500 Internal Server Error` strings or `400 Bad Request` messages natively instead of crashing the Python process, allowing for fast API diagnosis via the browser's Network tab.
