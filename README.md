# NexusFi Tracker

NexusFi Tracker is a premium, minimalistic full-stack expense management web application. It combines a visually striking frontend layout featuring glassmorphism elements with a robust, simple REST API backend.

## Architecture

- **Frontend**: React (Vite-powered for rapid development), Vanilla CSS for custom, aesthetic-heavy utility components. 
- **Backend**: Python with Flask, providing RESTful endpoints.
- **Database**: SQLite, managed via Flask-SQLAlchemy.

## Technical Decisions

1. **Simplicity Over Complexity**: 
   - Uses SQLite to eliminate explicit database hosting/setup dependencies for quick local spins up.
   - Eschews heavy state-management libraries (like Redux) in the frontend for native React `useState` and `useEffect`, keeping bundle size low and code highly readable.
2. **Design Philosophy**: 
   - Vanilla CSS was intentionally chosen over heavy CSS frameworks to exercise strict control over layout, micro-animations, and custom gradient overlays aligning with a modern "Futuristic Finance Dashboard" requirement.
3. **Correctness & Resilience**: 
   - Backend enforces schema validation securely via SQLAlchemy constraints.
   - Empty state fallbacks in the frontend prevent unpredictable render states.
4. **CORS Configuration**: Flask-CORS is enabled out of the gate to handle resource sharing effortlessly, reflecting standard decoupled API-Client architecture logic.

## AI Usage

This project heavily leverages AI assistance for:
- Bolstering boilerplate scaffolding.
- Structuring aesthetic "Wow-factor" frontend styles (e.g., animations and custom backdrop-filters).
- Ensuring prompt resolution of any configuration blockers rapidly via an active agentic approach.

See `claude.md` and `Walkthrough.md` for extended details.

## Running Locally

1. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
