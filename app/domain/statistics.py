from collections import Counter, defaultdict
from typing import Dict, List, Optional, Union

PERIOD_BUCKETS = [10, 20, 30, 40, 60]
OTHER_BUCKET = "other"


def _parse_amount(item: dict) -> Optional[float]:
    value = item.get("amount")
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None


def _parse_period_days(item: dict) -> Optional[int]:
    value = item.get("period_days")
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def _parse_rating(item: dict) -> Optional[float]:
    value = item.get("rating")
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def _bucket_period_days(period_days: int) -> Union[int, str]:
    if period_days in PERIOD_BUCKETS:
        return period_days
    return OTHER_BUCKET


def _filter_amounts(
    sorted_amounts: List[float],
    amount_totals: Counter,
    min_amount_count: Optional[int],
    max_amount_count: Optional[int],
) -> List[float]:
    filtered = sorted_amounts
    if min_amount_count is not None:
        filtered = [amount for amount in filtered if amount_totals[amount] >= min_amount_count]
    if max_amount_count is not None:
        filtered = [amount for amount in filtered if amount_totals[amount] <= max_amount_count]
    return filtered


def build_amount_stats(
    items: List[dict],
    min_amount_count: Optional[int] = None,
    max_amount_count: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> Dict[str, object]:
    amount_totals: Counter = Counter()
    amount_period_counts = defaultdict(Counter)

    for item in items:
        if not isinstance(item, dict):
            continue

        amount = _parse_amount(item)
        period_days = _parse_period_days(item)
        rating = _parse_rating(item)
        if amount is None or period_days is None:
            continue
        if min_rating is not None:
            if rating is None or rating <= min_rating:
                continue

        bucket = _bucket_period_days(period_days)
        amount_totals[amount] += 1
        amount_period_counts[bucket][amount] += 1

    sorted_amounts = sorted(amount_totals.keys())
    sorted_amounts = _filter_amounts(sorted_amounts, amount_totals, min_amount_count, max_amount_count)

    period_keys: List[Union[int, str]] = [key for key in PERIOD_BUCKETS if key in amount_period_counts]
    if OTHER_BUCKET in amount_period_counts:
        period_keys.append(OTHER_BUCKET)

    labels = [f"{amount:.2f}" for amount in sorted_amounts]
    datasets = []

    for period_key in period_keys:
        counts_for_period = amount_period_counts[period_key]
        datasets.append(
            {
                "label": str(period_key),
                "data": [counts_for_period.get(amount, 0) for amount in sorted_amounts],
            }
        )

    return {
        "labels": labels,
        "datasets": datasets,
        "total_records": sum(amount_totals[amount] for amount in sorted_amounts),
    }
