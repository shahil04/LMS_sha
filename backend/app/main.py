from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings

if settings.app_env.lower() == "production" and "*" in settings.allowed_origins:
    raise RuntimeError("CORS_ORIGINS must list exact trusted origins in production")

app = FastAPI(
    title="Shahil Academy API",
    version="1.0.0",
    description="Learning platform API. Authentication is provided by Supabase Auth.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
