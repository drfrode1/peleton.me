import logging

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from peleton_api.core.config import settings
from peleton_api.core.database import get_db
from peleton_api.models import models

logger = logging.getLogger(__name__)

_jwks_client: jwt.PyJWKClient | None = None


def get_jwks_client() -> jwt.PyJWKClient | None:
    """Caches and returns PyJWKClient instance for Neon / Better Auth JWKS verification."""
    global _jwks_client
    if not settings.neon_auth_url:
        return None

    if _jwks_client is None:
        jwks_url = f"{settings.neon_auth_url.rstrip('/')}/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url)
    return _jwks_client


def get_current_user(
    authorization: str | None = Header(None),
    x_dev_user_id: str | None = Header(None),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Authenticates request via Bearer JWT token against JWKS.
    Falls back to dev user if running in development mode without NEON_AUTH_URL configured.
    """
    auth_user_id: str | None = None
    email: str | None = None
    name: str | None = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1]
        jwks_client = get_jwks_client()

        if jwks_client:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["EdDSA", "RS256"],
                    issuer=settings.neon_auth_url,
                    audience=settings.neon_auth_url,
                )
                auth_user_id = payload.get("sub")
                email = payload.get("email")
                name = payload.get("name")
            except Exception as e:
                logger.warning(f"JWT verification failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token.",
                ) from e
        else:
            # Fallback for dev / unconfigured JWKS
            auth_user_id = "00000000-0000-0000-0000-000000000001"
            email = "dev@peleton.me"
            name = "Dev Commuter"
    elif x_dev_user_id:
        auth_user_id = x_dev_user_id
        email = f"{x_dev_user_id}@peleton.me"
        name = "Dev User"
    elif not settings.neon_auth_url:
        # Local development auto-user
        auth_user_id = "00000000-0000-0000-0000-000000000001"
        email = "dev@peleton.me"
        name = "Dev Commuter"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    # Fetch or provision local user record
    user = db.query(models.User).filter(
        (models.User.auth_user_id == auth_user_id) | (models.User.email == email)
    ).first()

    if not user:
        user = models.User(
            auth_user_id=auth_user_id,
            email=email or "unknown@peleton.me",
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
