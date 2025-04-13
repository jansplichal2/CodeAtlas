from pathlib import Path
from .python_chunker import PythonChunker


def get_chunker(file_path: Path):
    if file_path.suffix == ".py":
        return PythonChunker()
    raise ValueError(f"No chunker implemented for file type: {file_path.suffix}")
