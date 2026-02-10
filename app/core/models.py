from dataclasses import dataclass
from typing import Dict


def _to_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off", ""):
            return False
    return bool(value)


@dataclass
class ApiParams:
    amount_min: str = "500"
    amount_max: str = "500"
    period_days_min: str = "30"
    period_days_max: str = "30"
    rating_min: str = "45"
    rating_max: str = "45"

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        values = {field: data.get(field, getattr(cls(), field)) for field in cls.__annotations__}
        return cls(**values)

    def to_dict(self) -> Dict[str, str]:
        return {field: getattr(self, field) for field in self.__annotations__}


@dataclass
class AppConfig:
    json_path: str
    api_base_url: str
    aliases: str
    ignore_ssl: bool
    api_params: ApiParams

    @classmethod
    def from_dict(cls, data: Dict[str, str], defaults: "AppConfig"):
        api_params = ApiParams.from_dict(data.get("api_params", {}))
        return cls(
            json_path=data.get("json_path", defaults.json_path),
            api_base_url=data.get("api_base_url", defaults.api_base_url),
            aliases=data.get("aliases", defaults.aliases),
            ignore_ssl=_to_bool(data.get("ignore_ssl", defaults.ignore_ssl), defaults.ignore_ssl),
            api_params=api_params,
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "json_path": self.json_path,
            "api_base_url": self.api_base_url,
            "aliases": self.aliases,
            "ignore_ssl": self.ignore_ssl,
            "api_params": self.api_params.to_dict(),
        }
