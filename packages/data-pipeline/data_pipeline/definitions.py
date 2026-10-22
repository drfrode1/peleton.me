import os

import boto3
from botocore.client import Config
from dagster import Definitions, ScheduleDefinition, define_asset_job

from data_pipeline.assets import traffic_volumes, travel_times, weather_frost
from data_pipeline.resources import MotherDuckResource

travel_times_job = define_asset_job(
    name="travel_times_rush_hour_job",
    selection=["bronze_travel_times_vegvesen", "silver_travel_times_vegvesen"]
)

# Schedule: Every 5 minutes during rush hours (06:00-09:00 and 15:00-18:00), Monday to Friday.
travel_times_schedule = ScheduleDefinition(
    job=travel_times_job,
    cron_schedule="*/5 6-8,15-17 * * 1-5",
    execution_timezone="Europe/Oslo",
)

traffic_volumes_job = define_asset_job(
    name="traffic_volumes_rush_hour_job",
    selection=["bronze_traffic_volumes_vegvesen", "silver_traffic_volumes_vegvesen"]
)

traffic_volumes_schedule = ScheduleDefinition(
    job=traffic_volumes_job,
    cron_schedule="*/5 6-8,15-17 * * 1-5", # Rush hours: 06:00-09:00 & 15:00-18:00, Mon-Fri
    execution_timezone="Europe/Oslo",
)

weather_job = define_asset_job(
    name="bronze_weather_hourly_job",
    selection=["bronze_weather_met_frost"],
)

# Hourly Schedule
hourly_weather_schedule = ScheduleDefinition(
    job=weather_job,
    cron_schedule="0 * * * *",
    execution_timezone="Europe/Oslo",
)

# Read Environment Variables (with local fallback defaults for SeaweedFS/R2)
endpoint_url = os.getenv("R2_ENDPOINT", "http://localhost:9000")
access_key_id = os.getenv("R2_ACCESS_KEY_ID", "test")
secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY", "test")
region_name = os.getenv("R2_REGION_NAME", "auto")

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
    assets=[
        weather_frost.bronze_weather_met_frost,
        travel_times.bronze_travel_times_vegvesen,
        travel_times.silver_travel_times_vegvesen,
        traffic_volumes.bronze_traffic_volumes_vegvesen,
        traffic_volumes.silver_traffic_volumes_vegvesen,
    ],
    jobs=[
        weather_job,
        travel_times_job,
        traffic_volumes_job, 
    ],
    schedules=[
        hourly_weather_schedule,
        travel_times_schedule,
        traffic_volumes_schedule, 
    ],
    resources={
        "s3": s3_client,
        "motherduck": MotherDuckResource(),
    },
)