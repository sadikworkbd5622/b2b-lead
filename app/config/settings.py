
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SearchQuery(BaseModel):
    query: str
    location: str


class SearchConfig(BaseModel):
    queries: list[SearchQuery]
    max_results_per_query: int = 20
    delay_between_requests: float = 2.0
    fuzzy_dedup_threshold: float = 0.0


class ApiConfig(BaseModel):
    provider: str = "serpapi"


class QualificationConfig(BaseModel):
    non_website_domains: list[str]
    website_check_timeout: int = 5


class LlmConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_retries: int = 3


class CacheConfig(BaseModel):
    enabled: bool = True
    ttl_hours: int = 24
    cache_dir: str = "data/cache"


class EnrichmentConfig(BaseModel):
    enabled: bool = False
    provider: str = "hunter"
    api_key_env: str = "HUNTER_API_KEY"


class ExportConfig(BaseModel):
    formats: list[str] = ["json", "csv"]
    output_dir: str = "data/exports"


class Settings(BaseSettings):
    search: SearchConfig
    api: ApiConfig
    qualification: QualificationConfig
    llm: LlmConfig
    cache: CacheConfig = CacheConfig()
    enrichment: EnrichmentConfig = EnrichmentConfig()
    export: ExportConfig

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    serpapi_api_key: Optional[str] = Field(default=None, alias="SERPAPI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    hunter_api_key: Optional[str] = Field(default=None, alias="HUNTER_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
