import os
from datetime import datetime, timedelta

import duckdb
import polars as pl
import pytz
import requests
from dagster import Output, asset

OSLO_TZ = pytz.timezone("Europe/Oslo")
API_URL = "https://trafikkdata-api.atlas.vegvesen.no"

@asset(
    group_name="traffic",
    description="Fetches 3-month historical and incremental traffic volumes for all locations configured in locations.yaml."
)
def bronze_traffic_volumes_vegvesen() -> Output[str]:
    # Import config loader from utils
    from data_pipeline.utils.config_loader import load_locations_config
    config = load_locations_config()

    now = datetime.now(OSLO_TZ)
    to_time = now.isoformat()
    default_days = config.get("settings", {}).get("default_history_days", 90)
    from_time = (now - timedelta(days=default_days)).isoformat() 

    all_records = []

    # Iterate through locations defined in YAML
    for loc in config.get("locations", []):
        loc_id = loc.get("id")
        sources = loc.get("sources", {})
        tv_source = sources.get("traffic_volumes", {})

        if not tv_source.get("enabled", False):
            continue

        trp_ids = tv_source.get("trp_ids", [])

        for trp_id in trp_ids:
            query = f"""
            {{
              trafficData(trafficRegistrationPointId: "{trp_id}") {{
                volume {{
                  byHour(from: "{from_time}", to: "{to_time}") {{
                    edges {{
                      node {{
                        from
                        to
                        total {{
                          volumeNumbers {{
                            volume
                          }}
                          coverage {{
                            percentage
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """

            response = requests.post(
                API_URL,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            try:
                edges = data["data"]["trafficData"]["volume"]["byHour"]["edges"]
                for edge in edges:
                    node = edge["node"]
                    total_vol = node.get("total", {})
                    volume_num = total_vol.get("volumeNumbers", {}).get("volume")
                    coverage_pct = total_vol.get("coverage", {}).get("percentage")

                    all_records.append({
                        "location_id": loc_id,  # Linked to your location structure!
                        "traffic_registration_point_id": trp_id,
                        "from_time": node.get("from"),
                        "to_time": node.get("to"),
                        "volume": volume_num,
                        "coverage_percentage": coverage_pct,
                        "ingested_at": now.isoformat()
                    })
            except (KeyError, TypeError) as e:
                print(f"Warning: Could not parse traffic volume data for location {loc_id} (TRP {trp_id}): {e}")

    if not all_records:
        raise ValueError("No traffic volume records retrieved from Trafikkdata API for any location.")

    df = pl.DataFrame(all_records)
    
    df = df.with_columns([
        pl.col("from_time").str.to_datetime(time_zone="Europe/Oslo", strict=False),
        pl.col("to_time").str.to_datetime(time_zone="Europe/Oslo", strict=False),
        pl.col("ingested_at").str.to_datetime(time_zone="Europe/Oslo", strict=False),
    ])

    os.makedirs("bronze_data/traffic_volumes", exist_ok=True)
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    parquet_path = f"bronze_data/traffic_volumes/traffic_volumes_{timestamp_str}.parquet"
    
    df.write_parquet(parquet_path)

    return Output(
        parquet_path,
        metadata={
            "record_count": len(df),
            "parquet_path": parquet_path,
            "fetched_at": now.isoformat(),
        }
    )

@asset(
    group_name="traffic",
    description="Loads Bronze Parquet traffic volume snapshots into the Silver DuckDB analytics table with deduplication."
)
def silver_traffic_volumes_vegvesen(bronze_traffic_volumes_vegvesen: str) -> Output[int]:
    db_path = os.getenv("DUCKDB_PATH", "duckdb_data/analytics.duckdb")
    
    con = duckdb.connect(db_path)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_traffic_volumes_vegvesen (
            location_id VARCHAR,
            traffic_registration_point_id VARCHAR,
            from_time TIMESTAMP,
            to_time TIMESTAMP,
            volume DOUBLE,
            coverage_percentage DOUBLE,
            ingested_at TIMESTAMP
        )
    """)

    con.execute(f"""
        CREATE TEMP TABLE incoming_volumes AS 
        SELECT * FROM read_parquet('{bronze_traffic_volumes_vegvesen}');
    """)

    # Deduplicate based on location, point, and start time
    con.execute("""
        DELETE FROM silver_traffic_volumes_vegvesen 
        WHERE (location_id, traffic_registration_point_id, from_time) IN (
            SELECT location_id, traffic_registration_point_id, from_time FROM incoming_volumes
        );
    """)

    con.execute("""
        INSERT INTO silver_traffic_volumes_vegvesen 
        SELECT * FROM incoming_volumes;
    """)
    
    row_count = pl.read_parquet(bronze_traffic_volumes_vegvesen).height
    con.close()

    return Output(
        row_count,
        metadata={
            "processed_rows": row_count,
            "source_parquet": bronze_traffic_volumes_vegvesen,
            "table": "silver_traffic_volumes_vegvesen"
        }
    )