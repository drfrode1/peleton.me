import os
from unittest.mock import MagicMock

import pytest

# Ensure required environment variables for local testing are present
os.environ.setdefault("R2_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test-key")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test-secret")
os.environ.setdefault("R2_BUCKET_NAME", "peleton-r2-bucket")
os.environ.setdefault("LOCAL_DUCKDB_PATH", ":memory:")


@pytest.fixture
def mock_s3_client():
    """Provides a mock S3 client for testing storage operations."""
    client = MagicMock()
    client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    return client
