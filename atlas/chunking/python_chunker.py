import ast
from pathlib import Path
from typing import List
from atlas.chunking.base_chunker import CodeChunk, BaseChunker
from atlas.config import MAX_CHUNK_LINES


class PythonChunker(BaseChunker):

    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix != ".py":
            return []

        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code)
        lines = source_code.splitlines()
        chunks: List[CodeChunk] = []

        docstring = ast.get_docstring(tree)
        if docstring:
            docstring_node = tree.body[0]
            if isinstance(docstring_node, ast.Expr):
                chunks.append(CodeChunk(
                    chunk_type="docstring",
                    name=None,
                    chunk_no=1,
                    start_line=docstring_node.lineno,
                    end_line=docstring_node.end_lineno,
                    source="\\n".join(lines[docstring_node.lineno - 1:docstring_node.end_lineno]),
                    file_path=str(file_path)
                ))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                try:
                    start = node.lineno
                    end = node.end_lineno
                    if end - start + 1 > MAX_CHUNK_LINES:
                        chunks.extend(self._split_long_chunk(node, lines, file_path))
                    else:
                        chunk_source = "\\n".join(lines[start - 1:end])
                        chunks.append(CodeChunk(
                            chunk_type=type(node).__name__.lower(),
                            name=node.name,
                            chunk_no=1,
                            start_line=start,
                            end_line=end,
                            source=chunk_source,
                            file_path=str(file_path)
                        ))
                except AttributeError:
                    continue

        return chunks

    def _split_long_chunk(self, node, lines, file_path: Path) -> List[CodeChunk]:
        chunks = []
        start = node.lineno
        end = node.end_lineno
        raw_lines = lines[start - 1:end]
        chunk_type = type(node).__name__.lower()
        name = node.name

        sub_start_line = start
        count = 1
        buffer = []
        for i, line in enumerate(raw_lines):
            buffer.append(line)
            is_split_point = (
                len(buffer) >= MAX_CHUNK_LINES or
                line.strip() == "" or
                line.strip().startswith("#")
            )
            if is_split_point:
                sub_end_line = sub_start_line + len(buffer) - 1
                chunks.append(CodeChunk(
                    chunk_type=chunk_type,
                    name=name,
                    chunk_no=count,
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
                chunk_type=chunk_type,
                name=name,
                chunk_no=count,
                start_line=sub_start_line,
                end_line=sub_end_line,
                source="\\n".join(buffer),
                file_path=str(file_path)
            ))

        return chunks