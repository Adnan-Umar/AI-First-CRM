# RUN.md — How to run the AI-First CRM

This guide covers everything needed to install, configure, and run the
AI-First CRM (FastAPI backend + React/Vite frontend + PostgreSQL + LangGraph agent).

---

## Prerequisites

| Tool | Required version | Notes |
|------|------------------|-------|
| Python | **3.13.x** | A virtual environment is used in `server/.venv` |
| Node.js | **24.x** | Comes with npm 11.x |
| PostgreSQL | **18.x** | Must be running and reachable on `localhost:5432` |
| Groq API key | — | Optional. Without it the agent runs in **demo mode** (keyword routing, no LLM extraction) |

Verify locally:

```powershell
python --version      # 3.13.x (use the server/.venv interpreter)
node --version        # v24.x
npm --version         # 11.x
psql --version        # PostgreSQL 18.x
```

---

## Installation

Clone the repository and install both backends:

```powershell
git clone <repo-url>
cd ai-first-crm
```

### Backend setup

```powershell
cd server

# Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies (pinned in requirements.txt)
pip install -r requirements.txt
```

> All commands below that use `python` assume the venv is activated. If not
> activated, call `.\.venv\Scripts\python.exe` instead of `python`.

### Frontend setup

```powershell
cd client
npm install
```

---

## Database setup

1. Make sure PostgreSQL is running:

   ```powershell
   Get-Service postgresql-x64-18
   # Status should be "Running". Start it if needed:
   Start-Service postgresql-x64-18
   ```

2. Create the database (run from a `psql` / SQL shell as a superuser):

   ```sql
   CREATE DATABASE ai_first_crm;
   ```

3. Configure the connection in `server/.env` (see **Environment variables**).
   The default uses the local `postgres` superuser with no password — adjust
   `DATABASE_URL` to match your PostgreSQL username/password.

4. (Optional) Seed demo data — 3 organizations, 3 doctors, 1 sales rep user,
   and 1 sample interaction:

   ```powershell
   cd server
   python -m app.db.seed
   ```

---

## Alembic migration

Migrations live in `server/alembic/versions/`. Run them from the `server`
directory (the venv must be active so `alembic` is on the path):

```powershell
cd server
python -m alembic upgrade head
```

- Check current revision: `python -m alembic current`
- Check target head: `python -m alembic heads`
- Roll back one step: `python -m alembic downgrade -1`

The schema is **not** auto-created at startup (`DB_AUTO_CREATE=false`); always
use Alembic.

---

## Groq API key setup

The LangGraph agent uses Groq (`langchain-groq`) with the model
`llama-3.3-70b-versatile`.

1. Get a key from <https://console.groq.com/keys>.
2. Add it to `server/.env`:

   ```dotenv
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. Restart the backend after changing `.env`.

If `GROQ_API_KEY` is empty, the server still runs but the agent falls back to
**demo mode** (intent is chosen by keyword heuristics and no LLM field
extraction happens). The chat endpoint still returns HTTP 200.

---

## Environment variables

### `server/.env` (gitignored — do not commit secrets)

```dotenv
APP_NAME=AI-First CRM API
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
API_V1_PREFIX=/api/v1

# PostgreSQL. Adjust user/password to your install.
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/ai_first_crm
DB_AUTO_CREATE=false

# Groq API key (optional — enables full AI routing)
GROQ_API_KEY=

# Allowed CORS origins (frontend dev servers)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
```

A documented template is in `server/.env.example`.

### `client/.env` (optional)

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

If omitted, the frontend defaults to `http://localhost:8000/api/v1`.

---

## How to start the backend

From the `server` directory with the venv active:

```powershell
cd server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000/api/v1`
- Interactive docs (Swagger UI): <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Health check:

```powershell
curl http://localhost:8000/api/v1/health
# -> {"status":"ok", ...}
```

---

## How to start the frontend

From the `client` directory:

```powershell
cd client
npm run dev
```

The app is served at <http://localhost:5173>. It calls the backend at
`http://localhost:8000/api/v1` (CORS is pre-configured for `localhost:5173`).

Other scripts:

```powershell
npm run build   # type-check (tsc -b) + production build into dist/
npm run lint    # oxlint
npm run preview # preview the production build
```

---

## How to test the LangGraph agent

The agent is exposed at:

```
POST /api/v1/ai/chat/messages
```

Request body:

```json
{
  "message": "Log a call with Dr. Sarah Khan about Aspirin, plan follow-up next month",
  "doctor_id": "hcp-001",
  "visit_type": "Call",
  "interaction_date": "2026-07-10",
  "products_discussed": ["Aspirin"],
  "notes": "Discussed new trial",
  "follow_up_date": "2026-08-10"
}
```

Example (PowerShell):

```powershell
curl.exe -X POST http://localhost:8000/api/v1/ai/chat/messages `
  -H "Content-Type: application/json" `
  -d '{"message":"Log a call with Dr. Sarah Khan about Aspirin","doctor_id":"hcp-001"}'
```

Response (when `GROQ_API_KEY` is set):

```json
{
  "reply": "Logged call with Dr. Sarah Khan about Aspirin, follow-up planned for next month",
  "extracted_fields": {
    "doctorId": "hcp-001",
    "visitType": "Call",
    "date": "2026-07-11",
    "productsDiscussed": "Aspirin",
    "notes": "Discussed new trial",
    "followUpDate": "2026-08-11",
    "intent": "log_interaction",
    "intentLabel": "Log Interaction"
  },
  "intent": "log_interaction"
}
```

You can also test it from the Swagger UI at `/docs` → `POST /ai/chat/messages`.

---

## How to test all five tools

The agent routes each message to one of five LangGraph tool nodes. Trigger each
with a representative message (make sure `GROQ_API_KEY` is set for real LLM
behavior; otherwise the agent uses demo-mode heuristics):

| Tool | Example message | What it does |
|------|-----------------|--------------|
| `log_interaction` | "Log a call with Dr. Sarah Khan about Aspirin, follow-up next month" | Extracts structured visit fields |
| `edit_interaction` | "Update my last visit with Dr. Sarah to change the outcome to Closed" | Finds & updates an interaction |
| `search_history` | "Show me past visits with Dr. Sarah" | Searches interactions by filter |
| `follow_up_plan` | "Create a follow-up plan for Dr. Sarah" | Generates a coaching plan via LLM |
| `summarize_interaction` | "Summarize my last interaction with Dr. Ali" | Summarizes an interaction via LLM |

Quick loop (PowerShell):

```powershell
$msgs = @(
  'Log a call with Dr. Sarah Khan about Aspirin, follow-up next month',
  'Update my last visit with Dr. Sarah to change the outcome to Closed',
  'Show me past visits with Dr. Sarah',
  'Create a follow-up plan for Dr. Sarah',
  'Summarize my last interaction with Dr. Ali'
)
foreach ($m in $msgs) {
  Write-Host "`n=== $m ==="
  curl.exe -s -X POST http://localhost:8000/api/v1/ai/chat/messages `
    -H "Content-Type: application/json" `
    -d "{`"message`":`"$m`",`"doctor_id`":`"hcp-001`"}" `
    | python -m json.tool
}
```

Each response's `intent` field should match the tool name above.

---

## Common errors and fixes

**1. `Error code: 400` from Groq on every AI call**
- Cause: deprecated default model. Fixed — `server/app/agents/llm.py` now uses
  `llama-3.3-70b-versatile`. If you still see it, set `DEFAULT_MODEL` in
  `llm.py` to any currently available Groq model (`llama-3.1-8b-instant`, etc.)
  and restart the backend.

**2. CORS error in the browser console (`blocked by CORS policy`)**
- Cause: frontend opened via `127.0.0.1` but only `localhost` was allowed.
- Fix: `CORS_ORIGINS` in `server/.env` now includes `127.0.0.1:5173` and
  `127.0.0.1:3000`. Restart the backend after editing `.env`.

**3. `connection refused` / `could not connect to server` on startup**
- PostgreSQL is not running, or `DATABASE_URL` credentials are wrong, or the
  `ai_first_crm` database does not exist. Start the service, fix the URL, and
  run `createdb ai_first_crm`.

**4. `missing "=" after "postgresql+psycopg://..."` when calling `psycopg.connect`**
- The raw `psycopg` driver does not understand the `postgresql+psycopg://`
  dialect prefix — that prefix is for **SQLAlchemy** only. Always connect
  through `app.db.session.engine`, not `psycopg.connect`.

**5. Agent stays in demo mode / `I'm running in demo mode...`**
- `GROQ_API_KEY` is empty in `server/.env`. Add a valid key and restart.

**6. `alembic` command not found**
- The venv is not activated. Activate it (`..\venv\Scripts\Activate.ps1`) or run
  `.\.venv\Scripts\python.exe -m alembic ...`.

**7. `Target database is not up to date` / migration conflicts**
- Run `python -m alembic upgrade head` from the `server` directory. The
  migration chain is linear: `20260711_01` → `92c6f0f8d999` → `64314a26bad7`.

**8. Port already in use (8000 or 5173)**
- Stop the other process, or change `APP_PORT` in `server/.env` (backend) /
  pass `--port` to `npm run dev` (frontend). If you change the backend port,
  update `VITE_API_BASE_URL` accordingly.

**9. Frontend builds but API calls fail silently**
- Confirm the backend is running on `:8000` and that `VITE_API_BASE_URL`
  (or its default) points there. Check the Network tab for the exact request.
