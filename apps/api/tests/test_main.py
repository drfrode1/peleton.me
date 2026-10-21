from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the public health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "peleton-api"}


def test_weather_endpoint_not_found(client: TestClient):
    """Test that requesting weather for a non-existent location returns 404 or 503."""
    response = client.get("/api/v1/weather/nonexistent-location-999")
    # 404 = Location not found in DuckDB, 503 = DuckDB file missing during test run
    assert response.status_code in (404, 503)