import unittest
import tempfile
from pathlib import Path
from atlas.chunking.sql_chunker import SQLChunker


class TestSQLChunkingMultipleStatements(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test method.
        Creates a temporary SQL file with multiple statements.
        """
        self.sql_code = """
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
        # Create a temporary file for the SQL code
        self.tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".sql", delete=False)
        self.tmp_file.write(self.sql_code)
        self.tmp_file.close()  # Close the file handle
        self.tmp_path = Path(self.tmp_file.name)

        # Register the cleanup function
        self.addCleanup(self.cleanup_temp_file)

    def cleanup_temp_file(self):
        """
        Clean up the temporary file after the test.
        """
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    def test_multiple_sql_statements_chunking(self):
        """
        Tests if multiple SQL statements in a file are chunked correctly.
        """
        chunker = SQLChunker()
        chunks = chunker.extract_chunks_from_file(self.tmp_path)

        print(f"Extracted {len(chunks)} SQL chunks:")  # Optional: for debugging/info
        for c in chunks:
            # Assuming chunk object has attributes: chunk_type, start_line, end_line, source
            # Adjust if your chunk object structure is different
            chunk_type = getattr(c, 'chunk_type', 'N/A')
            start_line = getattr(c, 'start_line', 'N/A')
            end_line = getattr(c, 'end_line', 'N/A')
            source_preview = getattr(c, 'source', '')[:40]  # Get first 40 chars of source
            print(f" - {chunk_type} ({start_line}-{end_line}): {source_preview}...")
