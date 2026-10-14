import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import Profile

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Profile:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=503, detail="JWT_SECRET_KEY is not configured")
    if settings.jwt_algorithm not in {"HS256", "HS384", "HS512"}:
        raise HTTPException(status_code=503, detail="JWT_ALGORITHM must be an HMAC algorithm")
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
            audience="authenticated",
        )
    except (jwt.PyJWTError, ValueError) as exc:
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
