# Run Shahil Academy step by step

These instructions are for Windows PowerShell. Keep the backend and frontend running in two separate terminal windows. Commands assume the project is at `C:\Users\hp\Documents\lms_sha`; change that path if you moved the folder.

## 1. Install prerequisites

Install:

- Node.js 20 or newer (npm is included).
- Python 3.11 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for backend environment and package management.
- A Supabase project for real registration, sign-in, and password recovery.

Check that PowerShell can find the tools:

```powershell
node --version
npm --version
py -3.11 --version
uv --version
```

## 2. Configure the backend

Open PowerShell window 1 and go to the backend:

```powershell
Set-Location C:\Users\hp\Documents\lms_sha\backend
```

Use uv to create the project environment and install the backend and test dependencies:

```powershell
uv sync --extra dev
```

This creates `.venv`, resolves dependencies from `pyproject.toml` and `uv.lock`, and installs the `dev` extra. No virtual-environment activation is required; run backend commands with `uv run`.

Confirm the project interpreter and environment:

```powershell
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
notepad .env
```

For local SQLite, leave `DATABASE_URL=sqlite:///./shahil_academy.db`. Set `SUPABASE_URL` to your Supabase project URL, such as `https://your-project.supabase.co`. If your Supabase project uses legacy HS256 JWT signing, set `SUPABASE_JWT_SECRET` to the project's JWT secret; keep it only in the backend `.env`. With asymmetric signing keys, leave it blank so the API can verify tokens using Supabase's published JWKS.

Keep the default local CORS origin:

```text
CORS_ORIGINS=http://localhost:5173
APP_ENV=development
```

Do not put database credentials, `SUPABASE_JWT_SECRET`, or the Supabase service-role key in frontend settings or commit them to source control.

## 3. Create or update the database

In the backend terminal:

```powershell
uv run alembic upgrade head
```

For the default SQLite configuration, this creates `backend\shahil_academy.db`. To use Supabase PostgreSQL instead, set `DATABASE_URL` in `backend\.env` to your database connection string before running the migration. Prefer the Supabase pooler connection string when required by your deployment.

## 4. Start the API

From `C:\Users\hp\Documents\lms_sha\backend`:

```powershell
uv run uvicorn app.main:app --reload
```

Leave this terminal open. Check that the API is running:

- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

The health endpoint should return `{"status":"ok"}`.

## 5. Configure the frontend

Open PowerShell window 2 and go to the frontend:

```powershell
Set-Location C:\Users\hp\Documents\lms_sha\frontend
```

Install frontend packages:

```powershell
npm install
```

Create and edit the frontend environment file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set the three values:

```dotenv
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-or-publishable-key
```

Use the project URL and anon/publishable key from the Supabase project settings. These are frontend configuration values; never use the service-role key here. In Supabase Auth, configure the local site URL and allow the redirect URL `http://localhost:5173/reset-password`.

## 6. Start the website

From `C:\Users\hp\Documents\lms_sha\frontend`:

```powershell
npm run dev
```

Open the local URL printed by Vite, normally [http://localhost:5173](http://localhost:5173). Keep this terminal open too. Public course pages can load when the API is running; account-related routes need valid Supabase configuration.

## 7. Create an administrator account

1. Register a student account through the website.
2. Verify the email if email confirmation is enabled in Supabase.
3. Sign in once and visit `/student/dashboard`. This creates the matching database profile row.
4. Using a trusted Supabase SQL editor or another authorized database connection, promote only the intended account:

```sql
UPDATE profiles
SET role = 'admin', updated_at = CURRENT_TIMESTAMP
WHERE email = 'your-admin-email@example.com';
```

5. Sign out and sign in again, then open `/admin/dashboard`.

Never expose database credentials or service-role keys in the browser. Public registration cannot assign admin roles.

## 8. Add course content and student access

From the administrator workspace:

1. Create a course and choose whether it is a draft or published.
2. Copy its ID from the Courses table.
3. Create one or more modules using the course ID.
4. Copy each module ID and add published topics. A YouTube video URL is optional.
5. Add external study-resource links and practice questions to topics.
6. Open Students to find a student's profile ID.
7. Open Enrollments and grant access using the student profile ID and course ID.
8. A student can then open their learning space, course lessons, resources, quizzes, and doubts.

Only use links that students are authorized to access. Private file uploads and payment processing are not configured in this release.

## 9. Run tests and build checks

In the backend terminal, run:

```powershell
Set-Location C:\Users\hp\Documents\lms_sha\backend
uv run pytest
```

In the frontend terminal:

```powershell
Set-Location C:\Users\hp\Documents\lms_sha\frontend
npm run build
npm audit
```

## 10. Stop the local servers

In each terminal running a server, press `Ctrl+C`. The local SQLite database remains at `backend\shahil_academy.db`.

## Troubleshooting

- **API will not start:** Check that `uv sync --extra dev` completed. Check `backend\.env` values and run `uv run alembic upgrade head`.
- **Website cannot load courses:** Confirm the API is running at port 8000 and `VITE_API_URL=http://localhost:8000`. Restart Vite after changing `.env`.
- **Supabase login fails:** Check the project URL and anon/publishable key, Auth email settings, and allowed redirect URLs. Restart Vite after editing `frontend\.env`.
- **Authenticated API requests return 401:** Verify the token is from the configured Supabase project and the backend `SUPABASE_URL` is correct. For legacy HS256 projects, ensure `SUPABASE_JWT_SECRET` is set in the backend only.
- **Administrator is redirected away:** Confirm the matching `profiles` row exists, its `role` is `admin`, and sign in again to refresh the profile.
- **Database schema is out of date:** In the backend terminal run `uv run alembic upgrade head`.
