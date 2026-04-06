# Clarity Pulse

Clarity Pulse is a premium, enterprise-ready real-time initiative tracker. It's designed to replace messy spreadsheets with a high-end, extremely fast interface where leaders and employees can post status updates, blockages, and priority levels for their current projects.

## Architecture

- **Frontend**: React (Vite-powered for rapid development), custom strict vanilla CSS design system inspired by top tier enterprise products like Linear and Vercel (dark mode natively). 
- **Backend**: Python with Flask, providing robust secure endpoints.
- **Database**: Supabase (PostgreSQL), managed via the strictly-typed `supabase` Python API client.

## Key Features & Enterprise Approach

1. **Information Density & Speed**: 
   - Forms are quick to tab through, ensuring "Posting an update" has zero friction. Instead of a deep ticketing system, this acts as a "What's the status of X right now" pulse board.
   - Built explicitly avoiding overly complex abstractions like Redux; local state `useState` prevents deep re-renders making interaction instant.
2. **Design Elements**: 
   - Implemented a "Glass-panel" dark theme. Avoids harsh gradients in favor of subtle bordering, muted secondary texts (`#A1A1AA`), and stark contrast badges (`On Track`, `At Risk`, `Blocked`). Very easy on the eyes for all-day screen usage.
3. **Change Resilience**: 
   - Backend gracefully returns 500 error blocks instead of killing the Python Thread when the `SUPABASE_KEY` is missing, allowing the React frontend to intercept and warn the user. 
4. **Safe Interactions**: 
   - Dropdown selections natively cast statuses preventing improper strings from leaking into the database via Flask.

## Running Locally

1. **Supabase Database Setup**:
   - Go to Supabase, create a project.
   - Run the SQL contained in `backend/schema.sql` in your Supabase SQL Editor.
   - Rename `backend/.env.example` to `backend/.env` and paste your project URL and Anon Key.

2. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
