from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_JSON_DEFAULT = BASE_DIR / "700.json"
SQL_FILE_DEFAULT = BASE_DIR / "myRequest.sql"
API_BASE_DEFAULT = "https://kapusta.by/api/internal/v1/public/loans/lend_request/"
CONFIG_PATH = BASE_DIR / "kapusta_report_settings.json"
DEFAULT_STATUS = "active"

APP_TITLE = "Kapusta Report"
WINDOW_GEOMETRY = "1200x760"
WINDOW_MIN_SIZE = (980, 620)
