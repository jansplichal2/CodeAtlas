from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass

@dataclass(slots=True)
class Line:
    line_id: str
    file_name: str
    source: str
    file_line_no: int
    clazz: Optional[str]
    method: Optional[str]

    def as_json(self) -> Dict[str, Optional[Any]]:  # noqa: D401 – simple name
        return {
            "line_id": self.line_id,
            "parent_type": self.clazz,
            "parent_method": self.method,
            "source": self.source,
            "file_path": self.file_name,
            "file_line_no": self.file_line_no,
        }

@dataclass(slots=True)
class LineContext:
    """Container for context metadata attached to a single source line."""
    clazz: Optional[str] = None  # fully‑qualified class or enum or interface
    method: Optional[str] = None  # simple method name


def read_source(path: Path) -> tuple[bytes, List[str]]:
    if not path.is_file():
        raise SystemExit(f"Error: File not found – {path}")
    try:
        src = path.read_bytes()
    except OSError as exc:
        raise SystemExit(f"Error reading {path}: {exc}") from exc
    return src, src.decode("utf‑8").splitlines()

class BaseLineExtractor:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def extract_lines_from_file(self, file_path: Path) -> List[Line]:
        raise NotImplementedError