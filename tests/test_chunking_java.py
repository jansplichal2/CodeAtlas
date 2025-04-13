import tempfile
from pathlib import Path
from atlas.indexing.java_chunker import JavaChunker


def test_java_chunking_long_method():
    method_body = "\n".join(["        x = x + " + str(i) + ";" for i in range(200)])
    java_code = f"""
public class BigClass {{
    public int bigMethod() {{
        int x = 0;
{method_body}
        return x;
    }}
}}
"""

    with tempfile.NamedTemporaryFile("w+", suffix=".java", delete=False) as tmp:
        tmp.write(java_code)
        tmp_path = Path(tmp.name)

    chunker = JavaChunker()
    chunks = chunker.extract_chunks_from_file(tmp_path)

    print(f"Extracted {len(chunks)} chunks:")
    for c in chunks:
        print(f" - {c.chunk_type}: {c.name} ({c.start_line}-{c.end_line})")

    assert len(chunks) > 1, "Expected long method to be split into multiple chunks"
    assert any("part" in c.name for c in chunks if c.name), "Expected part-named chunks"
    assert all("bigMethod" in c.name for c in chunks if c.name and "method" in c.chunk_type), "Chunk names should include method name"