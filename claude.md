# NexusFi Coding Standards & AI Guidance Constraints

This document dictates rules and behavior constraints for any AI agents interacting with or generating code for the NexusFi repository.

## 1. Aesthetic Restrictions (Frontend)
- **CSS Strategy**: Avoid Tailwind or excessive CSS utility frameworks unless explicitly requested. Rely on pure semantic Vanilla CSS (`index.css` & `App.css`) for maximal customizability. 
- **Premium Identity**: Always generate layouts that utilize modern properties like `backdrop-filter: blur()`, clean transparent borders (`rgba(255, 255, 255, 0.1)`), and smooth gradient overlays to ensure an enterprise-grade / high-tech design feel. No generic blue or red color schemes.
- **Animations**: Include micro-interactions natively (e.g., hover scaling, subtle glow effects, and entry animations `keyframes` like `fade-in`).

## 2. Structural & Architectural Bounds
- **Language Stack**: Flask/Python (Backend) + React/Vite (Frontend). Never suggest alternate backend stacks blindly.
- **Simplicity**: Do not over-engineer. Avoid adding Redis, Docker configurations, or extensive task queues unless the feature inherently requires it.
- **State Integrity**: Limit state management to React `useState`/`useEffect`. Avoid recommending Redux, Zustand, or MobX for base-level CRUD tasks.

## 3. Communication & Code Modifications
- **Idempotent Operations**: When adding APIs, verify the endpoint doesn't overlap via `view_file` before writing logic. 
- **Error Handling**: Do not write endpoints that crash silently. Backend must always return dictionary structures `{ "error": "message" }` with appropriate status codes (`400`, `404`, `500`).
- **Safety First**: Treat database modifications cautiously. Always enclose `db.session.commit()` inside Try-Catch pipelines.
