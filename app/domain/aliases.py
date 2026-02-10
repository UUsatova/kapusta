from typing import Dict


def parse_aliases(raw: str) -> Dict[str, str]:
    if not raw or not raw.strip():
        return {}

    mapping: Dict[str, str] = {}
    for pair in [item.strip() for item in raw.split(",") if item.strip()]:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            mapping[key] = value
    return mapping
