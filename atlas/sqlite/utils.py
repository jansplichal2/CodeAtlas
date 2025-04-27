import logging
import sqlite3
import atexit

from atlas.config import DB_PATH

_connection = None

logger = logging.getLogger(__name__)

CHUNK_SCHEMA = """
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

LINE_SCHEMA = """
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

def get_db_connection():
    """Gets the single database connection."""
    global _connection
    if _connection is None:
        try:
            # consider check_same_thread=False if using threads, but be careful!
            _connection = sqlite3.connect(DB_PATH)
            _connection.row_factory = sqlite3.Row # Optional: Access columns by name
            _connection.execute("PRAGMA journal_mode=WAL;")
            logger.info("Database connection opened.")
            _connection.executescript(CHUNK_SCHEMA)
            _connection.executescript(LINE_SCHEMA)
            logger.info("Schemas loaded")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    return _connection

def close_db_connection():
    """Closes the database connection if it's open."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None
        print("Database connection closed.")

# Ensure the connection is closed when the program exits
atexit.register(close_db_connection)


def execute_sql_query(query: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info(f"{len(rows)} rows returned")
        return rows