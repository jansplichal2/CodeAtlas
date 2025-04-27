import json
import logging

from typing import Dict, Tuple, Any
from datetime import datetime

from atlas.config import CHUNK_DIR
from atlas.sqlite.utils import get_db_connection

logger = logging.getLogger(__name__)


def insert_chunk_record(conn: Any, chunk: Dict) -> Tuple[bool, str]:
    try:
        cur = conn.cursor()
        chunk_id = chunk.get("chunk_id")
        if not chunk_id:
            return True, f'Cannot find chunk_id in this chunk {chunk}'
        cur.execute(
            """INSERT INTO chunks 
               (chunk_id, 
               chunk_type, 
               name,
               chunk_no,
               start_line, 
               end_line, 
               file_path, 
               source, 
               tokens, 
               created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                chunk["type"],
                chunk["name"],
                chunk["chunk_no"],
                chunk["start_line"],
                chunk["end_line"],
                chunk["file_path"],
                chunk["source"],
                chunk.get("tokens", 0),
                datetime.utcnow().isoformat()
            )
        )
        conn.commit()

        return False, ''
    except Exception as e:
        return True, str(e)

def load_chunks_to_sqlite():
    count = 0
    errors = 0
    with get_db_connection() as conn:
        for chunk_file in CHUNK_DIR.glob("*.json"):
            with open(chunk_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                count += 1
                is_error, error = insert_chunk_record(conn, data)
                if is_error:
                    errors += 1
                    with open(chunk_file, "r+", encoding="utf-8") as w:
                        if 'errors' not in data:
                            data['errors'] = []
                        data['errors'].append({'source': 'sqlite', 'error': error})
                        json.dump(data, w, indent=2)

    logger.info(f"Inserted {count} chunks into SQLite. {errors} files finished with error")
