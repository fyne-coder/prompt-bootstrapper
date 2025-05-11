#
#   This file is read by OpenAI Codex CLI on every command.
#   KEEP IT SHORT and bullet-proof; never describe tasks here.
#   Task-specific specs live in the /tasks directory.
#
#─────────────────────────────────────────────────────────────────
## 1 ▍Stack Snapshot  (implementation-specific)
| Layer        | Preferred Tool |
|--------------|----------------|
| Task DAG     | **PocketFlow ≥ 0.4** :contentReference[oaicite:4]{index=4} |
| API Layer    | FastAPI |
| Front-end    | React + Vite + Tailwind (with `fyne-core.css`) |
| Async Jobs   | Redis / RQ |
| PDF Engine   | WeasyPrint |
| Storage      | Postgres (jobs), S3 (PDF/HTML) |
| Hosting      | Render.com (keep combined cost ≤ $100 /mo) |

## 2 ▍Repo Layout
```text
/api/    ← FastAPI app & PocketFlow DAG
/web/    ← React UI
/tasks/  ← Codex task files
/tests/  ← pytest
/infra/  ← Render blueprints & migrations
