# Deployment guide

## Supabase

1. Create a project and configure Auth email confirmation and password recovery.
2. Add the exact frontend production URL to Auth site/redirect URL settings.
3. Obtain the project URL and anon/publishable key for the frontend.
4. Obtain a PostgreSQL connection string for the backend and store it as `DATABASE_URL` in the backend host. Use a pooled connection URL when required by the host's connection limits.
5. Run `alembic upgrade head` as a one-off release command before routing traffic.
6. Create/provision the first admin only through a trusted database operator workflow.

## Frontend host

Deploy `frontend/` as a Vite static application. Set `VITE_API_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY` as build environment variables. Configure SPA fallback/rewrite to `index.html`.

## FastAPI host

Run `uvicorn app.main:app --host 0.0.0.0 --port $PORT` from `backend/`. Configure `DATABASE_URL`, `SUPABASE_URL`, and comma-separated `CORS_ORIGINS`. Store secrets in the host's secret manager, require HTTPS, and keep the API and database region/network settings aligned where possible.

Free-tier availability, sleep/cold-start behavior, storage, and usage limits change; verify the current provider documentation and do not treat free resources as permanent or unlimited. Logs should not contain access tokens, passwords, or sensitive profile data.
