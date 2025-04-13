import tempfile
from pathlib import Path
from atlas.indexing.python_chunker import PythonChunker


def test_python_chunking_long_method():
    code = """
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

    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)

    chunker = PythonChunker()
    chunks = chunker.extract_chunks_from_file(tmp_path)

    assert len(chunks) > 1, "Expected function to be split into multiple chunks"
    assert any("part" in c.name for c in chunks), "Expected part-named chunks"
    assert all("big_function" in c.name for c in chunks), "Chunk names should include function name"
