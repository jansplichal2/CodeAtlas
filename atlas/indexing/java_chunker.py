from pathlib import Path
from typing import List
from .base_chunker import CodeChunk, BaseChunker

try:
    import javalang
except ImportError:
    javalang = None


class JavaChunker(BaseChunker):
    MAX_CHUNK_LINES = 80

    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix != ".java":
            return []

        if javalang is None:
            raise ImportError("javalang must be installed for Java chunking")

        source_code = file_path.read_text(encoding="utf-8")
        chunks = []
        lines = source_code.splitlines()

        try:
            tree = javalang.parse.parse(source_code)
        except Exception as e:
            raise ValueError(f"Java parse error: {e}")

        for type_node in tree.types:
            if hasattr(type_node, "name") and type_node.position:
                start = type_node.position.line
                end = self._find_scope_end(start, lines)
                if end - start + 1 > self.MAX_CHUNK_LINES:
                    chunks.extend(
                        self._split_long_chunk(lines[start - 1:end], "class", type_node.name, start, file_path))
                else:
                    chunks.append(CodeChunk("class", type_node.name, start, end, "\\n".join(lines[start - 1:end]),
                                            str(file_path)))

            for member in getattr(type_node, "body", []):
                if isinstance(member, javalang.tree.MethodDeclaration) and member.position:
                    start = member.position.line
                    end = self._find_scope_end(start, lines)
                    if end - start + 1 > self.MAX_CHUNK_LINES:
                        chunks.extend(
                            self._split_long_chunk(lines[start - 1:end], "method", member.name, start, file_path))
                    else:
                        chunks.append(CodeChunk("method", member.name, start, end, "\\n".join(lines[start - 1:end]),
                                                str(file_path)))

        return chunks

    def _find_scope_end(self, start_line: int, lines: List[str]) -> int:
        brace_level = 0
        in_scope = False
        for i in range(start_line - 1, len(lines)):
            line = lines[i]
            brace_level += line.count("{")
            brace_level -= line.count("}")
            if "{" in line:
                in_scope = True
            if in_scope and brace_level == 0:
                return i + 1
        return len(lines)

    def _split_long_chunk(self, raw_lines, chunk_type, name, start_line, file_path: Path) -> List[CodeChunk]:
        chunks = []
        buffer = []
        sub_start_line = start_line

        for i, line in enumerate(raw_lines):
            buffer.append(line)
            is_split_point = (
                    len(buffer) >= self.MAX_CHUNK_LINES or
                    line.strip() == "" or
                    line.strip().startswith("//")
            )
            if is_split_point:
                sub_end_line = sub_start_line + len(buffer) - 1
                chunks.append(CodeChunk(
                    chunk_type=f"{chunk_type}_part",
                    name=f"{name}_part{i}",
                    start_line=sub_start_line,
                    end_line=sub_end_line,
                    source="\\n".join(buffer),
                    file_path=str(file_path)
                ))
                sub_start_line = sub_end_line + 1
                buffer = []

        if buffer:
            sub_end_line = sub_start_line + len(buffer) - 1
            chunks.append(CodeChunk(
                chunk_type=f"{chunk_type}_part",
                name=f"{name}_tail",
                start_line=sub_start_line,
                end_line=sub_end_line,
                source="\\n".join(buffer),
                file_path=str(file_path)
            ))

        return chunks
