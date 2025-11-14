import json
import re
from pathlib import Path
from typing import Any, Dict

from .config import DEFAULT_ENCODING


def sanitize_filename(name: str) -> str:
    if not name:
        return "business"
    cleaned = re.sub(r"\s+", "_", name.strip())
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", cleaned)
    return cleaned or "business"


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding=DEFAULT_ENCODING) as f:
        data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Root of JSON must be an object")
        return data
