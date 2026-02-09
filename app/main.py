from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.constants import API_BASE_DEFAULT, DATA_JSON_DEFAULT
from app.core.models import ApiParams, AppConfig
from app.core.settings import load_app_config, save_app_config
from app.services import build_report, calculate_values, fetch_all_pages, load_items_from_file

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Kapusta Web Report")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class AppState:
    def __init__(self):
        self.report = {"columns": [], "headers": [], "rows": [], "rows_count": 0}
        self.status = "Выберите источник данных и загрузите таблицу."


state = AppState()


def _default_config() -> AppConfig:
    return AppConfig(
        json_path=str(DATA_JSON_DEFAULT),
        api_base_url=API_BASE_DEFAULT,
        aliases="",
        ignore_ssl=False,
        api_params=ApiParams(),
    )


def _view_context(request: Request):
    cfg = load_app_config(_default_config())
    calculator = calculate_values("500", "700", "30")
    return {
        "request": request,
        "config": cfg,
        "api_params": cfg.api_params.to_dict(),
        "calculator": calculator,
        "report": state.report,
        "status": state.status,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", _view_context(request))


@app.post("/actions/calc", response_class=HTMLResponse)
def calc_partial(
    request: Request,
    calc_amount: str = Form(""),
    calc_rate: str = Form(""),
    calc_period: str = Form(""),
):
    result = calculate_values(calc_amount, calc_rate, calc_period)
    return templates.TemplateResponse(
        "partials/calc_result.html",
        {
            "request": request,
            "calculator": result,
        },
    )


@app.post("/actions/load-file", response_class=HTMLResponse)
def load_file(
    request: Request,
    json_path: str = Form(""),
):
    cfg = load_app_config(_default_config())
    cfg.json_path = json_path or cfg.json_path
    save_app_config(cfg)

    try:
        items = load_items_from_file(cfg.json_path)
        state.report = build_report(items, cfg.aliases)
        state.status = f"Строк: {state.report['rows_count']}"
    except Exception as exc:
        state.status = f"Ошибка: {exc}"

    return templates.TemplateResponse(
        "partials/table_container.html",
        {
            "request": request,
            "report": state.report,
            "status": state.status,
        },
    )


@app.post("/actions/load-api", response_class=HTMLResponse)
def load_api(
    request: Request,
    api_base_url: str = Form(""),
    amount_min: str = Form(""),
    amount_max: str = Form(""),
    period_days_min: str = Form(""),
    period_days_max: str = Form(""),
    rating_min: str = Form(""),
):
    cfg = load_app_config(_default_config())
    cfg.api_base_url = api_base_url or cfg.api_base_url
    cfg.api_params = ApiParams.from_dict(
        {
            "amount_min": amount_min,
            "amount_max": amount_max,
            "period_days_min": period_days_min,
            "period_days_max": period_days_max,
            "rating_min": rating_min,
        }
    )
    save_app_config(cfg)

    try:
        items = fetch_all_pages(cfg.api_base_url, cfg.api_params.to_dict(), cfg.ignore_ssl)
        state.report = build_report(items, cfg.aliases)
        state.status = f"Строк: {state.report['rows_count']}"
    except Exception as exc:
        state.status = f"Ошибка: {exc}"

    return templates.TemplateResponse(
        "partials/table_container.html",
        {
            "request": request,
            "report": state.report,
            "status": state.status,
        },
    )


@app.post("/actions/save-settings", response_class=HTMLResponse)
def save_settings(
    request: Request,
    aliases: str = Form(""),
    ignore_ssl: str | None = Form(default=None),
):
    cfg = load_app_config(_default_config())
    cfg.aliases = aliases
    cfg.ignore_ssl = bool(ignore_ssl)
    save_app_config(cfg)
    state.status = "Настройки сохранены"

    return templates.TemplateResponse(
        "partials/status_line.html",
        {
            "request": request,
            "status": state.status,
        },
    )
