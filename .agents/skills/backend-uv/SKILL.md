---
name: backend-uv
description: Use uv for Python backend environment setup, dependency resolution, commands, migrations, and tests in this project.
---

# Backend project management with uv

Use `uv` as the Python environment and package manager for the Shahil Academy backend.

## Project files

- `backend/pyproject.toml` declares runtime dependencies and the `dev` optional extra.
- `backend/uv.lock` locks resolved dependency versions and should remain committed.
- `backend/.venv/` is generated locally and must not be committed.
- `backend/.env` holds local secrets; copy it from `.env.example` and never commit it.

## Setup

From the repository root:

```powershell
Set-Location backend
uv sync --extra dev
```

`uv sync` creates and maintains `.venv`, installs the project and its dependencies, and synchronizes the lockfile. Do not manually create or activate a virtual environment and do not install project packages with `pip`.

## Commands

Run project commands through uv so they use the project environment:

```powershell
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run pytest
```

Add a runtime dependency with `uv add <package>`. Add a development-only dependency with `uv add --dev <package>`. After changing dependency declarations, run `uv lock` and `uv sync --extra dev`, then validate the backend tests.

For CI or deployment where a stale lockfile should fail the setup, use:

```powershell
uv sync --locked --extra dev
```

## Environment and database

Keep backend configuration in `backend/.env`; uv does not replace the application's environment configuration. The backend defaults to SQLite for local use. Apply schema changes using Alembic rather than `Base.metadata.create_all()` in production.

