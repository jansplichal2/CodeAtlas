from typing import List

import typer
from pprint import pprint
from pathlib import Path
from atlas.chunking.chunk_dispatcher import get_chunker
from atlas.chunking.chunker import save_chunks_to_files, validate_chunks, cleanup_chunks, display_error_chunks
from atlas.qdrant.qdrant_index import embed_ready_chunks
from atlas.sqlite.loader import load_chunks_to_sqlite, test_query
from atlas.utils import iter_files

app = typer.Typer()


@app.command()
def chunk(path: str):
    base_path = Path(path).resolve()
    if not base_path.exists():
        typer.echo(f"❌ Path does not exist: {base_path}")
        raise typer.Exit(code=1)

    typer.echo(f"🔍 Scanning and chunking for embedding: {base_path}")
    all_chunks = []
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            try:
                chunker = get_chunker(file_path)
                chunks = chunker.extract_chunks_from_file(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                typer.echo(f"⚠️ Skipped {file_path.name}: {e}")

    save_chunks_to_files(all_chunks)
    typer.echo(f"💾 Saved {len(all_chunks)} chunks to .chunks/")


@app.command()
def validate():
    typer.echo(f"🔍 Validating chunks ...")
    validate_chunks()


@app.command()
def errors():
    typer.echo(f"🔍 Display chunks with errors ...")
    display_error_chunks()


@app.command("load-sqlite")
def load_sqlite():
    typer.echo("📥 Loading chunk metadata into SQLite...")
    load_chunks_to_sqlite()


@app.command("test-sqlite")
def test_sqlite(query: str):
    typer.echo(f"Running SQL query {query}...")
    rows = test_query(query)
    for row in rows:
        pprint(dict(row))


@app.command("load-qdrant")
def load_qdrant(batch_size: int = 100):
    typer.echo(f"🚀 Embedding up to {batch_size} ready chunks...")
    embed_ready_chunks(batch_size=batch_size)


@app.command()
def cleanup():
    typer.echo('Cleaning up chunks')
    cleanup_chunks()


@app.command("test-chunk-files")
def test_(
    root: Path = typer.Argument(..., exists=True, file_okay=False, resolve_path=True),
    include_ext: List[str] = typer.Option(
        ...,
        "--ext",
        "-e",
        help="File extension(s) to include. Repeat the flag for multiple.",
        show_default=False,
    ),
    exclude_dir: List[str] = typer.Option(
        None,
        "--exclude-dir",
        "-x",
        help="Directory name(s) to skip. Repeat for multiple.",
    ),
):
    """
    Recursively list files below ROOT that match one or more -e/--ext extensions,
    skipping hidden directories and any -x/--exclude-dir names.
    """
    for path in iter_files(root, include_ext, exclude_dir):
        typer.echo(path)


if __name__ == "__main__":
    app()
