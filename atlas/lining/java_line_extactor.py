import tree_sitter_java
import uuid

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from tree_sitter import Language, Node, Parser

from atlas.lining.base_line_extractor import LineContext, Line, BaseLineExtractor, read_source

JAVA_LANGUAGE = Language(tree_sitter_java.language())
parser = Parser(JAVA_LANGUAGE)


@dataclass(slots=True)
class JavaContextExtractor:
    """Walks a tree‑sitter syntax tree and fills a list[LineContext]."""

    source_bytes: bytes
    source_lines: List[str]
    package_name: Optional[str] = None
    _line_ctx: List[LineContext] = field(init=False, repr=False)

    # Pre‑computed lookup tables – class attrs for speed & memory
    _DECLARATIONS = {
        "class_declaration",
        "interface_declaration",
        "enum_declaration",
    }
    _CONTAINERS = {
        "class_body",
        "interface_body",
        "enum_body_declarations",
    }

    # Public ---------------------------------------------------------------
    def extract(self, root: Node) -> List[LineContext]:
        """Returns a list whose length == len(source_lines)."""

        self._line_ctx = [LineContext() for _ in self.source_lines]
        self._discover_package_name(root)
        self._visit(root, None, None)
        return self._line_ctx

    # Internal -------------------------------------------------------------
    def _discover_package_name(self, root: Node) -> None:
        pkg_node = next(
            (c for c in root.children if c.type == "package_declaration"), None
        )
        if not pkg_node:
            return
        name_node = pkg_node.child_by_field_name("name") or next(
            (c for c in pkg_node.children if c.type.endswith("identifier")), None
        )
        if name_node:
            self.package_name = self._text(name_node)

    # Recursive DFS traversal
    def _visit(
            self,
            node: Node,
            fq_class: Optional[str],
            method: Optional[str],
    ) -> None:
        node_type = node.type
        new_fq_class, new_method = fq_class, method

        # ---------------- Determine context for *this* node -------------
        if node_type in self._DECLARATIONS:
            name_node = node.child_by_field_name("name")
            if name_node:  # skip anonymous classes
                simple = self._text(name_node)
                new_fq_class = (
                    f"{fq_class}.{simple}"
                    if fq_class
                    else f"{self.package_name}.{simple}" if self.package_name else simple
                )
                new_method = None  # entering a new class scope resets method

        elif node_type == "method_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                new_method = self._text(name_node)

        # -------------- Apply context to the node's own line span -------
        self._set_context(node, new_fq_class, new_method)

        # -------------- Special handling for class bodies ---------------
        children = node.children
        if node_type in self._DECLARATIONS:
            body = node.child_by_field_name("body")
            if body and body.type in self._CONTAINERS:
                children = body.children

        # Detect Javadoc immediately preceding each child method
        prev: Optional[Node] = None
        for child in children:
            if (
                    prev
                    and prev.type == "block_comment"
                    and child.type == "method_declaration"
                    and self._is_javadoc(prev)
                    and prev.end_byte <= child.start_byte  # contiguous after whitespace
            ):
                method_name_node = child.child_by_field_name("name")
                if method_name_node:
                    m_name = self._text(method_name_node)
                    self._set_context(prev, new_fq_class, m_name)
            # Recurse – class context carries over; method resets for new child
            self._visit(child, new_fq_class, None)
            prev = child

    # Helpers -------------------------------------------------------------
    def _set_context(
            self,
            node: Node,
            fq_class: Optional[str],
            method: Optional[str],
    ) -> None:
        start, end = node.start_point[0], node.end_point[0]
        for line_no in range(start, min(end + 1, len(self._line_ctx))):
            ctx = self._line_ctx[line_no]
            if fq_class:
                ctx.clazz = fq_class
            if method:
                ctx.method = method

    def _text(self, node: Node) -> str:
        return self.source_bytes[node.start_byte: node.end_byte].decode("utf‑8")

    @staticmethod
    def _is_javadoc(node: Node) -> bool:
        return node.start_byte < node.end_byte and node.text.startswith(b"/**")


class JavaLineExtractor(BaseLineExtractor):
    def __init__(self, project_root: Path):
        super().__init__(project_root)

    def extract_lines_from_file(self, file_path: Path) -> List[Line]:
        src_bytes, src_lines = read_source(file_path)
        tree = parser.parse(src_bytes)

        extractor = JavaContextExtractor(src_bytes, src_lines)
        line_ctx = extractor.extract(tree.root_node)

        file_name = file_path.name
        result = []
        for i, (src_line, ctx) in enumerate(zip(src_lines, line_ctx)):
            result.append(
                Line(
                    line_id=str(uuid.uuid4()),
                    source=src_line,
                    file_name=file_name,
                    file_line_no=i + 1,
                    clazz=ctx.clazz,
                    method=ctx.method,
                )
            )
        return result
