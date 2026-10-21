import os

import boto3
from botocore.client import Config
from dagster import Definitions, ScheduleDefinition, define_asset_job

from data_pipeline.assets.bronze import weather_frost
from data_pipeline.resources import MotherDuckResource

# Define Job
weather_job = define_asset_job(
    name="bronze_weather_hourly_job",
    selection=["bronze_weather_met_frost"],
)

# Hourly Schedule
hourly_weather_schedule = ScheduleDefinition(
    job=weather_job,
    cron_schedule="0 * * * *",
)

# Read Environment Variables (with local fallback defaults for SeaweedFS/R2)
endpoint_url = os.getenv("R2_ENDPOINT", "http://minio:8333")
access_key_id = os.getenv("R2_ACCESS_KEY_ID", "test")
secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY", "test")
region_name = os.getenv("R2_REGION_NAME", "auto")

# Validate required S3/R2 settings
missing_vars = [
    var_name
    for var_name, var_val in [
        ("R2_ENDPOINT", endpoint_url),
        ("R2_ACCESS_KEY_ID", access_key_id),
        ("R2_SECRET_ACCESS_KEY", secret_access_key),
    ]
    if not var_val
]

if missing_vars:
    raise RuntimeError(
        f"Missing required environment variables for S3/R2 client: {', '.join(missing_vars)}"
    )

# Configure boto3 client for S3/R2 compatibility
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name=region_name,
    config=Config(signature_version="s3v4"),
)

defs = Definitions(
    assets=[weather_frost.bronze_weather_met_frost],
    jobs=[weather_job],
    schedules=[hourly_weather_schedule],
    resources={
        "s3": s3_client,
        "motherduck": MotherDuckResource(),
    },
)