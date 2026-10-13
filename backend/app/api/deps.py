from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import Profile

bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client() -> PyJWKClient:
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL is not configured")
    return PyJWKClient(f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Profile:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        if settings.supabase_jwt_secret:
            claims = jwt.decode(
                credentials.credentials,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"require": ["sub", "exp"]},
                audience="authenticated",
            )
        else:
            signing_key = _jwks_client().get_signing_key_from_jwt(credentials.credentials).key
            claims = jwt.decode(
                credentials.credentials,
                signing_key,
                algorithms=["ES256", "RS256"],
                audience="authenticated",
                issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1",
                options={"require": ["sub", "exp"]},
            )
    except (jwt.PyJWTError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc

    subject = claims.get("sub")
    email = claims.get("email")
    if not isinstance(subject, str) or not isinstance(email, str):
        raise HTTPException(status_code=401, detail="Access token is missing required identity claims")
    profile = db.get(Profile, subject)
    if profile is None:
        metadata = claims.get("user_metadata")
        full_name = metadata.get("full_name", "") if isinstance(metadata, dict) else ""
        profile = Profile(
            id=subject,
            email=email,
            full_name=full_name[:160] if isinstance(full_name, str) else "",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    if not profile.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return profile


def require_admin(user: Profile = Depends(get_current_user)) -> Profile:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
