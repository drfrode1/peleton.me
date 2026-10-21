from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    org_number: str
    name: str
    postal_code: str | None = None
    company_type: str | None = None
    company_category: str | None = None
    show_name_consent: bool = False


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CompanySearchItem(BaseModel):
    org_number: str
    name: str
    postal_code: str | None = None
    company_type: str | None = None
    company_category: str | None = None


class CompanySearchResponse(BaseModel):
    results: list[CompanySearchItem]