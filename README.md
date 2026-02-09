# Kapusta Web

Web version of the report app built with FastAPI + Jinja2 + HTMX + Tabler + DataTables.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

Open: `http://127.0.0.1:8000`

## Deploy on Render

### Option 1: Blueprint (recommended)

This repo already contains `render.yaml`.

1. Push this folder as a separate Git repository.
2. In Render: `New +` -> `Blueprint`.
3. Select your repository.
4. Render will create service `kapusta-web` using:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Manual Web Service

1. In Render create `Web Service` from this repo.
2. Runtime: `Python`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Notes

- SQL is loaded from `myRequest.sql` in repo root.
- App config is stored in `kapusta_report_settings.json` (ephemeral on Render).
- API data fetch supports multi-page loading until empty page.
