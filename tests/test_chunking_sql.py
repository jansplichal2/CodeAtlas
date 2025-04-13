import tempfile
from pathlib import Path
from atlas.indexing.sql_chunker import SQLChunker


def test_sql_chunking_multiple_statements():
    sql_code = """
-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT
);

-- Insert sample data
INSERT INTO users (id, name) VALUES (1, 'Alice');
INSERT INTO users (id, name) VALUES (2, 'Bob');

-- Select users
SELECT * FROM users;
"""

    with tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False) as tmp:
        tmp.write(sql_code)
        tmp_path = Path(tmp.name)

    chunker = SQLChunker()
    chunks = chunker.extract_chunks_from_file(tmp_path)

    print(f"Extracted {len(chunks)} SQL chunks:")
    for c in chunks:
        print(f" - {c.chunk_type} ({c.start_line}-{c.end_line}): {c.source[:40]}...")

    assert len(chunks) >= 3, "Expected at least 3 SQL statements to be chunked"
    assert all("sql_statement" == c.chunk_type for c in chunks), "Expected all chunks to be SQL statements"
