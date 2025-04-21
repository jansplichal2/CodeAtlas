from pathlib import Path
from typing import List, Optional, Dict


class CodeChunk:
    def __init__(
        self,
        chunk_type: str,
        chunk_no: int,
        name: Optional[str],
        start_line: int,
        end_line: int,
        source: str,
        file_path: str,
    ):
        self.chunk_type = chunk_type
        self.name = name
        self.chunk_no = chunk_no
        self.start_line = start_line
        self.end_line = end_line
        self.source = source
        self.file_path = file_path

    def to_dict(self) -> Dict:
        return {
            "type": self.chunk_type,
            "name": self.name,
            "chunk_no": self.chunk_no,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "file_path": self.file_path,
            "source": self.source,
        }


class BaseChunker:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        raise NotImplementedError

