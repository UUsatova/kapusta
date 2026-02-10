from pathlib import Path
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
        all_items: List[dict] = []
        page = 1
        page_size = 100

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
