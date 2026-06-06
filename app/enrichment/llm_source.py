from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.enrichment.base import EnrichmentSource
from app.enrichment.models import EnrichmentResult
from app.utils.logger import logger

ENRICHMENT_PROMPT = """You are a B2B data enrichment assistant. Given a business name and domain, infer the most likely contact information.

Be honest — if you cannot determine something, output "Not Found".

Business Name: {business_name}
Domain: {domain}

Output as JSON:
{{
  "decision_maker_name": "likely owner/founder name or Not Found",
  "email_address": "likely business email pattern (e.g. info@domain.com) or Not Found",
  "confidence": 0-100 based on how certain you are
}}"""


class LLMEnrichment(EnrichmentSource):
    """Uses existing Gemini/OpenAI key to infer contact info from business name + domain."""

    def __init__(self, api_key: str, provider: str = "gemini", model_name: str = "gemini-1.5-flash"):
        if not api_key:
            logger.warning("LLM API key not set — enrichment will return empty results")
            self.llm = None
            return

        if provider.lower() == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model_name, temperature=0.1, google_api_key=api_key
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name, temperature=0.1, api_key=api_key
            )

        self.prompt = ChatPromptTemplate.from_messages([("system", ENRICHMENT_PROMPT)])

    async def enrich(self, business_name: str, domain: Optional[str] = None) -> EnrichmentResult:
        if not self.llm:
            return EnrichmentResult(
                business_name=business_name, source="llm",
                error="No LLM API key configured"
            )

        if not domain:
            return EnrichmentResult(
                business_name=business_name, source="llm",
                error="No domain provided"
            )

        try:
            messages = self.prompt.format_messages(
                business_name=business_name, domain=domain
            )
            result = self.llm.invoke(messages)
            import json
            import re

            text = result.content if hasattr(result, "content") else str(result)
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                return EnrichmentResult(
                    business_name=business_name, domain=domain,
                    source="llm", error="LLM output was not valid JSON",
                    confidence=0
                )

            data = json.loads(json_match.group())

            return EnrichmentResult(
                business_name=business_name,
                domain=domain,
                decision_maker_name=data.get("decision_maker_name", "Not Found"),
                email_address=data.get("email_address", "Not Found"),
                confidence=int(data.get("confidence", 0)),
                source="llm"
            )
        except Exception as e:
            logger.debug(f"LLM enrichment error for {domain}: {e}")
            return EnrichmentResult(
                business_name=business_name, domain=domain,
                source="llm", error=str(e)
            )
