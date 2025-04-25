import json
import logging
import sqlite3
from typing import Dict, Tuple, Any
from datetime import datetime
from atlas.config import CHUNK_DIR, DB_PATH

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE,
    chunk_type TEXT,
    name TEXT,
    chunk_no INTEGER,
    start_line INTEGER,
    end_line INTEGER,
    file_path TEXT,
    source TEXT,
    tokens INTEGER,
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


def test_sql_query(query: str):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info(f"{len(rows)} rows returned")
        return rows


def load_chunks_to_sqlite():
    init_db()
    count = 0
    errors = 0
    with connect_db() as conn:
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
