from abc import ABC, abstractmethod
from typing import Optional

from app.enrichment.models import EnrichmentResult


class EnrichmentSource(ABC):
    @abstractmethod
    async def enrich(self, business_name: str, domain: Optional[str] = None) -> EnrichmentResult:
        pass
