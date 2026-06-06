from enum import Enum
from typing import Optional

from pydantic import BaseModel


class URLType(Enum):
    DEDICATED_WEBSITE = "dedicated"
    SOCIAL_MEDIA = "social"
    DIRECTORY_LISTING = "directory"
    LINK_IN_BIO = "link_in_bio"
    NO_URL = "none"

class WebsiteStatus(BaseModel):
    is_live: bool
    final_url: Optional[str]
    status_code: Optional[int]
    url_type: URLType
    error: Optional[str] = None
