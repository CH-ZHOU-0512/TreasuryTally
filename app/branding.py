"""The user-provided transparent brand asset, used unchanged."""

from base64 import b64encode
from functools import lru_cache
from pathlib import Path

LOGO_PATH = Path(__file__).resolve().parent / "static" / "logo.png"


def logo_static_url(base_path: str = "") -> str:
    prefix = base_path.strip("/")
    return f"/{prefix + '/' if prefix else ''}app/static/logo.png"


@lru_cache(maxsize=1)
def logo_data_url() -> str:
    return "data:image/png;base64," + b64encode(LOGO_PATH.read_bytes()).decode("ascii")
