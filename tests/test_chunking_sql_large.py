import unittest
from pathlib import Path
from atlas.chunking.sql_chunker import SQLChunker
from atlas.config import PROJECT_ROOT


class TestSQLChunkingMultipleStatements(unittest.TestCase):

    def test_sql_chunking_large_file(self):
        sql_file = PROJECT_ROOT / Path("tests/testdata/huge_test.sql")
        chunker = SQLChunker()
        chunks = chunker.extract_chunks_from_file(sql_file)

        print(f"Extracted {len(chunks)} chunks:")
        for chunk in chunks:
            print(f" - {chunk.chunk_type} ({chunk.start_line}-{chunk.end_line})")

        assert len(chunks) > 5, "Expected more than 5 chunks due to subchunking"
        assert any("part" in chunk.chunk_type for chunk in chunks), "Expected some part chunks from long statements"
