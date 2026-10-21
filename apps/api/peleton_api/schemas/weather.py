from datetime import datetime

from pydantic import BaseModel


class WeatherObservationItem(BaseModel):
    location_id: str
    reference_time: datetime | str
    element_id: str
    value: float
    unit: str
    ingested_at: datetime | str


class WeatherObservationResponse(BaseModel):
    location_id: str
    count: int
    total_records: int
    items: list[WeatherObservationItem]