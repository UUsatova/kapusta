from typing import Dict, List

from app.core.data import load_default_sql, prepare_db, run_report


class ReportRepository:
    def run_report_for_items(self, items: List[dict]) -> Dict[str, object]:
        conn = prepare_db(items)
        sql_text = load_default_sql()
        columns, rows = run_report(conn, sql_text)
        conn.close()
        return {
            "columns": columns,
            "rows": rows,
            "rows_count": len(rows),
        }
