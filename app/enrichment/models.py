
from typing import Optional

from pydantic import BaseModel, Field


class EnrichmentResult(BaseModel):
    business_name: str
    domain: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_title: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    confidence: int = Field(default=0, ge=0, le=100)
    source: str = "unknown"
    error: Optional[str] = None
