import base64

import pytest
from fastapi.testclient import TestClient

from peleton_api.core.crypto import decrypt_token, encrypt_token

# Generate a valid 32-byte Base64 key for testing
TEST_ENCRYPTION_KEY = base64.b64encode(b"01234567890123456789012345678901").decode("utf-8")


@pytest.fixture(autouse=True)
def setup_strava_env(monkeypatch):
    """Sets required Strava environment variables for test execution."""
    monkeypatch.setenv("STRAVA_CLIENT_ID", "123456")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "super_secret_strava_key")
    monkeypatch.setenv("STRAVA_REDIRECT_URI", "http://localhost:8000/api/v1/strava/callback")
    monkeypatch.setenv("STRAVA_TOKEN_ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)


def test_strava_token_encryption_decryption():
    """Verifies that AES-256-GCM correctly encrypts and decrypts OAuth tokens."""
    token = "strava_sample_access_token_abc123"
    encrypted = encrypt_token(token)

    assert encrypted.ciphertext != token
    assert len(encrypted.iv) > 0
    assert len(encrypted.tag) > 0

    decrypted = decrypt_token(encrypted)
    assert decrypted == token


def test_strava_connect_endpoint(client: TestClient):
    """Verifies that /api/v1/strava/connect returns authorization URL with state cookie."""
    response = client.get("/api/v1/strava/connect")
    assert response.status_code == 200

    data = response.json()
    assert "authorization_url" in data
    assert "https://www.strava.com/oauth/authorize" in data["authorization_url"]
    assert "client_id=123456" in data["authorization_url"]
    assert "scope=read%2Cactivity%3Aread_all" in data["authorization_url"]

    # Verify state cookie was set
    assert "peleton_strava_oauth_state" in response.cookies


def test_strava_status_disconnected(client: TestClient):
    """Verifies status endpoint when no Strava connection exists."""
    response = client.get("/api/v1/strava/status")
    assert response.status_code == 200
    assert response.json() == {"connected": False, "athlete_id": None, "scopes": None, "connected_at": None}
