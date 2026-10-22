from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StravaConnectResponse(BaseModel):
    authorization_url: str


class StravaStatusResponse(BaseModel):
    connected: bool
    athlete_id: str | None = None
    scopes: str | None = None
    connected_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StravaDisconnectResponse(BaseModel):
    connected: bool
    provider_revoked: bool
