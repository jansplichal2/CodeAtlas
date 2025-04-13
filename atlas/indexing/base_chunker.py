from pathlib import Path
from typing import List, Optional, Dict


class CodeChunk:
    def __init__(
        self,
        chunk_type: str,
        name: Optional[str],
        start_line: int,
        end_line: int,
        source: str,
        file_path: str,
    ):
        self.chunk_type = chunk_type
        self.name = name
        self.start_line = start_line
        self.end_line = end_line
        self.source = source
        self.file_path = file_path

    def to_dict(self) -> Dict:
        return {
            "type": self.chunk_type,
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "file_path": self.file_path,
            "source": self.source,
        }


class BaseChunker:
    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        raise NotImplementedError

    def extract_chunks_from_dir(self, directory: Path) -> List[CodeChunk]:
        all_chunks = []
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    all_chunks.extend(self.extract_chunks_from_file(file_path))
                except Exception:
                    continue
        return all_chunks
