# Shared utilities
from pathlib import Path
import os
from typing import Collection, Iterable, Iterator


def iter_files(
        root: os.PathLike,
        include_exts: Iterable[str],
        exclude_dirs: Collection[str] = None
) -> Iterator[Path]:
    if not include_exts:
        raise ValueError("include_exts must contain at least one extension")

    # normalise things once up‑front
    include_exts = {("." + e.lstrip(".")).lower() for e in include_exts}
    exclude_dirs = {d.lower() for d in (exclude_dirs or set())}

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # prune unwanted sub‑directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d.lower() not in exclude_dirs]

        for filename in filenames:
            if Path(filename).suffix.lower() in include_exts:
                yield Path(dirpath) / filename
