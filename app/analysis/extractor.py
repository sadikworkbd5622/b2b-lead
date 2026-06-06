import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.analysis.models import ExtractedLead
from app.analysis.prompts import EXTRACTION_SYSTEM_PROMPT
from app.discovery.models import RawBusinessData
from app.utils.logger import logger


JSON_SCHEMA_SUFFIX = """

# OUTPUT FORMAT
Respond ONLY with a valid JSON object (no markdown, no backticks) matching this schema:
{
  "lead_status": "Qualified - No Website" or "Rejected - Has Website",
  "extracted_data": {
    "business_name": "...",
    "decision_maker_name": "..." or "Not Found",
    "phone_number": "..." or "Not Found",
    "email_address": "..." or "Not Found",
    "social_media_link": "..." or "Not Found"
  },
  "confidence_score": 1-100,
  "reasoning_log": "..."
}
"""


class LeadExtractor:
    def __init__(self, api_key: str, provider: str = "openai", model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        if not api_key:
            raise ValueError(f"{provider.capitalize()} API key is required for LeadExtractor.")

        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

        if self.provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
                max_retries=3
            ).with_structured_output(ExtractedLead)
        elif self.provider == "groq":
            self.llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                api_key=api_key,
                max_retries=3
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=api_key,
                max_retries=3
            ).with_structured_output(ExtractedLead)

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("human", "Analyze this business:\nName: {name}\nCategory: {category}\nAddress: {address}\nPhone: {phone}\nWebsite: {website}\nSnippet: {raw_snippet}")
        ])

        if self.provider == "groq":
            self.json_system_prompt = EXTRACTION_SYSTEM_PROMPT + JSON_SCHEMA_SUFFIX

    def _extract_json_mode(self, business: RawBusinessData) -> ExtractedLead:
        content = (
            f"Analyze this business:\nName: {business.name or 'N/A'}\n"
            f"Category: {business.category or 'N/A'}\n"
            f"Address: {business.address or 'N/A'}\n"
            f"Phone: {business.phone or 'N/A'}\n"
            f"Website: {business.website or 'N/A'}\n"
            f"Snippet: {business.raw_snippet or 'N/A'}"
        )
        messages = [
            SystemMessage(content=self.json_system_prompt),
            HumanMessage(content=content),
        ]
        raw = self.llm.invoke(messages)
        text = raw.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        parsed = json.loads(text.strip())
        if isinstance(parsed.get("confidence_score"), str):
            parsed["confidence_score"] = int(parsed["confidence_score"])
        return ExtractedLead(**parsed)

    def extract(self, business: RawBusinessData) -> ExtractedLead:
        logger.debug(f"Extracting lead info for: {business.name}")

        try:
            if self.provider == "groq":
                return self._extract_json_mode(business)
            messages = self.prompt_template.format_messages(
                name=business.name or "N/A",
                category=business.category or "N/A",
                address=business.address or "N/A",
                phone=business.phone or "N/A",
                website=business.website or "N/A",
                raw_snippet=business.raw_snippet or "N/A"
            )
            from typing import cast
            return cast(ExtractedLead, self.llm.invoke(messages))
        except Exception as e:
            logger.error(f"Failed to extract data for {business.name}: {e}")
            return ExtractedLead(
                reasoning_log=f"LLM Extraction failed: {str(e)}. Business data preserved for later reprocessing.",
                lead_status="Unprocessed - LLM Unavailable",
                extracted_data={
                    "business_name": business.name or "Not Found",
                    "decision_maker_name": "Not Found",
                    "phone_number": business.phone or "Not Found",
                    "email_address": "Not Found",
                    "social_media_link": "Not Found"
                },
                confidence_score=1
            )
