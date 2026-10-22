import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables before module imports
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("STRAVA_CLIENT_ID", "123456")
os.environ.setdefault("STRAVA_CLIENT_SECRET", "test_strava_secret")
os.environ.setdefault(
    "STRAVA_TOKEN_ENCRYPTION_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
)

import peleton_api.models.models  # noqa: F401
from peleton_api.core.database import Base, get_db
from peleton_api.main import app

# In-memory SQLite database shared across test threads
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provides a reusable FastAPI TestClient instance for the test session."""
    with TestClient(app) as c:
        yield c
