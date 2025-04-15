import sqlite3
from typing import List, Dict
from datetime import datetime
from atlas.config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_type TEXT,
    name TEXT,
    start_line INTEGER,
    end_line INTEGER,
    file_path TEXT,
    source TEXT,
    tokens INTEGER,
    status TEXT DEFAULT 'ready',
    created_at TEXT
);
"""


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    with connect_db() as conn:
        conn.executescript(SCHEMA)


def insert_chunk_records(chunks: List[Dict]):
    with connect_db() as conn:
        cur = conn.cursor()
        for chunk in chunks:
            cur.execute(
                "INSERT INTO chunks (chunk_type, name, start_line, end_line, file_path, source, tokens, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    chunk["type"],
                    chunk.get("name"),
                    chunk["start_line"],
                    chunk["end_line"],
                    chunk["file_path"],
                    chunk["source"],
                    chunk.get("tokens"),
                    chunk.get("status", "ready"),
                    datetime.utcnow().isoformat()
                )
            )
        conn.commit()


def update_chunk_status(ids: List[int], new_status: str):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.executemany(
            "UPDATE chunks SET status = ? WHERE id = ?",
            [(new_status, chunk_id) for chunk_id in ids]
        )
        conn.commit()
