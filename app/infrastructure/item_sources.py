from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import math
from typing import Dict, List

from app.core.api import build_query_url, fetch_json
from app.core.constants import DEFAULT_STATUS
from app.core.data import extract_items, load_items


class ItemSource:
    def load_from_file(self, json_path: str) -> List[dict]:
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError("JSON file not found")
        return load_items(path)

    def fetch_all_filtered(self, base_url: str, api_params: Dict[str, str], ignore_ssl: bool) -> List[dict]:
        params = dict(api_params)
        params.setdefault("status", DEFAULT_STATUS)
        return self._fetch_paginated(base_url, params, ignore_ssl)

    def fetch_all_unfiltered(self, base_url: str, ignore_ssl: bool) -> List[dict]:
        return self._fetch_paginated(base_url, {}, ignore_ssl)

    def _fetch_paginated(self, base_url: str, base_params: Dict[str, str], ignore_ssl: bool) -> List[dict]:
        """
        Load paginated data from API.
        Strategy:
        - page 1 request first
        - if total pages can be inferred from pagination meta, fetch remaining pages concurrently
        - otherwise fallback to sequential scan until empty page
        """
        all_items: List[dict] = []
        page_size = 100

        params = dict(base_params)
        params["page"] = "1"
        params["page_size"] = str(page_size)
        first_raw = fetch_json(build_query_url(base_url, params), verify_ssl=not ignore_ssl)
        first_items = extract_items(first_raw)
        if not first_items:
            return []

        all_items.extend(first_items)
        total_pages = self._extract_total_pages(first_raw, page_size)

        if total_pages and total_pages > 1:
            all_items.extend(self._fetch_pages_parallel(base_url, base_params, ignore_ssl, page_size, total_pages))
            return all_items

        page = 2
        while True:
            params = dict(base_params)
            params["page"] = str(page)
            params["page_size"] = str(page_size)
            url = build_query_url(base_url, params)
            raw = fetch_json(url, verify_ssl=not ignore_ssl)
            items = extract_items(raw)

            if not items:
                break

            all_items.extend(items)

            if len(items) < page_size:
                break

            page += 1
            if page > 1000:
                break

        return all_items

    def _fetch_pages_parallel(
        self,
        base_url: str,
        base_params: Dict[str, str],
        ignore_ssl: bool,
        page_size: int,
        total_pages: int,
    ) -> List[dict]:
        max_workers = min(8, max(1, total_pages - 1))
        pages = list(range(2, total_pages + 1))
        page_results: Dict[int, List[dict]] = {}

        def fetch_page(page: int) -> List[dict]:
            params = dict(base_params)
            params["page"] = str(page)
            params["page_size"] = str(page_size)
            url = build_query_url(base_url, params)
            raw = fetch_json(url, verify_ssl=not ignore_ssl)
            return extract_items(raw)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(fetch_page, page): page for page in pages}
            for future, page in futures.items():
                page_results[page] = future.result()

        ordered_items: List[dict] = []
        for page in pages:
            ordered_items.extend(page_results.get(page, []))
        return ordered_items

    @staticmethod
    def _extract_total_pages(raw: object, page_size: int) -> int | None:
        if not isinstance(raw, dict):
            return None
        pagination = raw.get("pagination")
        if not isinstance(pagination, dict):
            return None

        for key in ("total_pages", "pages", "page_count"):
            value = pagination.get(key)
            if isinstance(value, int) and value > 0:
                return value

        total_count = None
        for key in ("count", "total", "total_count", "items_count"):
            value = pagination.get(key)
            if isinstance(value, int) and value >= 0:
                total_count = value
                break

        if total_count is None:
            return None
        return max(1, math.ceil(total_count / page_size))
