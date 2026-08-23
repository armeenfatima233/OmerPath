# OmerPath

An AI-guided scholarship discovery and application workspace: a React frontend, a FastAPI backend, Postgres (via Supabase) for data and Supabase Auth for authentication, and a Groq-backed AI Advisor grounded in each student's real profile, scholarships, matches, applications, and documents.

## Architecture

```
client/   React + TypeScript + Vite frontend (deployed as app.<domain> in production)
backend/  FastAPI + SQLAlchemy + Alembic backend (deployed as api.<domain> in production)
```

The frontend never talks to Supabase or Groq directly - every request goes through the FastAPI backend, which holds all secrets server-side and authenticates every request via an HttpOnly session cookie.

## Backend setup

Requirements: Python 3.12+, a Supabase project (Postgres + Auth), a Groq API key.

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # then fill in real values - see .env.example for what each one does
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` by default. See `backend/.env.example` for every required/optional environment variable and what it controls (database, Supabase keys, `GROQ_API_KEY`, cookie/CORS behavior).

### Running backend tests

```bash
cd backend
pytest
```

This is an integration-style suite (see `backend/tests/conftest.py`): it runs the real FastAPI app in-process against whatever Supabase project + Postgres database `backend/.env` points to, creating and deleting throwaway `pytest-*@example.com` accounts via the Supabase admin API. **Never point `backend/.env` at a production database or Supabase project while running tests.** The AI Advisor's LLM call is mocked in every test except one, which only runs when `GROQ_API_KEY` is set (`pytest -m live_llm` to select it explicitly, or it runs automatically as part of the full suite whenever the key is present).

## Frontend setup

Requirements: Node.js 20+ and npm.

```bash
npm install
cp client/.env.example client/.env.local   # then set VITE_API_BASE_URL to the backend's URL
npm run dev
```

Open the URL shown by Vite, normally `http://localhost:3000`.

```bash
npm run check   # TypeScript type-check
npm run build   # production bundle
npm run preview
```

## Main routes

- `/` — public landing page
- `/signup`, `/login` — authentication
- `/onboarding` — profile + academic profile setup
- `/dashboard` — workspace overview
- `/dashboard/scholarships` — real scholarship search/filter, with computed match/eligibility
- `/dashboard/scholarships/:id` — scholarship detail, eligibility breakdown, application entry point
- `/dashboard/applications` — application status/progress tracking
- `/dashboard/passport` — document upload/readiness (private Supabase Storage, signed URLs)
- `/dashboard/advisor` — AI Advisor, grounded in the signed-in student's real data
- `/dashboard/notifications`, `/dashboard/profile`, `/dashboard/settings`

## Production deployment notes

- **Domains**: same-site custom-domain architecture (`app.<domain>` for the frontend, `api.<domain>` for the backend, both HTTPS). Set `FRONTEND_URL` (backend) and `VITE_API_BASE_URL` (frontend) accordingly.
- **Supabase**: add the production `FRONTEND_URL` to the Supabase project's Allowed Redirect URLs, or signup-confirmation/password-reset email links will fail.
- **Migrations**: `alembic upgrade head` must run against the production database before the backend starts serving traffic - there is no automatic migration-on-startup.
- **Secrets**: `SUPABASE_SECRET_KEY`, `GROQ_API_KEY`, and `DATABASE_URL` are server-side only and must never reach the frontend build or any client-visible config.
