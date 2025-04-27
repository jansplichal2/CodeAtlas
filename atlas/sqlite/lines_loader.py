import json
import logging

from datetime import datetime, timezone
from typing import Dict, Tuple, Any, List

from atlas.config import LINES_DIR
from atlas.sqlite.utils import get_db_connection

logger = logging.getLogger(__name__)


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
    count = 0
    errors = 0
    with get_db_connection() as conn:
        for line_file in LINES_DIR.glob("*.json"):
            with open(line_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                count += 1
                is_error, error = insert_line_record(conn, data)
                if is_error:
                    errors += 1
                    logger.error(error)

    logger.info(f"Inserted {count} files into SQLite. {errors} files finished with error")