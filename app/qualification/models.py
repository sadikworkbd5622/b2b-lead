from enum import Enum

from pydantic import BaseModel


class URLType(Enum):
    DEDICATED_WEBSITE = "dedicated"
    SOCIAL_MEDIA = "social"
    DIRECTORY_LISTING = "directory"
    LINK_IN_BIO = "link_in_bio"
    NO_URL = "none"

class WebsiteStatus(BaseModel):
    is_live: bool
    final_url: str | None
    status_code: int | None
    url_type: URLType
    error: str | None = None
