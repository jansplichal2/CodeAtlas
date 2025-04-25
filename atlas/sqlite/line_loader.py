import json
import logging
import sqlite3

from datetime import datetime, timezone
from typing import Dict, Tuple, Any, List

from atlas.config import LINES_DIR, DB_PATH

logger = logging.getLogger(__name__)


SCHEMA = """
CREATE TABLE IF NOT EXISTS lines (
    id INTEGER PRIMARY KEY,
    line_id TEXT UNIQUE,
    parent_type TEXT,
    parent_method TEXT,
    file_line_no INTEGER,
    file_path TEXT,
    source TEXT,
    created_at TEXT
);
"""


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    with connect_db() as conn:
        conn.executescript(SCHEMA)


def insert_line_record(conn: Any, lines: List[Dict]) -> Tuple[bool, str]:
    try:
        cur = conn.cursor()
        for line in lines:
            cur.execute(
                """INSERT INTO lines 
                   (line_id,
                    parent_type,
                    parent_method,
                    file_line_no,
                    file_path,
                    source,
                    created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    line['line_id'],
                    line['parent_type'],
                    line['parent_method'],
                    line['file_line_no'],
                    line['file_path'],
                    line['source'],
                    datetime.now(timezone.utc).isoformat()
                )
            )
        conn.commit()

        return False, ''
    except Exception as e:
        return True, str(e)


def load_lines_to_sqlite():
    init_db()
    count = 0
    errors = 0
    with connect_db() as conn:
        for line_file in LINES_DIR.glob("*.json"):
            with open(line_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                count += 1
                is_error, error = insert_line_record(conn, data)
                if is_error:
                    errors += 1
                    logger.error(error)

    logger.info(f"Inserted {count} lines into SQLite. {errors} files finished with error")