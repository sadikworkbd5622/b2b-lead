import asyncio
import difflib
from typing import Any

from app.analysis.extractor import LeadExtractor
from app.analysis.models import ExtractedLead
from app.config.settings import Settings
from app.discovery.models import RawBusinessData
from app.discovery.serpapi_source import SerpApiSource
from app.enrichment.factory import get_enricher
from app.pipeline.state import PipelineState
from app.qualification.models import URLType
from app.qualification.url_classifier import URLClassifier
from app.qualification.website_checker import WebsiteChecker
from app.utils.logger import logger


def _dedup_key(b: RawBusinessData) -> str:
    website = (b.website or "").strip().lower().rstrip("/")
    phone = (b.phone or "").strip()
    return phone or website or b.name.strip().lower()


def _cheap_classify(business: RawBusinessData) -> bool:
    name = (business.name or "").lower()
    snippet = (business.raw_snippet or "").lower()
    combined = name + " " + snippet
    reject_signals = [
        "corporate", "chain", "franchise", "headquarters",
        "llc", "inc.", "corporation", "ltd", "plc",
        "national", "global", "worldwide"
    ]
    for signal in reject_signals:
        if signal in combined:
            return False
    return True


def _fuzzy_dedup(businesses: list[RawBusinessData], threshold: float = 0.85) -> list[RawBusinessData]:
    if not threshold or not businesses:
        return businesses
    kept = []
    for b in businesses:
        name = (b.name or "").strip().lower()
        if not name:
            kept.append(b)
            continue
        is_dup = False
        for existing in kept:
            existing_name = (existing.name or "").strip().lower()
            if not existing_name:
                continue
            ratio = difflib.SequenceMatcher(None, name, existing_name).ratio()
            if ratio >= threshold:
                is_dup = True
                existing_has = bool(existing.phone or existing.website)
                b_has = bool(b.phone or b.website)
                if b_has and not existing_has:
                    kept.remove(existing)
                    kept.append(b)
                break
        if not is_dup:
            kept.append(b)
    removed = len(businesses) - len(kept)
    if removed:
        logger.info(f"Fuzzy dedup: removed {removed} near-duplicate(s) (threshold={threshold})")
    return kept


class PipelineNodes:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.discovery_source = SerpApiSource(
            api_key=settings.serpapi_api_key or "",
            delay_between_requests=settings.search.delay_between_requests,
            cache_enabled=settings.cache.enabled,
            cache_dir=settings.cache.cache_dir,
            cache_ttl_hours=settings.cache.ttl_hours
        )

        provider = settings.llm.provider.lower()
        if provider == "gemini":
            llm_key = settings.gemini_api_key
        elif provider == "groq":
            llm_key = settings.groq_api_key
        else:
            llm_key = settings.openai_api_key

        self.extractor = LeadExtractor(
            api_key=llm_key or "",
            provider=settings.llm.provider,
            model_name=settings.llm.model,
            temperature=settings.llm.temperature
        )

        classifier = URLClassifier(non_website_domains=settings.qualification.non_website_domains)
        self.checker = WebsiteChecker(
            classifier=classifier,
            timeout=settings.qualification.website_check_timeout
        )

        self.enricher = get_enricher(settings)

    def discover_node(self, state: PipelineState) -> dict[str, Any]:
        logger.info("--- DISCOVERY NODE ---")
        raw_businesses = []
        errors = list(state.get("errors", []))
        stats = dict(state.get("stats", {}))

        for sq in state["search_queries"]:
            try:
                results = self.discovery_source.search(
                    query=sq["query"],
                    location=sq["location"],
                    max_results=state["max_results_per_query"]
                )
                raw_businesses.extend(results)
            except Exception as e:
                err_msg = f"Discovery failed for {sq}: {str(e)}"
                logger.error(err_msg)
                errors.append(err_msg)

        stats["discovered_count"] = len(raw_businesses)
        return {
            "raw_businesses": raw_businesses,
            "errors": errors,
            "current_step": "discovery_complete",
            "stats": stats
        }

    def dedup_node(self, state: PipelineState) -> dict[str, Any]:
        logger.info("--- DEDUP NODE ---")
        stats = dict(state.get("stats", {}))
        raw = state.get("raw_businesses", [])
        seen = set()
        unique = []
        for b in raw:
            key = _dedup_key(b)
            if key and key not in seen:
                seen.add(key)
                unique.append(b)

        stats["exact_duplicates_removed"] = len(raw) - len(unique)
        logger.info(f"Exact dedup: {len(raw)} -> {len(unique)} ({stats['exact_duplicates_removed']} duplicates removed)")

        threshold = self.settings.search.fuzzy_dedup_threshold
        if threshold:
            unique = _fuzzy_dedup(unique, threshold)

        stats["after_dedup"] = len(unique)
        return {
            "raw_businesses": unique,
            "stats": stats
        }

    def qualify_node(self, state: PipelineState) -> dict[str, Any]:
        logger.info("--- QUALIFICATION NODE ---")
        stats = dict(state.get("stats", {}))
        raw_businesses = state.get("raw_businesses", [])
        if not raw_businesses:
            return {"current_step": "qualification_complete", "stats": stats}

        async def _run():
            qualified = []
            rejected = []
            tasks = [self.checker.check_website(b.website) for b in raw_businesses]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            from app.qualification.models import WebsiteStatus
            for business, raw_status in zip(raw_businesses, results):
                if isinstance(raw_status, BaseException):
                    logger.warning(f"Website check failed for {business.name}: {raw_status}")
                    rejected.append(business)
                    continue

                status: WebsiteStatus = raw_status
                if status.url_type == URLType.DEDICATED_WEBSITE and status.is_live:
                    rejected.append(business)
                else:
                    qualified.append(business)

            return {"qualified": qualified, "rejected": rejected}

        results = asyncio.run(_run())

        stats["qualified_at_qualify"] = len(results["qualified"])
        stats["rejected_at_qualify"] = len(results["rejected"])
        return {
            "raw_businesses": results["qualified"],
            "qualified_raw_businesses": results["qualified"],
            "current_step": "qualification_complete",
            "stats": stats
        }

    def analyze_node(self, state: PipelineState) -> dict[str, Any]:
        logger.info("--- ANALYSIS NODE ---")
        stats = dict(state.get("stats", {}))
        extracted = []
        errors = list(state.get("errors", []))
        businesses = state.get("raw_businesses", [])

        for b in businesses:
            if not _cheap_classify(b):
                logger.debug(f"Cheap reject: {b.name}")
                extracted.append(ExtractedLead(
                    reasoning_log="Rejected by cheap pre-classifier (chain/corporate signal)",
                    lead_status="Rejected - Has Website",
                    extracted_data={
                        "business_name": b.name or "Not Found",
                        "decision_maker_name": "Not Found",
                        "phone_number": b.phone or "Not Found",
                        "email_address": "Not Found",
                        "social_media_link": "Not Found"
                    },
                    confidence_score=1
                ))
                continue

            try:
                import time
                time.sleep(4.1) # Delay to respect Gemini's free tier limit of 15 requests/minute
                lead = self.extractor.extract(b)
                extracted.append(lead)
            except Exception as e:
                errors.append(f"Extraction failed for {b.name}: {str(e)}")

        qualified_leads = []
        rejected_leads = []
        unprocessed_leads = []
        for lead in extracted:
            if lead.lead_status == "Unprocessed - LLM Unavailable":
                unprocessed_leads.append(lead)
            elif "Qualified" in lead.lead_status:
                qualified_leads.append(lead)
            else:
                rejected_leads.append(lead)

        stats["llm_extracted"] = len(extracted)
        stats["qualified_after_llm"] = len(qualified_leads)
        stats["rejected_after_llm"] = len(rejected_leads)
        stats["unprocessed_after_llm"] = len(unprocessed_leads)
        return {
            "extracted_leads": extracted,
            "qualified_leads": qualified_leads,
            "rejected_leads": rejected_leads,
            "errors": errors,
            "current_step": "analysis_complete",
            "stats": stats
        }

    def enrich_node(self, state: PipelineState) -> dict[str, Any]:
        logger.info("--- ENRICHMENT NODE ---")
        stats = dict(state.get("stats", {}))

        if not self.enricher:
            logger.info("No enricher configured. Skipping enrichment.")
            return {
                "enriched_leads": [],
                "current_step": "enrichment_complete",
                "stats": stats
            }

        async def _run():
            tasks = []
            for lead in state.get("qualified_leads", []):
                domain = None
                if lead.extracted_data.email_address and "@" in lead.extracted_data.email_address:
                    domain = lead.extracted_data.email_address.split("@")[1]
                tasks.append(
                    self.enricher.enrich(
                        business_name=lead.extracted_data.business_name,
                        domain=domain
                    )
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            enriched = []
            for r in results:
                if isinstance(r, Exception):
                    logger.warning(f"Enrichment error: {r}")
                    continue
                enriched.append(r)
            return enriched

        enriched = asyncio.run(_run())
        stats["enriched_count"] = len(enriched)
        logger.info(f"Enriched {len(enriched)} leads")
        return {
            "enriched_leads": enriched,
            "current_step": "enrichment_complete",
            "stats": stats
        }
