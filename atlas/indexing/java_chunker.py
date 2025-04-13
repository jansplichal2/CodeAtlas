import javalang
from pathlib import Path
from typing import List
from .base_chunker import CodeChunk, BaseChunker


class JavaChunker(BaseChunker):
    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix != ".java":
            return []

        source_code = file_path.read_text(encoding="utf-8")
        lines = source_code.splitlines()
        chunks: List[CodeChunk] = []

        try:
            tree = javalang.parse.parse(source_code)
        except Exception as e:
            raise ValueError(f"Java parse error: {e}")

        # Top-level types (classes, interfaces, etc.)
        for type_node in tree.types:
            if hasattr(type_node, "name") and type_node.position:
                start = type_node.position.line
                # Approximate end line: look for closing brace or count lines of class body
                end = start + len(str(type_node).splitlines())
                chunks.append(CodeChunk(
                    chunk_type="class",
                    name=type_node.name,
                    start_line=start,
                    end_line=end,
                    source="\n".join(lines[start - 1:end]),
                    file_path=str(file_path),
                ))

            # Methods inside the class
            for member in getattr(type_node, "body", []):
                if isinstance(member, javalang.tree.MethodDeclaration) and member.position:
                    start = member.position.line
                    end = start + len(str(member).splitlines())
                    chunks.append(CodeChunk(
                        chunk_type="method",
                        name=member.name,
                        start_line=start,
                        end_line=end,
                        source="\n".join(lines[start - 1:end]),
                        file_path=str(file_path),
                    ))

        return chunks
