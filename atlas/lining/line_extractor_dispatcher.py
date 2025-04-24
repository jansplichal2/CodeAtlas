from pathlib import Path

from atlas.lining.java_line_extactor import JavaLineExtractor


def get_line_extractor(file_path: Path, project_root: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".java":
        return JavaLineExtractor(project_root)

    raise ValueError(f"No line extractor implemented for file type: {suffix}")