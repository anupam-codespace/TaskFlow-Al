# NexusFi Tracker - Project Walkthrough

## 1. Architecture Overview
This application follows a classical decoupled **Client-Server Architecture**.
- **Frontend** acts as the client, built with React and Vite. It serves static assets and dynamically renders user interfaces by communicating with external APIs.
- **Backend** acts as the server, powered by Flask. It handles business logic, processing incoming RESTful requests (GET, POST, DELETE), and managing database interactions.
- **Database**: We use **Supabase** (PostgreSQL) hosted remotely. The backend uses the official `supabase` Python client to perform data mutations and retrievals. This offloads database management and provides scalable limits seamlessly.

## 2. File Structure Boundaries
Maintaining clear separation of concerns:
- **`/backend/`**: Contains the server logic (`app.py`, `requirements.txt`), Supabase DB setup (`schema.sql`), and environment secrets (`.env`).
- **`/frontend/`**: Contains the React ecosystem (`src/`, `App.jsx`, `index.css`).
- Communication exclusively happens across standard HTTP methods via `http://127.0.0.1:5000/api/expenses`, maintaining rigid system boundaries.

## 3. Technical Decisions & Interface Safety
- **Framework Choice**: React supports robust, predictable view rendering. Flask is highly explicit and lightweight out-of-the-box. Both avoid unnecessarily steep configurations.
- **Supabase Integration**: By using `supabase-py` instead of generic ORMs, the application directly integrates with cloud-first paradigms while keeping server payload formatting minimal. 
- **Interface Safety**: Inputs on the frontend `type="number"` with `min="0.01"` combined with backend validation (`if not data.get('title')...`) prevent invalid states implicitly (empty expenses or malformed queries). Float parsing and strict dictionary access guarantee type-safety on critical payloads before dispatching to Supabase.

## 4. Change Resilience & Verification
- State is compartmentalized cleanly within React. Changing how amounts are validated locally will not break rendering paths elsewhere. Backend endpoint modularity means adding a new `PUT` method won't disrupt existing `GET` mechanisms.
- Verification occurs via strict API response handling (`if response.ok`). Try-catch blocks ensure client-side exceptions do not crash the component silently.

## 5. Observability
- All errors are distinctly visible. Failed frontend fetches log strictly to `console.error()`.
- Failed backend executions return verbose `500 Internal Server Error` strings or `400 Bad Request` messages natively instead of crashing the Python process, allowing for fast API diagnosis via the browser's Network tab.

## 6. AI Usage & Guidance Setup
- **Code Structuring**: Boilerplate initialization was highly optimized utilizing AI agents to build standard REST blueprints and frontend scaffolding automatically.
- **Guidance & Safety**: The AI was provided with a constraints guidance file (`claude.md`) dictating layout instructions, visual specifications, routing rules, and constraints to ensure output reliability and enforce a premium aesthetic approach securely.
- **Risk Evaluation**: The main risk with AI generation is the hallucination of non-existent component logic or incorrect CSS properties. This was mitigated by having strict file boundary definitions and using vanilla CSS variables instead of untailored utility frameworks. All AI generated structures were reviewed prior to commit.
