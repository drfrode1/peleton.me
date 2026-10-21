import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import duckdb
import httpx
import yaml
from dagster import AssetExecutionContext, ResourceParam, asset
from data_pipeline.utils.storage import archive_bronze_payload

FROST_OBSERVATIONS_URL = "https://frost.met.no/observations/v0.jsonld"
FROST_SOURCES_URL = "https://frost.met.no/sources/v0.jsonld"


@asset
def bronze_weather_met_frost(
    context: AssetExecutionContext, 
    s3: ResourceParam[Any]
) -> str:
    """Ingests MET Frost weather observations based on locations.yaml configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "locations.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        loaded_config: Any = yaml.safe_load(f)

    config: dict[str, Any] = loaded_config if isinstance(loaded_config, dict) else {}

    settings: dict[str, Any] = config.get("settings", {}) if isinstance(config.get("settings"), dict) else {}
    default_days: int = int(settings.get("default_history_days", 90))

    client_id = os.getenv("FROST_CLIENT_ID")
    client_secret: str = os.getenv("FROST_CLIENT_SECRET") or ""

    if not client_id:
        raise RuntimeError("FROST_CLIENT_ID environment variable is missing.")

    duckdb_path = os.getenv("LOCAL_DUCKDB_PATH", "/app/data/dev.duckdb")
    bucket = os.getenv("R2_BUCKET_NAME", "peleton-r2-bucket")
    now = datetime.now(UTC)

    con = duckdb.connect(duckdb_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS bronze_weather_met_frost (
            location_id VARCHAR,
            reference_time TIMESTAMP,
            element_id VARCHAR,
            value DOUBLE,
            unit VARCHAR,
            ingested_at TIMESTAMP
        );
    """)

    count_res: Any = con.execute("SELECT COUNT(*) FROM bronze_weather_met_frost")
    count_row = count_res.fetchone() if count_res else None
    existing_count: int = int(count_row[0]) if count_row else 0

    if existing_count == 0:
        start_time = now - timedelta(days=default_days)
        context.log.info(f"Initial ingestion: fetching {default_days} days history.")
    else:
        start_time = now - timedelta(hours=2)

    time_interval = f"{start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}/{now.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
    all_rows: list[tuple[str, Any, Any, Any, Any, datetime]] = []

    locations: list[dict[str, Any]] = cast(
        list[dict[str, Any]], config.get("locations", []) if isinstance(config.get("locations"), list) else []
    )

    with httpx.Client(auth=(client_id, client_secret), timeout=30.0) as client:
        for loc in locations:
            frost_cfg: dict[str, Any] = (
                loc.get("sources", {}).get("met_frost", {})
                if isinstance(loc.get("sources"), dict) and isinstance(loc["sources"].get("met_frost"), dict)
                else {}
            )
            if not frost_cfg.get("enabled", False):
                continue

            loc_id: str = str(loc.get("id", ""))
            coords: dict[str, Any] = loc.get("coordinates", {}) if isinstance(loc.get("coordinates"), dict) else {}
            lon = coords.get("lon")
            lat = coords.get("lat")
            element_ids: list[str] = frost_cfg.get("element_ids", [])

            # Step 1: Find the nearest valid station ID using the /sources endpoint
            source_params = {
                "geometry": f"nearest(POINT({lon} {lat}))",
                "nearestmaxcount": 1,
            }
            src_res = client.get(FROST_SOURCES_URL, params=source_params)
            if src_res.status_code != 200:
                context.log.warning(f"Could not resolve station for {loc_id}: {src_res.text}")
                continue

            src_data = src_res.json()
            sources_list = src_data.get("data", [])
            if not sources_list:
                context.log.warning(f"No weather stations found near {loc_id} ({lon}, {lat}).")
                continue

            station_id = sources_list[0].get("id")
            context.log.info(f"Resolved location '{loc_id}' to nearest MET station ID: {station_id}")

            # Step 2: Query observations using the resolved station ID
            obs_params = {
                "sources": station_id,
                "referencetime": time_interval,
                "elements": ",".join(element_ids),
            }

            res = client.get(FROST_OBSERVATIONS_URL, params=obs_params)
            
            # Handle expected API status warnings gracefully (404 Not Found or 412 Precondition Failed)
            if res.status_code in (404, 412):
                context.log.warning(
                    f"Skipping station {station_id} for {loc_id}: "
                    f"Received HTTP {res.status_code} (Data or elements not supported by this station)."
                )
                continue
                
            res.raise_for_status()
            raw_data: dict[str, Any] = res.json()

            # Step 3: Archive raw JSON payload and extract rows
            archive_bronze_payload(
                s3_client=s3,
                bucket=bucket,
                domain="weather",
                source="met_frost",
                entity="observations",
                location_id=loc_id,
                payload=raw_data,
            )

            for item in raw_data.get("data", []):
                ref_time = item.get("referenceTime")
                for obs in item.get("observations", []):
                    all_rows.append(
                        (
                            loc_id,
                            ref_time,
                            obs.get("elementId"),
                            obs.get("value"),
                            obs.get("unit"),
                            now,
                        )
                    )

    if all_rows:
        con.executemany("INSERT INTO bronze_weather_met_frost VALUES (?, ?, ?, ?, ?, ?)", all_rows)

    con.close()
    return f"Ingested {len(all_rows)} rows."