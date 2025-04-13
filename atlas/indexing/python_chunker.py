import ast
from pathlib import Path
from typing import List
from .base_chunker import CodeChunk, BaseChunker


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
                    start_line=docstring_node.lineno,
                    end_line=docstring_node.end_lineno,
                    source="\n".join(lines[docstring_node.lineno - 1:docstring_node.end_lineno]),
                    file_path=str(file_path)
                ))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                try:
                    chunk_source = "\n".join(lines[node.lineno - 1:node.end_lineno])
                except AttributeError:
                    continue
                chunks.append(CodeChunk(
                    chunk_type=type(node).__name__.lower(),
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno,
                    source=chunk_source,
                    file_path=str(file_path)
                ))

        return chunks
