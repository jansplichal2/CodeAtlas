from pathlib import Path
from typing import List
from atlas.chunking.base_chunker import CodeChunk, BaseChunker
from atlas.config import MAX_CHUNK_LINES
import re


class SQLChunker(BaseChunker):
    def __init__(self, project_root: Path):
        super().__init__(project_root)

    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix.lower() not in [".sql", ".psql"]:
            return []

        relative_file_path = file_path.relative_to(self.project_root)
        source_code = file_path.read_text(encoding="utf-8")
        chunks = []
        statements = re.split(r";\\s*\\n", source_code)

        offset = 0

        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            start_line = source_code[:source_code.find(stmt, offset)].count("\\n") + 1
            end_line = start_line + stmt.count("\\n")

            lines = stmt.splitlines()
            if len(lines) > MAX_CHUNK_LINES:
                subchunks = self._split_long_sql(lines, start_line, relative_file_path)
                chunks.extend(subchunks)
            else:
                chunks.append(CodeChunk(
                    chunk_type="sql_statement",
                    name=f"statement_part_1",
                    chunk_no=1,
                    start_line=start_line,
                    end_line=end_line,
                    source=stmt,
                    file_path=str(relative_file_path)
                ))

            offset = source_code.find(stmt, offset) + len(stmt)

        return chunks

    def _split_long_sql(self, lines: List[str], start_line: int, relative_file_path: Path) -> List[CodeChunk]:
        chunks = []
        buffer = []
        sub_start_line = start_line
        count = 1

        for i, line in enumerate(lines):
            buffer.append(line)
            is_split_point = (
                len(buffer) >= MAX_CHUNK_LINES
                or line.strip() == ""
                or line.strip().startswith("--")
            )
            if is_split_point:
                count += 1
                sub_end_line = sub_start_line + len(buffer) - 1
                chunks.append(CodeChunk(
                    chunk_type="sql_statement",
                    name=f"statement_part_{count}",
                    chunk_no=count,
                    start_line=sub_start_line,
                    end_line=sub_end_line,
                    source="\n".join(buffer),
                    file_path=str(relative_file_path)
                ))
                sub_start_line = sub_end_line + 1
                buffer = []
                count += 1

        if buffer:
            count += 1
            sub_end_line = sub_start_line + len(buffer) - 1
            chunks.append(CodeChunk(
                chunk_type="sql_statement",
                name=f"statement_part_{count}",
                chunk_no=count,
                start_line=sub_start_line,
                end_line=sub_end_line,
                source="\n".join(buffer),
                file_path=str(relative_file_path)
            ))

        return chunks