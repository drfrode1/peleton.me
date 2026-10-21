from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from peleton_api.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provides a reusable FastAPI TestClient instance for the test session."""
    with TestClient(app) as c:
        yield c