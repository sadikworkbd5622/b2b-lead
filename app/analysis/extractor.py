from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.analysis.models import ExtractedLead
from app.analysis.prompts import EXTRACTION_SYSTEM_PROMPT
from app.discovery.models import RawBusinessData
from app.utils.logger import logger


class LeadExtractor:
    def __init__(self, api_key: str, provider: str = "openai", model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        if not api_key:
            raise ValueError(f"{provider.capitalize()} API key is required for LeadExtractor.")

        provider = provider.lower()
        if provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=api_key,
                max_retries=3
            ).with_structured_output(ExtractedLead)
        elif provider == "groq":
            self.llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                api_key=api_key,
                max_retries=3
            ).with_structured_output(ExtractedLead)
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

    def extract(self, business: RawBusinessData) -> ExtractedLead:
        logger.debug(f"Extracting lead info for: {business.name}")

        messages = self.prompt_template.format_messages(
            name=business.name or "N/A",
            category=business.category or "N/A",
            address=business.address or "N/A",
            phone=business.phone or "N/A",
            website=business.website or "N/A",
            raw_snippet=business.raw_snippet or "N/A"
        )

        try:
            from typing import cast
            result = cast(ExtractedLead, self.llm.invoke(messages))
            return result
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
