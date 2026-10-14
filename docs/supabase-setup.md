# Using Supabase PostgreSQL (optional)

The application no longer uses Supabase Auth. The FastAPI backend handles registration and login, signs its own HS256 access tokens, and does not send email verification or recovery messages. Supabase is optional as a PostgreSQL database provider only.

## Configure the database

Create a Supabase project and copy its PostgreSQL connection string from **Project Settings → Database**. Set it as `DATABASE_URL` in `backend/.env` or the backend host's protected environment settings. URL-encode reserved characters in the password, and use the connection mode supported by your deployment.

Apply the LMS database schema from the `backend/` directory:

```powershell
uv run alembic upgrade head
```

The migration adds the nullable `profiles.password_hash` column used for backend-managed accounts. Existing profiles created through Supabase Auth do not have a backend password hash and cannot sign in to the new authentication system. Do not let users claim those profiles solely by entering the same unverified email address; that could expose existing student data. Plan a trusted account-migration or re-enrollment process before switching an established deployment.

## Configure backend JWTs

Keep the following values in `backend/.env` or the backend host's secret manager:

```dotenv
JWT_SECRET_KEY=use-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a unique, unpredictable production secret of at least 32 random bytes. Never put `JWT_SECRET_KEY` in frontend variables or source control. The frontend only needs the API origin:

```dotenv
VITE_API_URL=http://localhost:8000
```

## Important account behavior

- Registration creates an active student account and immediately returns a bearer token; email ownership is not verified.
- Public registration cannot assign administrator roles. Promote an account only through a trusted database operator workflow.
- Email-based password recovery is not configured. Users who lose access need a trusted administrator recovery process.
