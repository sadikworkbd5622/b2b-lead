from datetime import datetime

from pydantic import BaseModel, Field


class RawBusinessData(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw_snippet: str | None = None
    source: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
