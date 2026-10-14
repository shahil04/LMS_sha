# Host the Shahil Academy frontend and backend

This guide describes a Vercel frontend and Render FastAPI service, with a managed PostgreSQL database (Supabase PostgreSQL is optional). The same build settings can be adapted to other static frontend and Python application hosts. Provider dashboard labels and free-tier limits can change; check current provider documentation before deploying.

## Deployment layout

```text
Browser
  ├── Vercel: React/Vite static site (HTTPS)
  └── Render: FastAPI service (HTTPS)
        └── Managed PostgreSQL: LMS application records
```

Use a managed PostgreSQL database for production. Do not use the backend's local SQLite file as production storage: local application disks may be ephemeral and are not a reliable shared database for multiple instances.

## 1. Prepare the database

Before deploying:

1. Select a PostgreSQL provider. For Supabase, copy a PostgreSQL connection string from **Project Settings → Database**. Use the connection mode supported by your host and networking; URL-encode reserved characters in the password.
2. Generate a strong random `JWT_SECRET_KEY` for backend token signing and store it only in the backend host's secret settings.
3. Do not expose the JWT signing secret or database password to the browser.

The backend issues HS256 tokens for registered users without email verification. Email-based password recovery is not configured.

## 2. Deploy the FastAPI backend to Render

Create a **Web Service** connected to this repository.

### Service settings

| Setting | Value |
|---|---|
| Root directory | `backend` |
| Runtime | Python |
| Build command | `uv sync --locked --extra dev` |
| Pre-deploy/release command | `uv run alembic upgrade head` |
| Start command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/health` |

`uv.lock` must be committed at the repository root of the backend service (`backend/uv.lock`). If the host does not have `uv` on its build/runtime PATH, configure its supported Python build setup to install `uv` first, then use the commands above. Keep build, release, and start commands using the same locked project environment.

If the selected host does not provide a pre-deploy/release command, run `uv run alembic upgrade head` as a one-off command against the service's production environment before sending traffic after each schema change. Do not run schema upgrades in every application worker at startup.

### Backend environment variables

Set these in the Render service's environment/secret settings. Do not commit real values:

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME?sslmode=require
JWT_SECRET_KEY=GENERATE_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN
```

- Use the full connection string supplied by the PostgreSQL provider; the example is illustrative. Confirm the SQLAlchemy `postgresql+psycopg` scheme and required TLS options for the selected connection.
- Store a cryptographically random JWT secret only in the backend host's protected environment settings. Do not reuse the example or place it in frontend environment variables.
- `CORS_ORIGINS` must contain the exact frontend origin, including scheme and any custom port, but no path. Multiple origins are comma-separated, for example `https://academy.example.com,https://www.academy.example.com`.
- Set `APP_ENV=production`; the API rejects wildcard CORS in production.
- Do not set `VITE_` variables on the backend.

After deployment, confirm `https://YOUR-API-DOMAIN/health` returns `{"status":"ok"}` and `https://YOUR-API-DOMAIN/docs` displays the OpenAPI page. Restrict or disable public API docs at the host/edge only if your operating requirements call for that.

## 3. Deploy the React frontend to Vercel

Import the repository as a Vercel project and set the root directory to `frontend`.

| Setting | Value |
|---|---|
| Framework preset | Vite |
| Install command | `npm install` |
| Build command | `npm run build` |
| Output directory | `dist` |

Set this as a Vercel **build environment variable**:

```dotenv
VITE_API_URL=https://YOUR-API-DOMAIN
```

The API URL is the origin only; the frontend API client appends `/api/v1`. Vite embeds `VITE_` values in the generated browser bundle. Never put the database password or `JWT_SECRET_KEY` in a `VITE_` value.

### Client-side route fallback

React Router serves routes such as `/student/dashboard` and `/admin/courses`. The static host must route those paths back to `index.html` so reloading a nested route does not return a host-level 404.

For Vercel, add `frontend/vercel.json` with:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

If the static host offers an SPA fallback setting instead, configure its equivalent to serve `index.html` for application routes while allowing generated assets to be served normally.

## 4. Connect the frontend and backend

After the frontend receives its final production domain:

1. Update Render's `CORS_ORIGINS` to that exact HTTPS frontend origin (plus any additional trusted production origins).
2. Trigger a new frontend build after changing `VITE_` variables. Restart/redeploy the backend after changing backend environment variables.

## 5. Provision an administrator

Public sign-up only creates student profiles. Once the intended admin has registered, use a trusted operator connection to set its database role:

```sql
UPDATE profiles
SET role = 'admin', updated_at = CURRENT_TIMESTAMP
WHERE email = 'your-admin-email@example.com'
  AND role = 'student';
```

Run this against the same production database referenced by the backend's `DATABASE_URL`. Check that exactly the intended profile was updated. Do not attempt to grant admin access using browser data, user-editable metadata, or frontend route settings.

## 6. Verify production before announcing availability

- Confirm `GET /health` works on the public API URL.
- Confirm public course catalog requests from the deployed website succeed without CORS errors.
- Register a test student and verify immediate sign-in, token persistence, and logout. Confirm no email is sent by registration.
- Confirm an enrolled student can access a published course and an unenrolled student cannot.
- Confirm student requests to `/api/v1/admin/*` receive `403`.
- Confirm a draft course/topic is not exposed through the public catalog or student lesson endpoints.
- Confirm an admin can create/publish content and grant enrollment.
- Confirm the production migration ran against the intended PostgreSQL database.
- Check host logs for startup and migration errors; never log access tokens, passwords, or database connection strings.
- Test refresh/deep links on `/courses/...`, `/student/...`, and `/admin/...`.

## 7. Updating a deployment

1. Make and validate code changes locally (`uv run pytest` in `backend/`; `npm run build` in `frontend/`).
2. Commit and push the reviewed changes to the deployment branch.
3. Apply the Alembic migration once as a release/pre-deploy step before the new backend code needs the changed schema.
4. Allow Render and Vercel to deploy the backend and frontend.
5. Recheck health, authentication, CORS, and critical student/admin workflows.

Keep database backups and use backward-compatible schema migrations when rolling out changes that require both old and new application versions during deployment.

## Cost, availability, and security

Hosted free tiers may sleep, impose quotas, limit build minutes, or have no persistent disk; availability and limits can change. Check current Render, Vercel, and Supabase plan documentation before choosing production services. This project does not configure private object storage, payment processing, transactional email delivery, or rate limiting. Add and test those integrations separately before relying on them.
