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

5. Manual testing examples:
   - FetchSummaryNode:
     ```bash
     python3 - << 'PYCODE'
     from api.nodes.fetch_summary_node import FetchSummaryNode
     text = FetchSummaryNode("https://example.com")
     print(text[:200] + "…")
     PYCODE
    ```

6. Configure environment variables:
   - Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

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
