from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    company_email: EmailStr | None = None


class UserCreate(UserBase):
    company_id: int | None = None


class UserResponse(UserBase):
    id: int
    verified_company: bool
    company_id: int | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)