import sqlite3
from typing import List, Dict
from datetime import datetime
from atlas.config import DB_PATH

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
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    with connect_db() as conn:
        conn.executescript(SCHEMA)


def insert_chunk_records(chunks: List[Dict]):
    with connect_db() as conn:
        cur = conn.cursor()
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            if not chunk_id:
                continue
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
