import unittest
import tempfile
from pathlib import Path
from atlas.chunking.python_chunker import PythonChunker  # Assuming this import is correct


class TestPythonChunkingLongMethod(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test method.
        Creates a temporary Python file with a long function.
        """
        # Define the long Python function code
        self.python_code = """
def big_function():
    x = 0
    for i in range(100):
        x += i
        if i % 2 == 0:
            x -= 1
        else:
            x += 2
""" + ("\n" * 170) + """
        print(x)
        # comment
        print("still going")
        # another comment
        x *= 2
    return x
"""
        # Create a temporary file for the Python code
        self.tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False)
        self.tmp_file.write(self.python_code)
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

    def test_long_function_chunking(self):
        """
        Tests if a long Python function is correctly split into multiple chunks.
        """
        chunker = PythonChunker("/")
        chunks = chunker.extract_chunks_from_file(self.tmp_path)

        print(f"Extracted {len(chunks)} chunks:")  # Optional: for debugging/info
        for c in chunks:
            print(
                f" - Chunk Name: {getattr(c, 'name', 'N/A')}, Start: {getattr(c, 'start_line', 'N/A')}, End: {getattr(c, 'end_line', 'N/A')}")

        self.assertGreater(len(chunks), 1, "Expected function to be split into multiple chunks")

        all_chunks_named_correctly = all("big_function" in c.name for c in chunks if getattr(c, 'name', None))
        self.assertTrue(all_chunks_named_correctly, "All chunk names should include 'big_function'")


if __name__ == '__main__':
    unittest.main()
