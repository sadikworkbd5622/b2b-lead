from typing import Literal

from pydantic import BaseModel, Field


class ExtractedData(BaseModel):
    business_name: str = "Not Found"
    decision_maker_name: str = "Not Found"
    phone_number: str = "Not Found"
    email_address: str = "Not Found"
    social_media_link: str = "Not Found"

class ExtractedLead(BaseModel):
    reasoning_log: str = Field(description="Briefly explain why this business was qualified or rejected, specifically noting your analysis of their web presence.")
    lead_status: Literal["Qualified - No Website", "Rejected - Has Website"]
    extracted_data: ExtractedData
    confidence_score: int = Field(ge=1, le=100)
