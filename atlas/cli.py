import typer
from pathlib import Path
from atlas.indexing.chunk_dispatcher import get_chunker
from atlas.indexing.embedder import save_chunks_to_files, validate_chunks
from atlas.indexing.embed_batch import embed_ready_chunks
from atlas.memory.loader import load_chunks_to_sqlite
from atlas.config import CHUNK_ERROR_DIR

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
    typer.echo(f"🔍 Validating chunks and moving the problematic ones to {CHUNK_ERROR_DIR}...")
    validate_chunks()


@app.command("load-sqlite")
def load_sqlite():
    typer.echo("📥 Loading chunk metadata into SQLite...")
    load_chunks_to_sqlite()


@app.command("load-qdrant")
def load_qdrant(batch_size: int = 100):
    typer.echo(f"🚀 Embedding up to {batch_size} ready chunks...")
    embed_ready_chunks(batch_size=batch_size)


if __name__ == "__main__":
    app()
