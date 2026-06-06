
from typing import Optional

import httpx

from app.qualification.models import URLType, WebsiteStatus
from app.qualification.url_classifier import URLClassifier
from app.utils.logger import logger


class WebsiteChecker:
    def __init__(self, classifier: URLClassifier, timeout: int = 5):
        self.classifier = classifier
        self.timeout = timeout

    async def check_website(self, url: Optional[str]) -> WebsiteStatus:
        """
        Validates the website via HTTP HEAD request, following redirects.
        Returns the status and the classified type of the final URL.
        """
        initial_type = self.classifier.classify(url)

        # If no URL or already known to not be a dedicated site, skip HTTP request
        if initial_type != URLType.DEDICATED_WEBSITE:
            return WebsiteStatus(
                is_live=False,
                final_url=url,
                status_code=None,
                url_type=initial_type
            )

        # Ensure scheme
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # Add headers to mimic browser
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                logger.debug(f"Checking website: {url}")
                response = await client.head(url, headers=headers)

                # Some servers don't support HEAD correctly, fallback to GET if 405 or 403
                if response.status_code in [403, 405]:
                    response = await client.get(url, headers=headers)

                final_url = str(response.url)
                final_type = self.classifier.classify(final_url)

                is_live = response.status_code == 200

                return WebsiteStatus(
                    is_live=is_live,
                    final_url=final_url,
                    status_code=response.status_code,
                    url_type=final_type
                )

        except httpx.RequestError as e:
            logger.debug(f"Request error for {url}: {e}")
            return WebsiteStatus(
                is_live=False,
                final_url=url,
                status_code=None,
                url_type=initial_type,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error checking {url}: {e}")
            return WebsiteStatus(
                is_live=False,
                final_url=url,
                status_code=None,
                url_type=initial_type,
                error="Unexpected error"
            )
