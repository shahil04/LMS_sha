# Shahil Academy

A full-stack Learning Management System built with React, TypeScript, Vite, FastAPI, SQLAlchemy, and Supabase Auth. The API uses PostgreSQL in production and can use SQLite for local development.

## Architecture

```text
Browser (React + Supabase Auth)
  ├── Public pages: catalog, course details, policies
  └── Student/Admin portals
          │ Supabase access token (Bearer)
          ▼
FastAPI /api/v1 ── verified Supabase JWT ── role from profiles table
          │
          ▼
SQLAlchemy ── PostgreSQL (Supabase) / SQLite (local)
```

Admin roles are stored in the database and are never accepted from public registration or browser-supplied role claims. The backend enforces enrollment, content publication, ownership, quiz grading, and admin authorization.

## Folder structure

```text
frontend/       React application, routing, forms, and API client
backend/        FastAPI application, data models, migrations, and tests
docs/           API, security, database, and deployment documentation
```

## Database relationship overview

```mermaid
erDiagram
  PROFILES ||--o{ ENROLLMENTS : receives
  COURSES ||--o{ MODULES : contains
  MODULES ||--o{ TOPICS : contains
  COURSES ||--o{ ENROLLMENTS : grants
  TOPICS ||--o{ TOPIC_RESOURCES : provides
  PROFILES ||--o{ TOPIC_PROGRESS : tracks
  TOPICS ||--o{ TOPIC_PROGRESS : records
  PROFILES ||--o{ BOOKMARKS : saves
  TOPICS ||--o{ BOOKMARKS : bookmarked
  TOPICS ||--o{ QUESTIONS : tests
  PROFILES ||--o{ QUIZ_ATTEMPTS : makes
  TOPICS ||--o{ QUIZ_ATTEMPTS : assesses
  PROFILES ||--o{ DOUBTS : asks
  TOPICS ||--o{ DOUBTS : concerns
  DOUBTS ||--o{ DOUBT_REPLIES : has
  PROFILES ||--o{ ANNOUNCEMENTS : authors
```

## Routes and screens

- Public: `/`, `/courses`, `/courses/:slug`, `/about`, `/contact`, `/privacy`, `/terms`
- Auth: `/login`, `/register`, `/forgot-password`, `/reset-password`
- Student: `/student/dashboard`, `/student/courses`, `/student/courses/:courseId`, `/student/learn/:topicId`, `/student/doubts`, `/student/announcements`, `/student/profile`
- Admin: `/admin/dashboard`, `/admin/courses`, `/admin/modules`, `/admin/topics`, `/admin/resources`, `/admin/questions`, `/admin/students`, `/admin/enrollments`, `/admin/doubts`, `/admin/announcements`, `/admin/reports`, `/admin/settings`

## Windows local development

For a detailed, numbered walkthrough, see [runs.md](runs.md).

### Prerequisites

- Node.js 20 or newer and npm
- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for backend dependency and environment management
- A Supabase project for authentication (URL and anon/publishable key)
- PostgreSQL/Supabase database for production; SQLite can be used locally

### Configure and run the backend

```powershell
cd backend
uv sync --extra dev
Copy-Item .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Set `DATABASE_URL` to a Supabase PostgreSQL connection string for a shared environment; the example uses a local SQLite database. Set `SUPABASE_URL` for JWT verification. `/docs` is the interactive OpenAPI page and `/health` checks API availability.

### Configure and run the frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `VITE_API_URL` in `frontend/.env`. Supabase Auth handles registration, login, logout, email verification, and password recovery. Configure the Supabase email templates and redirect URLs for `http://localhost:5173/reset-password`.

### Provisioning the first administrator

Register an account through the application, then use a trusted database connection to change only that account's `profiles.role` to `admin` after its profile row has been created (sign in once first). Never expose the database credential or Supabase service-role key in the frontend. A database migration or trusted operator action is required; public registration cannot set roles.

### Migrations and tests

```powershell
cd backend
uv run alembic upgrade head
uv run pytest
```

```powershell
cd frontend
npm run build
```

## Deployment

See [docs/deployment-guide.md](docs/deployment-guide.md). Set secrets in the hosting providers, run Alembic as a deployment/release step, configure production CORS origins, and configure Supabase Auth redirect URLs. No credentials are included in this repository.

## Current configuration-dependent capabilities

- Supabase Auth requires a configured project and valid frontend environment values.
- Private object storage uploads are intentionally unavailable until a bucket and server-side storage adapter are configured. External resource links work; the API does not claim local disk is persistent storage.
- Video playback is restricted to validated YouTube IDs; unlisted YouTube videos are not enrollment-protected.
- Payment processing is not enabled. No payment-success simulation or paid enrollment flow is present.
- Email delivery, notifications, and deployment must be configured with external providers.
