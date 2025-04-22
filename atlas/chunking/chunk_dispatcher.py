from pathlib import Path
from atlas.chunking.python_chunker import PythonChunker
from atlas.chunking.java_chunker import JavaChunker
from atlas.chunking.sql_chunker import SQLChunker
from atlas.chunking.jsp_chunker import JSPChunker


def get_chunker(file_path: Path, project_root: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        return PythonChunker(project_root)
    elif suffix == ".java":
        return JavaChunker(project_root)
    elif suffix in [".sql", ".tsql"]:
        return SQLChunker(project_root)
    elif suffix == ".jsp":
        return JSPChunker(project_root)
    raise ValueError(f"No chunker implemented for file type: {suffix}")