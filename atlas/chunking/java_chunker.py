import tree_sitter_java

from pathlib import Path
from typing import List
from tree_sitter import Language, Parser
from atlas.chunking.base_chunker import BaseChunker, CodeChunk
from atlas.config import MAX_CHUNK_LINES

JAVA_LANGUAGE = Language(tree_sitter_java.language())


class JavaChunker(BaseChunker):

    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.parser = Parser(JAVA_LANGUAGE)

    def extract_chunks_from_file(self, file_path: Path) -> List[CodeChunk]:
        if file_path.suffix != ".java":
            return []

        source_code = file_path.read_text(encoding="utf-8")
        relative_file_path = file_path.relative_to(self.project_root)
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        lines = source_code.splitlines()
        chunks = []

        def walk_tree(cursor, callback):
            reached_root = False
            while not reached_root:
                callback(cursor.node)
                if cursor.goto_first_child():
                    continue
                if cursor.goto_next_sibling():
                    continue
                while True:
                    if not cursor.goto_parent():
                        reached_root = True
                        break
                    if cursor.goto_next_sibling():
                        break

        def split_long_chunk(raw_lines, chunk_type, name, start_line):
            subchunks = []
            buffer = []
            sub_start_line = start_line
            count = 1
            for i, line in enumerate(raw_lines):
                buffer.append(line)
                is_split_point = (
                        len(buffer) >= MAX_CHUNK_LINES
                        or line.strip() == ""
                        or line.strip().startswith("//")
                )
                if is_split_point:
                    sub_end_line = sub_start_line + len(buffer) - 1
                    count += 1
                    source = "\n".join(buffer)
                    if len(str.strip(source)) != 0:
                        subchunks.append(CodeChunk(
                            chunk_type=chunk_type,
                            name=name,
                            chunk_no=count,
                            start_line=sub_start_line,
                            end_line=sub_end_line,
                            source=source,
                            file_path=str(relative_file_path)
                        ))
                    sub_start_line = sub_end_line + 1
                    buffer = []
            if buffer:
                sub_end_line = sub_start_line + len(buffer) - 1
                count += 1
                source = "\n".join(buffer)
                if len(str.strip(source)) != 0:
                    subchunks.append(CodeChunk(
                        chunk_type=chunk_type,
                        name=name,
                        chunk_no=count,
                        start_line=sub_start_line,
                        end_line=sub_end_line,
                        source=source,
                        file_path=str(relative_file_path)
                    ))
            return subchunks

        def resolve_type(original_type):
            if original_type == "class_declaration":
                return "class"
            elif original_type == "method_declaration":
                return "function"
            else:
                return "unknown"

        def collect_node(node):
            if node.type in {"class_declaration", "method_declaration"}:
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf8") if name_node else "<anon>"
                start = node.start_point
                end = node.end_point
                chunk_type = resolve_type(node.type)
                source_lines = lines[start.row:end.row + 1]
                if len(source_lines) > MAX_CHUNK_LINES:
                    chunks.extend(split_long_chunk(source_lines, chunk_type, name, start.row + 1))
                else:
                    source = "\n".join(source_lines)
                    if len(str.strip(source)) != 0:
                        chunks.append(CodeChunk(
                            chunk_type=chunk_type,
                            name=name,
                            chunk_no=1,
                            start_line=start.row + 1,
                            end_line=end.row + 1,
                            source=source,
                            file_path=str(relative_file_path)
                        ))

        walk_tree(root_node.walk(), collect_node)
        return chunks
