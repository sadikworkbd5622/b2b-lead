from abc import ABC, abstractmethod

from app.enrichment.models import EnrichmentResult


class EnrichmentSource(ABC):
    @abstractmethod
    async def enrich(self, business_name: str, domain: str | None = None) -> EnrichmentResult:
        pass
