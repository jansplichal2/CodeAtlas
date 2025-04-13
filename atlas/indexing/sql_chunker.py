from pathlib import Path
from typing import List
from .base_chunker import CodeChunk, BaseChunker
import re


class SQLChunker(BaseChunker):
    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix.lower() not in [".sql", ".psql"]:
            return []

        source_code = file_path.read_text(encoding="utf-8")
        chunks = []
        statements = re.split(r";\s*\n", source_code)

        offset = 0
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            start_line = source_code[:source_code.find(stmt, offset)].count("\n") + 1
            end_line = start_line + stmt.count("\n")
            chunks.append(CodeChunk(
                chunk_type="sql_statement",
                name=None,
                start_line=start_line,
                end_line=end_line,
                source=stmt,
                file_path=str(file_path)
            ))
            offset = source_code.find(stmt, offset) + len(stmt)

        return chunks
