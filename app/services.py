from pathlib import Path
from typing import Dict, List

from app.core.api import build_query_url, fetch_json
from app.core.constants import DEFAULT_STATUS
from app.core.data import extract_items, load_default_sql, load_items, prepare_db, run_report


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


def calculate_values(amount_raw: str, rate_raw: str, period_raw: str) -> Dict[str, str]:
    def parse_float(value: str):
        try:
            return float((value or "").replace(",", "."))
        except ValueError:
            return None

    amount = parse_float(amount_raw)
    rate = parse_float(rate_raw)
    period = parse_float(period_raw)

    if amount is None or rate is None or period is None or period == 0:
        return {
            "income_with_commission": "-",
            "income_without_commission": "-",
            "real_annual_yield": "-",
        }

    percent_amount = amount * (rate / 100.0) * (period / 365.0)
    income_with_commission = amount + percent_amount
    income_without_commission = income_with_commission * 0.955
    real_annual_yield = ((income_without_commission - amount) / amount) * (365.0 / period) * 100.0

    return {
        "income_with_commission": f"{income_with_commission:.2f}",
        "income_without_commission": f"{income_without_commission:.2f}",
        "real_annual_yield": f"{real_annual_yield:.2f}%",
    }


def load_items_from_file(json_path: str):
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError("JSON file not found")
    return load_items(path)


def fetch_all_pages(base_url: str, api_params: Dict[str, str], ignore_ssl: bool) -> List[dict]:
    all_items: List[dict] = []
    page = 1
    page_size = 100

    while True:
        params = dict(api_params)
        params.setdefault("status", DEFAULT_STATUS)
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


def build_report(items, aliases_raw: str) -> Dict[str, object]:
    conn = prepare_db(items)
    sql_text = load_default_sql()
    columns, rows = run_report(conn, sql_text)
    conn.close()

    aliases = parse_aliases(aliases_raw)
    rendered_columns = [aliases.get(col, col) for col in columns]

    return {
        "columns": columns,
        "headers": rendered_columns,
        "rows": rows,
        "rows_count": len(rows),
    }
