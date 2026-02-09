import json
from .constants import CONFIG_PATH
from .models import AppConfig, ApiParams


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(data: dict):
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_app_config(defaults: AppConfig) -> AppConfig:
    raw = load_config()
    return AppConfig.from_dict(raw, defaults)


def save_app_config(config: AppConfig):
    save_config(config.to_dict())
