import hashlib
import json
import os
import time
from datetime import datetime, timedelta

import requests

from app.discovery.base import DataSource
from app.discovery.models import RawBusinessData
from app.utils.logger import logger


class SerpApiSource(DataSource):
    def __init__(
        self,
        api_key: str,
        delay_between_requests: float = 2.0,
        cache_enabled: bool = True,
        cache_dir: str = "data/cache",
        cache_ttl_hours: int = 24,
        max_retries: int = 3,
        base_delay: float = 1.0
    ):
        if not api_key:
            raise ValueError("SerpAPI API key is required.")
        self.api_key = api_key
        self.delay = delay_between_requests
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.base_url = "https://serpapi.com/search.json"

        if self.cache_enabled:
            os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_key(self, query: str, location: str, page: int) -> str:
        raw = f"{query}|{location}|{page}".encode()
        return hashlib.md5(raw).hexdigest()

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def _load_from_cache(self, key: str) -> list | None:
        path = self._cache_path(key)
        if not os.path.exists(path):
            return None
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if datetime.now() - mtime > self.cache_ttl:
            os.remove(path)
            return None
        with open(path) as f:
            return json.load(f)

    def _save_to_cache(self, key: str, data: list):
        path = self._cache_path(key)
        with open(path, "w") as f:
            json.dump(data, f, default=str)

    def _request_with_retry(self, params: dict) -> dict:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                last_exception = e
                logger.warning(
                    f"SerpAPI request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    sleep_time = self.base_delay * (2 ** attempt)
                    time.sleep(sleep_time)
        raise last_exception

    def search(self, query: str, location: str, max_results: int = 20) -> list[RawBusinessData]:
        results: list[RawBusinessData] = []
        page = 0
        full_query = f"{query} in {location}"

        while len(results) < max_results:
            cache_key = self._cache_key(full_query, location, page)
            cached = self._load_from_cache(cache_key) if self.cache_enabled else None

            if cached is not None:
                logger.info(f"Cache hit for '{full_query}' page {page}")
                local_results = cached
            else:
                params = {
                    "engine": "google_maps",
                    "q": full_query,
                    "type": "search",
                    "api_key": self.api_key,
                    "start": page * 20
                }

                logger.info(f"Fetching SerpAPI for '{full_query}' (start={params['start']})...")
                data = self._request_with_retry(params)
                local_results = data.get("local_results", [])

                if self.cache_enabled:
                    self._save_to_cache(cache_key, local_results)

            if not local_results:
                logger.info("No more local results found.")
                break

            for place in local_results:
                if len(results) >= max_results:
                    break
                gps = place.get("gps_coordinates", {})
                business = RawBusinessData(
                    name=place.get("title", "Unknown"),
                    address=place.get("address"),
                    phone=place.get("phone"),
                    website=place.get("website"),
                    rating=place.get("rating"),
                    reviews_count=place.get("reviews"),
                    category=place.get("type"),
                    latitude=gps.get("latitude"),
                    longitude=gps.get("longitude"),
                    raw_snippet=place.get("description"),
                    source="serpapi"
                )
                results.append(business)

            if cached is not None:
                break

            page += 1
            time.sleep(self.delay)

        return results
