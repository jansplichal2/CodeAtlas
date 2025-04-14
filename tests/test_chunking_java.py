import unittest
import tempfile
from pathlib import Path
from atlas.indexing.java_chunker import JavaChunker  # Assuming this import is correct


class TestJavaChunkingLongMethod(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test method.
        Creates a temporary Java file with a long method.
        """
        method_body = "\n".join(["        x = x + " + str(i) + ";" for i in range(200)])
        self.java_code = f"""
public class BigClass {{
    public int bigMethod() {{
        int x = 0;
{method_body}
        return x;
    }}
}}
"""
        # Create a temporary file for the Java code
        # 'delete=False' is needed on Windows to allow reopening; we'll handle deletion manually.
        self.tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".java", delete=False)
        self.tmp_file.write(self.java_code)
        self.tmp_file.close()  # Close the file handle so chunker can open it
        self.tmp_path = Path(self.tmp_file.name)

        # Ensure the file is cleaned up after the test method runs
        self.addCleanup(self.cleanup_temp_file)

    def cleanup_temp_file(self):
        """
        Clean up the temporary file.
        """
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    def test_long_method_chunking(self):
        """
        Tests if a long Java method is correctly split into multiple chunks.
        """
        chunker = JavaChunker()
        chunks = chunker.extract_chunks_from_file(self.tmp_path)

        print(f"Extracted {len(chunks)} chunks:")  # Optional: keep for debugging/info
        for c in chunks:
            print(f" - {c.chunk_type}: {c.name} ({c.start_line}-{c.end_line})")

        # Assert that the long method was split into more than one chunk
        self.assertGreater(len(chunks), 1, "Expected long method to be split into multiple chunks")

        # Assert that at least one chunk has 'part' in its name (indicating a split part)
        # Filters out chunks where c.name might be None or empty before checking 'part'
        has_part_chunk = any("part" in c.name for c in chunks if c.name)
        self.assertTrue(has_part_chunk, "Expected at least one chunk name to contain 'part'")

        # Assert that all method chunks include the original method name 'bigMethod'
        # Filters for chunks marked as 'method' type and having a non-empty name
        all_method_chunks_named_correctly = all(
            "bigMethod" in c.name for c in chunks if c.name and "method" in c.chunk_type
        )
        self.assertTrue(all_method_chunks_named_correctly, "All method chunk names should include 'bigMethod'")


# Standard boilerplate to run the tests when the script is executed
if __name__ == '__main__':
    unittest.main()
