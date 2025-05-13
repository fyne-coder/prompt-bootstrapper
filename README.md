# Project

This repository contains:

- `/api`: FastAPI app & PocketFlow DAG
- `/web`: React UI
- `/tasks`: Codex task files
- `/tests`: pytest suites
- `/infra`: Render blueprints & migrations

## Getting Started

Prerequisites:
- Python 3.11
- Node.js 18
- pip and npm

1. Create & activate a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. (Optional) Install front-end dependencies:
   ```bash
   cd web
   npm ci
   cd ..
   ```

4. Run the test suite:
   ```bash
   pytest -q
   ```
  
5. End-to-end E2E tests (CI-only):
   These are configured via GitHub Actions in `.github/workflows/e2e.yml` and run automatically on push and PR.  

5. Manual testing examples:
   - FetchSummaryNode:
     ```bash
     python3 - << 'PYCODE'
     from api.nodes.fetch_summary_node import FetchSummaryNode
     text = FetchSummaryNode("https://example.com")
     print(text[:200] + "…")
     PYCODE
    ```

6. Configure environment variables (backend):
   - Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

7. Configure front-end environment (static site):
   - Define `VITE_API_BASE_URL` to point at your deployed API, e.g.
     ```bash
     VITE_API_BASE_URL=https://prompt-backend.onrender.com
     ```
   - In development, leave `VITE_API_BASE_URL` unset so the Vite proxy handles `/generate10/*` calls.
   - (Optional) For CI deploy via GitHub Actions, set the following repository secrets:
     - `RENDER_API_SERVICE_ID` — Render service ID for the FastAPI backend
     - `RENDER_WEB_SERVICE_ID` — Render service ID for the React static site
     - `RENDER_API_KEY` — Render API key with deploy permissions

7. Run the API server locally:
   ```bash
   uvicorn api.main:app --reload
   ```
   - SummariseNode:
     ```bash
     python3 - << 'PYCODE'
     from api.nodes.summarise_node import SummariseNode
     prompt = SummariseNode("Sample business description")
     print(prompt)
     PYCODE
     ```
- `/tests`: pytest suites
- `/infra`: Render blueprints & migrations
