import json
import sqlite3
from pathlib import Path

from .constants import SQL_FILE_DEFAULT


def extract_items(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("data", "items", "results"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
    raise ValueError("JSON must be a list or dict with data/items/results list")


def load_items(path: Path):
    if path.is_dir():
        raise IsADirectoryError(f"JSON path is a directory: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return extract_items(raw)


def to_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        return float(stripped)
    return None


def to_int(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        return int(float(stripped))
    return None


def strip_line_comments(sql_text: str) -> str:
    lines = []
    for line in sql_text.splitlines():
        if line.lstrip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def extract_last_statement(sql_text: str) -> str:
    cleaned = strip_line_comments(sql_text)
    statements = [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]
    if not statements:
        raise ValueError("SQL file has no statements")
    return statements[-1]


def prepare_db(items):
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE requests (
            id INTEGER,
            amount REAL,
            period_days INTEGER,
            interest_rate REAL,
            request_type TEXT,
            status TEXT,
            created_at TEXT,
            rating INTEGER,
            loans_count INTEGER,
            period_type TEXT,
            percent_amount REAL
        )
        """
    )
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            (
                to_int(item.get("id")),
                to_float(item.get("amount")),
                to_int(item.get("period_days")),
                to_float(item.get("interest_rate")),
                item.get("request_type"),
                item.get("status"),
                item.get("created_at"),
                to_int(item.get("rating")),
                to_int(item.get("loans_count")),
                item.get("period_type"),
                to_float(item.get("percent_amount")),
            )
        )

    conn.executemany(
        """
        INSERT INTO requests (
            id, amount, period_days, interest_rate, request_type, status,
            created_at, rating, loans_count, period_type, percent_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return conn


def load_default_sql() -> str:
    return SQL_FILE_DEFAULT.read_text(encoding="utf-8")


def run_report(conn: sqlite3.Connection, sql_text: str):
    conn.executescript(strip_line_comments(sql_text))
    final_stmt = extract_last_statement(sql_text)
    cur = conn.execute(final_stmt)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return columns, rows
