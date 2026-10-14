# Deployment guide

## Database and authentication

Use any supported PostgreSQL provider, including Supabase, for the backend database. Store its connection string as `DATABASE_URL`. Set `JWT_SECRET_KEY` to a strong random secret, `JWT_ALGORITHM=HS256`, and `ACCESS_TOKEN_EXPIRE_MINUTES=60` in the backend host's protected environment settings. Registration immediately returns an access token and does not send email.

Run `uv run alembic upgrade head` as a one-off release command before routing traffic. Create/provision the first admin only through a trusted database operator workflow. Email-based password recovery is not configured.

## Frontend host

Deploy `frontend/` as a Vite static application. Set `VITE_API_URL` as a build environment variable. Configure SPA fallback/rewrite to `index.html`.

## FastAPI host

Run `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` from `backend/`. Configure `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and comma-separated `CORS_ORIGINS`. Store secrets in the host's secret manager, require HTTPS, and keep the API and database region/network settings aligned where possible.

Free-tier availability, sleep/cold-start behavior, storage, and usage limits change; verify the current provider documentation and do not treat free resources as permanent or unlimited. Logs should not contain access tokens, passwords, or sensitive profile data.
