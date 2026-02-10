from typing import Dict, Optional


def _parse_float(value: str) -> Optional[float]:
    try:
        return float((value or "").replace(",", "."))
    except ValueError:
        return None


def calculate_values(amount_raw: str, rate_raw: str, period_raw: str) -> Dict[str, str]:
    amount = _parse_float(amount_raw)
    rate = _parse_float(rate_raw)
    period = _parse_float(period_raw)

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
