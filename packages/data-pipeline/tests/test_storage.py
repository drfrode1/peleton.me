from unittest.mock import MagicMock

from data_pipeline.utils.config_loader import load_locations_config
from data_pipeline.utils.storage import archive_bronze_payload


def test_archive_bronze_payload_structure(mock_s3_client: MagicMock):
    """Test that archive_bronze_payload constructs the expected S3/R2 key and calls put_object."""
    payload = {"sample_metric": 42.0}
    key = archive_bronze_payload(
        s3_client=mock_s3_client,
        bucket="test-bucket",
        domain="weather",
        source="met_frost",
        entity="observations",
        location_id="Forus",
        payload=payload,
    )

    assert key.startswith("bronze/weather/met_frost/observations/location=Forus/")
    assert key.endswith(".json")
    mock_s3_client.put_object.assert_called_once()
    call_kwargs = mock_s3_client.put_object.call_args[1]
    assert call_kwargs["Bucket"] == "test-bucket"
    assert call_kwargs["Key"] == key
    assert call_kwargs["ContentType"] == "application/json"


def test_load_locations_config():
    """Test that load_locations_config successfully loads locations.yaml."""
    config = load_locations_config()
    assert isinstance(config, dict)
    assert "locations" in config
    assert len(config["locations"]) > 0
    # Verify that first location has an id
    first_loc = config["locations"][0]
    assert "id" in first_loc
