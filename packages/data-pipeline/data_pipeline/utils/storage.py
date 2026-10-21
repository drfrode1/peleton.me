import json
from datetime import UTC, datetime


def archive_bronze_payload(
    s3_client,
    bucket: str,
    domain: str,
    source: str,
    entity: str,
    location_id: str,
    payload: dict
) -> str:
    """Archives raw API responses to S3 using the standardized partition path."""
    now = datetime.now(UTC)
    key = (
        f"bronze/{domain}/{source}/{entity}/"
        f"location={location_id}/"
        f"year={now.strftime('%Y')}/month={now.strftime('%m')}/day={now.strftime('%d')}/"
        f"{entity}_{now.strftime('%H%M%S')}.json"
    )
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json"
    )
    return key