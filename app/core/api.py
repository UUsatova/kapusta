import json
import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


def build_query_url(base_url: str, params: dict) -> str:
    parsed = urlparse(base_url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for key, value in params.items():
        if value not in (None, ""):
            query_params[key] = value
    query = urlencode(query_params)
    return urlunparse(parsed._replace(query=query))


def fetch_json(url: str, verify_ssl: bool = True):
    req = Request(url, headers={"User-Agent": "Tkinter-Report/1.0"})
    context = None
    if not verify_ssl:
        context = ssl._create_unverified_context()
    with urlopen(req, timeout=20, context=context) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))
