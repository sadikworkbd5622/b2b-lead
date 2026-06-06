from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RawBusinessData(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw_snippet: Optional[str] = None
    source: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
