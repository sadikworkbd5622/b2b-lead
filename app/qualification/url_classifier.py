import urllib.parse
from typing import Optional

from app.qualification.models import URLType


class URLClassifier:
    def __init__(self, non_website_domains: list[str]):
        # Normalize domains to lowercase
        self.non_website_domains = [domain.lower() for domain in non_website_domains]

    def classify(self, url: Optional[str]) -> URLType:
        if not url or not url.strip():
            return URLType.NO_URL

        # Ensure url has scheme for accurate parsing
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()

            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]

            for non_website in self.non_website_domains:
                if domain == non_website or domain.endswith("." + non_website):
                    # We could further split SOCIAL vs DIRECTORY based on the list,
                    # but per requirements, all are "Qualified" (no dedicated site).
                    # Let's map it simply here or expand if needed.
                    if any(s in non_website for s in ["facebook", "instagram", "twitter", "x", "tiktok"]):
                        return URLType.SOCIAL_MEDIA
                    if any(s in non_website for s in ["linktr"]):
                        return URLType.LINK_IN_BIO
                    return URLType.DIRECTORY_LISTING

            return URLType.DEDICATED_WEBSITE

        except Exception:
            return URLType.NO_URL
