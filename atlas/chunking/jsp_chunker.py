import re
from pathlib import Path
from typing import List
from .base_chunker import BaseChunker, CodeChunk

class JSPChunker(BaseChunker):
    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        relative_file_path = file_path.relative_to(self.project_root)

        chunks = []
        current_chunk_lines = []
        chunk_start = 0
        chunk_no = 1

        def is_boundary(line: str) -> bool:
            return bool(re.match(r"\\s*<(%|jsp:|custom:|script|!--)", line.strip(), re.IGNORECASE))

        def should_split(prev_line: str, curr_line: str) -> bool:
            return (
                curr_line.strip() == "" and prev_line.strip() == ""
            ) or is_boundary(curr_line)

        prev_line = ""
        for i, line in enumerate(lines):
            if current_chunk_lines and should_split(prev_line, line):
                chunk = CodeChunk(
                    chunk_type="jsp",
                    chunk_no=chunk_no,
                    name=None,
                    start_line=chunk_start + 1,
                    end_line=chunk_start + len(current_chunk_lines),
                    source="".join(current_chunk_lines),
                    file_path=str(relative_file_path),
                )
                chunks.append(chunk)
                chunk_no += 1
                current_chunk_lines = []
                chunk_start = i
            current_chunk_lines.append(line)
            prev_line = line

        if current_chunk_lines:
            chunk = CodeChunk(
                chunk_type="jsp",
                chunk_no=chunk_no,
                name=None,
                start_line=chunk_start + 1,
                end_line=chunk_start + len(current_chunk_lines),
                source="".join(current_chunk_lines),
                file_path=str(relative_file_path),
            )
            chunks.append(chunk)

        return chunks