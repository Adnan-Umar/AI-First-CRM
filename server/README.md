# AI-First CRM Server (Phase 1)

Production-ready FastAPI foundation with:

- FastAPI routing and lifecycle setup
- SQLAlchemy ORM with PostgreSQL driver (`psycopg`)
- Pydantic v2 schemas and settings-based environment config
- Alembic migration scaffolding and initial schema
- CRUD APIs for `users`, `organizations`, and `healthcare_professionals`

## Folder structure

```text
server/
├─ app/
│  ├─ api/
│  │  └─ v1/endpoints/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ repositories/
│  ├─ schemas/
│  ├─ services/
│  └─ main.py
├─ alembic/
│  └─ versions/
├─ alembic.ini
├─ requirements.txt
└─ .env.example
```

## Environment

1. Copy `.env.example` to `.env`
2. Update `DATABASE_URL` to your PostgreSQL instance

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API base URL

`/api/v1`

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/ai/chat/messages`
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/{id}`
- `PATCH /api/v1/users/{id}`
- `DELETE /api/v1/users/{id}`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations`
- `GET /api/v1/organizations/{id}`
- `PATCH /api/v1/organizations/{id}`
- `DELETE /api/v1/organizations/{id}`
- `POST /api/v1/hcps`
- `GET /api/v1/hcps`
- `GET /api/v1/hcps/{id}`
- `PATCH /api/v1/hcps/{id}`
- `DELETE /api/v1/hcps/{id}`
