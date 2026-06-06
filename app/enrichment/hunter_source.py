
import httpx

from app.enrichment.base import EnrichmentSource
from app.enrichment.models import EnrichmentResult
from app.utils.logger import logger


class HunterEnrichment(EnrichmentSource):
    def __init__(self, api_key: str):
        if not api_key:
            logger.warning("Hunter API key not set — enrichment will return empty results")
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"

    async def enrich(self, business_name: str, domain: str | None = None) -> EnrichmentResult:
        if not self.api_key or not domain:
            return EnrichmentResult(
                business_name=business_name,
                source="hunter",
                error="No API key or domain provided"
            )

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/domain-search",
                    params={"domain": domain, "api_key": self.api_key}
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})

                emails = data.get("emails", [])
                email = emails[0]["value"] if emails else None

                return EnrichmentResult(
                    business_name=business_name,
                    domain=domain,
                    email_address=email,
                    decision_maker_name=self._find_decision_maker(emails),
                    confidence=len(emails) * 20 if emails else 0,
                    source="hunter"
                )
        except httpx.RequestError as e:
            logger.debug(f"Hunter API error for {domain}: {e}")
            return EnrichmentResult(
                business_name=business_name,
                domain=domain,
                source="hunter",
                error=str(e)
            )

    def _find_decision_maker(self, emails: list) -> str | None:
        priority = ["ceo", "owner", "founder", "president", "director", "manager"]
        for email in emails:
            position = (email.get("position") or "").lower()
            for keyword in priority:
                if keyword in position:
                    return email.get("first_name", "") + " " + email.get("last_name", "")
        return emails[0].get("first_name", "") + " " + emails[0].get("last_name", "") if emails else None
