
from pydantic import BaseModel, Field


class EnrichmentResult(BaseModel):
    business_name: str
    domain: str | None = None
    decision_maker_name: str | None = None
    decision_maker_title: str | None = None
    email_address: str | None = None
    phone_number: str | None = None
    linkedin_url: str | None = None
    confidence: int = Field(default=0, ge=0, le=100)
    source: str = "unknown"
    error: str | None = None
