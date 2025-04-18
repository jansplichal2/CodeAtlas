from pathlib import Path
from .python_chunker import PythonChunker
from .java_chunker import JavaChunker
from .sql_chunker import SQLChunker


def get_chunker(file_path: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        return PythonChunker()
    elif suffix == ".java":
        return JavaChunker()
    elif suffix in [".sql", ".tsql"]:
        return SQLChunker()
    raise ValueError(f"No chunker implemented for file type: {suffix}")