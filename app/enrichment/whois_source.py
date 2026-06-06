import asyncio
from typing import Optional

from app.enrichment.base import EnrichmentSource
from app.enrichment.models import EnrichmentResult
from app.utils.logger import logger


class WhoisEnrichment(EnrichmentSource):
    """Uses whois domain lookup to find registrant info. No API key needed."""

    async def enrich(self, business_name: str, domain: Optional[str] = None) -> EnrichmentResult:
        if not domain:
            return EnrichmentResult(
                business_name=business_name, source="whois",
                error="No domain provided"
            )

        try:
            proc = await asyncio.create_subprocess_exec(
                "whois", domain,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            text = stdout.decode("utf-8", errors="ignore").lower()

            registrant = None
            email = None
            phone = None

            for line in text.split("\n"):
                if "registrant name:" in line:
                    registrant = line.split(":", 1)[1].strip()
                elif "registrant email:" in line or "admin email:" in line:
                    email = line.split(":", 1)[1].strip()
                elif "registrant phone:" in line:
                    phone = line.split(":", 1)[1].strip()

            confidence = 0
            if registrant:
                confidence += 30
            if email:
                confidence += 40
            if phone:
                confidence += 30

            return EnrichmentResult(
                business_name=business_name,
                domain=domain,
                decision_maker_name=registrant,
                email_address=email,
                phone_number=phone,
                confidence=min(confidence, 100),
                source="whois"
            )
        except FileNotFoundError:
            return EnrichmentResult(
                business_name=business_name, domain=domain,
                source="whois", error="whois command not found on system"
            )
        except asyncio.TimeoutError:
            return EnrichmentResult(
                business_name=business_name, domain=domain,
                source="whois", error="whois lookup timed out"
            )
        except Exception as e:
            logger.debug(f"Whois error for {domain}: {e}")
            return EnrichmentResult(
                business_name=business_name, domain=domain,
                source="whois", error=str(e)
            )
