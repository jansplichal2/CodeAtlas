import typer
import logging

from typing import List
from pprint import pprint
from pathlib import Path

from atlas.lining.line_extractor import save_lines_to_file
from atlas.lining.line_extractor_dispatcher import get_line_extractor
from atlas.qdrant.chunks_loader import client as qdrant_client

from atlas.agents.agent_workflow import run
from atlas.chunking.chunk_dispatcher import get_chunker
from atlas.chunking.chunker import save_chunks_to_files, validate_chunks, cleanup_chunks, display_error_chunks
from atlas.config import EMBED_PROVIDER, EMBED_MODEL, QDRANT_PATH
from atlas.embedding.embedder import embed_chunks
from atlas.embedding.embedding_dispatcher import get_embedder
from atlas.sqlite.lines_loader import load_lines_to_sqlite
from atlas.sqlite.chunks_loader import load_chunks_to_sqlite
from atlas.sqlite.utils import get_db_connection, execute_sql_query
from atlas.qdrant.chunks_loader import load_chunks_to_qdrant, test_qdrant_query
from atlas.utils import iter_files

logging.basicConfig(
    level=logging.INFO
)

app = typer.Typer()
test_app = typer.Typer()
app.add_typer(test_app, name="test")


def validate_and_normalize(root: Path, project_root: str):
    base_path = Path(root).resolve()
    if not base_path.exists():
        typer.echo(f"❌ Path does not exist: {base_path}")
        raise typer.Exit(code=1)

    project_root_path = Path(project_root).resolve()
    if not project_root_path.exists():
        typer.echo(f"❌ Project root not exist: {project_root_path}")
        raise typer.Exit(code=1)
    return base_path, project_root_path

@app.command("extract-lines")
def extract_lines(
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
        project_root: str = typer.Option(
            "/",
            "--project-root",
            "-p",
            help="Root of the project directory.",
        ),
):
    base_path, project_root_path = validate_and_normalize(root, project_root)

    typer.echo(f"🔍 Scanning and extracting lines for embedding: {base_path}")
    counter = 0

    for file_path in iter_files(root, include_ext, exclude_dir):
        if file_path.is_file():
            try:
                line_extractor = get_line_extractor(file_path, project_root_path)
                lines = line_extractor.extract_lines_from_file(file_path)
                save_lines_to_file(lines)
                counter += 1
            except Exception as e:
                import traceback
                typer.echo(f"⚠️ Skipped {file_path.name}: {e}")
                raise ValueError(f"Java parse error:\n{traceback.format_exc()}")


    typer.echo(f"💾 Saved {counter} files to .lines/")

@app.command()
def chunk(
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
        project_root: str = typer.Option(
            "/",
            "--project-root",
            "-p",
            help="Root of the project directory.",
        ),
):
    base_path, project_root_path = validate_and_normalize(root, project_root)

    typer.echo(f"🔍 Scanning and chunking for embedding: {base_path}")
    all_chunks = []

    for file_path in iter_files(root, include_ext, exclude_dir):
        if file_path.is_file():
            try:
                chunker = get_chunker(file_path, project_root_path)
                chunks = chunker.extract_chunks_from_file(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                import traceback
                typer.echo(f"⚠️ Skipped {file_path.name}: {e}")
                raise ValueError(f"Java parse error:\n{traceback.format_exc()}")

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


@app.command("load-sqlite-lines")
def load_sqlite_lines():
    typer.echo("📥 Loading line metadata into SQLite...")
    load_lines_to_sqlite()


@app.command()
def embed():
    typer.echo(f"🚀 Getting embeddings for chunks...")
    embed_chunks()


@app.command("load-qdrant")
def load_qdrant():
    typer.echo(f"🚀 Loading chunks into qdrant...")
    load_chunks_to_qdrant()


@app.command()
def cleanup():
    typer.echo('Cleaning up chunks')
    cleanup_chunks()


@test_app.command("sqlite")
def test_sqlite(query: str):
    typer.echo(f"Running SQL query {query}...")
    rows = execute_sql_query(query)
    for row in rows:
        pprint(dict(row))


@test_app.command("qdrant")
def test_qdrant(query: str):
    typer.echo(f"Running semantic query {query}...")
    embedder = get_embedder(EMBED_PROVIDER, EMBED_MODEL)
    embedding = embedder.retrieve_embedding_for_query(query)
    rows = test_qdrant_query(embedding, 10)
    for row in rows:
        pprint(dict(row))


@test_app.command("agent")
def test_agent(query: str):
    with get_db_connection() as sqlite:
        result = run(query, sqlite, qdrant_client)
        pprint(result)


@test_app.command("list-files")
def test_chunk_files(
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
