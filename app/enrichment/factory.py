from typing import Optional

from app.config.settings import Settings
from app.enrichment.base import EnrichmentSource
from app.enrichment.hunter_source import HunterEnrichment
from app.enrichment.llm_source import LLMEnrichment
from app.enrichment.whois_source import WhoisEnrichment
from app.utils.logger import logger


def get_enricher(settings: Settings) -> Optional[EnrichmentSource]:
    provider = settings.enrichment.provider.lower()
    llm_key = settings.gemini_api_key or settings.openai_api_key
    llm_provider = settings.llm.provider

    if provider == "hunter":
        logger.info("Enrichment: using Hunter.io API")
        return HunterEnrichment(api_key=settings.hunter_api_key or "")

    elif provider == "whois":
        logger.info("Enrichment: using whois domain lookup (no API key needed)")
        return WhoisEnrichment()

    elif provider == "llm":
        logger.info(f"Enrichment: using LLM ({llm_provider})")
        return LLMEnrichment(
            api_key=llm_key or "",
            provider=llm_provider,
            model_name=settings.llm.model
        )

    else:
        logger.warning(f"Unknown enrichment provider: {provider}, falling back to LLM")
        return LLMEnrichment(
            api_key=llm_key or "",
            provider=llm_provider,
            model_name=settings.llm.model
        )
