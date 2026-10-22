import os
import xml.etree.ElementTree as ET
from datetime import datetime

import duckdb
import polars as pl
import pytz
import requests
from dagster import Output, asset

OSLO_TZ = pytz.timezone("Europe/Oslo")

@asset(
    group_name="traffic",
    description="Fetches Vegvesen XML snapshot for travel times, parses durations, and writes structured Parquet to Bronze."
)

def bronze_travel_times_vegvesen() -> Output[str]:
    url = "https://datex-server-get-v3-1.atlas.vegvesen.no/datexapi/GetTravelTimeData/pullsnapshotdata"
    
    username = os.getenv("VEGVESEN_USERNAME")
    password = os.getenv("VEGVESEN_PASSWORD")
    
    if not username or not password:
        raise ValueError("Missing VEGVESEN_USERNAME or VEGVESEN_PASSWORD in environment variables.")

    response = requests.get(url, auth=(username, password), timeout=30)
    response.raise_for_status()
    
    root = ET.fromstring(response.text)
    
    def local_name(tag: str) -> str:
        return tag.split("}")[-1] if "}" in tag else tag

    records = {}

    for elem in root.iter():
        if local_name(elem.tag) == "physicalQuantity":
            loc_ref = elem.find(".//{*}predefinedLocationReference")
            if loc_ref is not None:
                loc_id = loc_ref.attrib.get("id")
                
                if loc_id not in records:
                    records[loc_id] = {
                        "location_id": loc_id,
                        "start_time": None,
                        "end_time": None,
                        "travel_time_seconds": None,
                        "free_flow_travel_time_seconds": None,
                        "free_flow_speed": None,
                        "traffic_status": None,
                        "ingested_at": datetime.now(OSLO_TZ).isoformat()
                    }

                start_elem = elem.find(".//{*}startOfPeriod")
                end_elem = elem.find(".//{*}endOfPeriod")
                if start_elem is not None: records[loc_id]["start_time"] = start_elem.text
                if end_elem is not None: records[loc_id]["end_time"] = end_elem.text

                tt_elem = elem.find(".//{*}travelTime/{*}duration")
                if tt_elem is not None and tt_elem.text is not None:
                    records[loc_id]["travel_time_seconds"] = float(tt_elem.text)

                fft_elem = elem.find(".//{*}freeFlowTravelTime/{*}duration")
                if fft_elem is not None and fft_elem.text is not None:
                    records[loc_id]["free_flow_travel_time_seconds"] = float(fft_elem.text)

                ffs_elem = elem.find(".//{*}freeFlowSpeed/{*}speed")
                if ffs_elem is not None and ffs_elem.text is not None:
                    records[loc_id]["free_flow_speed"] = float(ffs_elem.text)

                ts_elem = elem.find(".//{*}trafficStatusValue")
                if ts_elem is not None:
                    records[loc_id]["traffic_status"] = ts_elem.text

    parsed_rows = list(records.values())
    if not parsed_rows:
        raise ValueError("No travel time records found in snapshot XML.")

    df = pl.DataFrame(parsed_rows)
    
    df = df.with_columns([
        pl.col("start_time").str.to_datetime(time_zone="Europe/Oslo", strict=False),
        pl.col("end_time").str.to_datetime(time_zone="Europe/Oslo", strict=False),
        pl.col("ingested_at").str.to_datetime(time_zone="Europe/Oslo", strict=False),
    ])

    os.makedirs("bronze_data/travel_times", exist_ok=True)
    timestamp_str = datetime.now(OSLO_TZ).strftime("%Y%m%d_%H%M%S")
    parquet_path = f"bronze_data/travel_times/travel_times_{timestamp_str}.parquet"
    
    df.write_parquet(parquet_path)

    return Output(
        parquet_path,
        metadata={
            "record_count": len(df),
            "parquet_path": parquet_path,
            "fetched_at": datetime.now(OSLO_TZ).isoformat(),
        }
    )

@asset(
    group_name="traffic",
    description="Loads Bronze Parquet travel time snapshots into the Silver DuckDB analytics table."
)
def silver_travel_times_vegvesen(bronze_travel_times_vegvesen: str) -> Output[int]:
    db_path = os.getenv("DUCKDB_PATH", "duckdb_data/analytics.duckdb")
    
    con = duckdb.connect(db_path)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_travel_times_vegvesen (
            location_id VARCHAR,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            travel_time_seconds DOUBLE,
            free_flow_travel_time_seconds DOUBLE,
            free_flow_speed DOUBLE,
            traffic_status VARCHAR,
            ingested_at TIMESTAMP
        )
    """)

    con.execute(f"""
        INSERT INTO silver_travel_times_vegvesen 
        SELECT * FROM read_parquet('{bronze_travel_times_vegvesen}')
    """)
    
    row_count = pl.read_parquet(bronze_travel_times_vegvesen).height
    con.close()

    return Output(
        row_count,
        metadata={
            "inserted_rows": row_count,
            "source_parquet": bronze_travel_times_vegvesen,
            "table": "silver_travel_times_vegvesen"
        }
    )