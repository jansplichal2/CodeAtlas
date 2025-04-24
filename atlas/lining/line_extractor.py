import logging
import uuid
import json

from typing import List

from atlas.config import LINES_DIR
from atlas.lining.base_line_extractor import Line

logger = logging.getLogger(__name__)


def ensure_line_dir():
    LINES_DIR.mkdir(parents=True, exist_ok=True)


def save_lines_to_file(lines: List[Line]):
    ensure_line_dir()
    file_id = str(uuid.uuid4())
    data = [line.as_json() for line in lines]
    filename = f"lines_{file_id}.json"
    path = LINES_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


