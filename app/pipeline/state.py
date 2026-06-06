from typing import Any, TypedDict

from app.analysis.models import ExtractedLead
from app.discovery.models import RawBusinessData
from app.enrichment.models import EnrichmentResult


class PipelineState(TypedDict):
    search_queries: list[dict[str, str]]
    max_results_per_query: int
    raw_businesses: list[RawBusinessData]
    qualified_raw_businesses: list[RawBusinessData]
    extracted_leads: list[ExtractedLead]
    qualified_leads: list[ExtractedLead]
    rejected_leads: list[ExtractedLead]
    enriched_leads: list[EnrichmentResult]
    errors: list[str]
    current_step: str
    stats: dict[str, Any]
