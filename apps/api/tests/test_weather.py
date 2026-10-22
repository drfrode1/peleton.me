import duckdb
import pytest
from fastapi.testclient import TestClient

from peleton_api.core.database import get_duckdb_connection
from peleton_api.main import app


@pytest.fixture
def mock_duckdb():
    """In-memory DuckDB connection pre-seeded with test weather records."""
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE bronze_weather_met_frost (
            location_id VARCHAR,
            reference_time TIMESTAMP,
            element_id VARCHAR,
            value DOUBLE,
            unit VARCHAR,
            ingested_at TIMESTAMP
        );
        INSERT INTO bronze_weather_met_frost VALUES
        ('Forus', CURRENT_TIMESTAMP, 'air_temperature', 12.5, 'degC', CURRENT_TIMESTAMP),
        ('Stavanger', CURRENT_TIMESTAMP, 'air_temperature', 14.0, 'degC', CURRENT_TIMESTAMP);
    """)
    yield con
    con.close()


def test_weather_endpoint_returns_data(client: TestClient, mock_duckdb):
    """Verifies that the analytical weather endpoint correctly queries DuckDB and returns records."""
    app.dependency_overrides[get_duckdb_connection] = lambda: mock_duckdb
    try:
        response = client.get("/api/v1/weather/?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["data"]) == 2
        assert data["filters"]["days"] == 7
    finally:
        app.dependency_overrides.clear()


def test_weather_endpoint_filter_by_location(client: TestClient, mock_duckdb):
    """Verifies filtering by location ID."""
    app.dependency_overrides[get_duckdb_connection] = lambda: mock_duckdb
    try:
        response = client.get("/api/v1/weather/?location=Forus")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["data"][0]["location_id"] == "Forus"
        assert data["data"][0]["value"] == 12.5
    finally:
        app.dependency_overrides.clear()
