from typing import Dict, Optional

from app.domain.aliases import parse_aliases
from app.domain.calculator import calculate_values
from app.domain.statistics import build_amount_stats
from app.infrastructure.item_sources import ItemSource
from app.infrastructure.report_repository import ReportRepository


class ReportUseCases:
    def __init__(self, item_source: ItemSource, report_repository: ReportRepository):
        self.item_source = item_source
        self.report_repository = report_repository

    def calculate(self, amount_raw: str, rate_raw: str, period_raw: str) -> Dict[str, str]:
        return calculate_values(amount_raw, rate_raw, period_raw)

    def build_table_from_file(self, json_path: str, aliases_raw: str) -> Dict[str, object]:
        items = self.item_source.load_from_file(json_path)
        report = self.report_repository.run_report_for_items(items)
        return self._apply_aliases(report, aliases_raw)

    def build_table_from_api(
        self,
        base_url: str,
        api_params: Dict[str, str],
        ignore_ssl: bool,
        aliases_raw: str,
    ) -> Dict[str, object]:
        items = self.item_source.fetch_all_filtered(base_url, api_params, ignore_ssl)
        report = self.report_repository.run_report_for_items(items)
        return self._apply_aliases(report, aliases_raw)

    def build_amount_distribution(
        self,
        base_url: str,
        ignore_ssl: bool,
        min_amount_count: Optional[int],
        max_amount_count: Optional[int],
    ) -> Dict[str, object]:
        items = self.item_source.fetch_all_unfiltered(base_url, ignore_ssl)
        return build_amount_stats(
            items,
            min_amount_count=min_amount_count,
            max_amount_count=max_amount_count,
        )

    @staticmethod
    def _apply_aliases(report: Dict[str, object], aliases_raw: str) -> Dict[str, object]:
        aliases = parse_aliases(aliases_raw)
        columns = report["columns"]
        return {
            "columns": columns,
            "headers": [aliases.get(col, col) for col in columns],
            "rows": report["rows"],
            "rows_count": report["rows_count"],
        }
