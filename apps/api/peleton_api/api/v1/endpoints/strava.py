import hashlib
import hmac
import time
from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from peleton_api.core.auth import get_current_user
from peleton_api.core.config import settings
from peleton_api.core.crypto import EncryptedToken, decrypt_token, encrypt_token
from peleton_api.core.database import get_db
from peleton_api.models import models
from peleton_api.schemas.strava import (
    StravaConnectResponse,
    StravaDisconnectResponse,
    StravaStatusResponse,
)

router = APIRouter()
STATE_COOKIE_NAME = "peleton_strava_oauth_state"


def _create_oauth_state(user_id: int) -> str:
    """Creates a HMAC-signed state parameter containing user_id and timestamp."""
    secret = (settings.strava_client_secret or "peleton_default_secret").encode("utf-8")
    now = str(int(time.time()))
    payload = f"{user_id}:{now}"
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def _verify_oauth_state(state: str, user_id: int) -> bool:
    """Verifies that the OAuth state parameter is valid and not expired (15 min)."""
    try:
        parts = state.split(":")
        if len(parts) != 3:
            return False
        state_user_id, timestamp_str, signature = parts
        if int(state_user_id) != user_id:
            return False
        timestamp = int(timestamp_str)
        if time.time() - timestamp > 900:  # 15 min expiry
            return False
        secret = (settings.strava_client_secret or "peleton_default_secret").encode("utf-8")
        expected_sig = hmac.new(
            secret, f"{state_user_id}:{timestamp_str}".encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_sig)
    except Exception:  # noqa: BLE001
        return False


@router.get("/connect", response_model=StravaConnectResponse)
def connect_strava(
    response: Response,
    current_user: models.User = Depends(get_current_user),
):
    """Generates Strava OAuth authorization URL and sets a state cookie."""
    if not settings.strava_client_id or not settings.strava_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Strava is not configured for this environment.",
        )

    state = _create_oauth_state(current_user.id)
    response.set_cookie(
        key=STATE_COOKIE_NAME,
        value=state,
        max_age=900,
        httponly=True,
        samesite="lax",
    )

    params = {
        "client_id": settings.strava_client_id,
        "redirect_uri": settings.strava_redirect_uri,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "read,activity:read_all",
        "state": state,
    }
    authorization_url = f"https://www.strava.com/oauth/authorize?{urlencode(params)}"
    return {"authorization_url": authorization_url}


@router.get("/callback")
def strava_oauth_callback(
    response: Response,
    code: str | None = Query(None),
    state: str | None = Query(None),
    scope: str | None = Query(None),
    error: str | None = Query(None),
    cookie_state: str | None = Cookie(None, alias=STATE_COOKIE_NAME),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Handles OAuth callback from Strava, encrypts tokens, and saves connection."""
    redirect_target = f"{settings.frontend_url}/settings"
    response.delete_cookie(key=STATE_COOKIE_NAME)

    if error:
        return RedirectResponse(f"{redirect_target}?strava=denied")

    if not state or not _verify_oauth_state(state, current_user.id):
        return RedirectResponse(f"{redirect_target}?strava=error")

    if not code:
        return RedirectResponse(f"{redirect_target}?strava=error")

    accepted_scopes = [s.strip() for s in (scope or "").split(",") if s.strip()]
    if "activity:read_all" not in accepted_scopes:
        return RedirectResponse(f"{redirect_target}?strava=scope-required")

    # Exchange authorization code for access and refresh tokens
    try:
        with httpx.Client(timeout=15.0) as client:
            token_res = client.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": settings.strava_client_id,
                    "client_secret": settings.strava_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            token_res.raise_for_status()
            token_data = token_res.json()
    except Exception:  # noqa: BLE001
        return RedirectResponse(f"{redirect_target}?strava=error")

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_at = token_data.get("expires_at")
    athlete = token_data.get("athlete", {})
    athlete_id = str(athlete.get("id"))

    if not access_token or not refresh_token or not athlete_id:
        return RedirectResponse(f"{redirect_target}?strava=error")

    # Encrypt tokens with AES-256-GCM
    access_enc = encrypt_token(access_token)
    refresh_enc = encrypt_token(refresh_token)
    token_expires_dt = datetime.fromtimestamp(expires_at, tz=UTC)

    # Upsert connection record in PostgreSQL
    connection = (
        db.query(models.StravaConnection)
        .filter(models.StravaConnection.user_id == current_user.id)
        .first()
    )

    if not connection:
        connection = models.StravaConnection(
            user_id=current_user.id,
            athlete_id=athlete_id,
            access_token_ciphertext=access_enc.ciphertext,
            access_token_iv=access_enc.iv,
            access_token_tag=access_enc.tag,
            refresh_token_ciphertext=refresh_enc.ciphertext,
            refresh_token_iv=refresh_enc.iv,
            refresh_token_tag=refresh_enc.tag,
            scopes=",".join(accepted_scopes),
            token_expires_at=token_expires_dt,
        )
        db.add(connection)
    else:
        connection.athlete_id = athlete_id
        connection.access_token_ciphertext = access_enc.ciphertext
        connection.access_token_iv = access_enc.iv
        connection.access_token_tag = access_enc.tag
        connection.refresh_token_ciphertext = refresh_enc.ciphertext
        connection.refresh_token_iv = refresh_enc.iv
        connection.refresh_token_tag = refresh_enc.tag
        connection.scopes = ",".join(accepted_scopes)
        connection.token_expires_at = token_expires_dt

    db.commit()
    return RedirectResponse(f"{redirect_target}?strava=connected")


@router.get("/status", response_model=StravaStatusResponse)
def get_strava_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the current user's Strava connection status."""
    connection = (
        db.query(models.StravaConnection)
        .filter(models.StravaConnection.user_id == current_user.id)
        .first()
    )

    if not connection:
        return {"connected": False}

    return {
        "connected": True,
        "athlete_id": connection.athlete_id,
        "scopes": connection.scopes,
        "connected_at": connection.connected_at,
    }


@router.post("/disconnect", response_model=StravaDisconnectResponse)
def disconnect_strava(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes the stored Strava credentials and revokes access at Strava."""
    connection = (
        db.query(models.StravaConnection)
        .filter(models.StravaConnection.user_id == current_user.id)
        .first()
    )

    if not connection:
        return {"connected": False, "provider_revoked": True}

    provider_revoked = False
    try:
        raw_access_token = decrypt_token(
            EncryptedToken(
                ciphertext=connection.access_token_ciphertext,
                iv=connection.access_token_iv,
                tag=connection.access_token_tag,
            )
        )
        with httpx.Client(timeout=10.0) as client:
            revoke_res = client.post(
                "https://www.strava.com/oauth/deauthorize",
                data={"access_token": raw_access_token},
            )
            provider_revoked = revoke_res.is_success
    except Exception:  # noqa: BLE001
        provider_revoked = False

    db.delete(connection)
    db.commit()

    return {"connected": False, "provider_revoked": provider_revoked}
