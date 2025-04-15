import typer
from pathlib import Path
from atlas.indexing.chunk_dispatcher import get_chunker
from atlas.indexing.embedder import save_chunks_to_files, dry_run_validate_chunks
from atlas.indexing.embed_batch import embed_ready_chunks
from atlas.memory.loader import load_chunks_to_sqlite

app = typer.Typer()


@app.command()
def init(path: str):
    base_path = Path(path).resolve()
    if not base_path.exists():
        typer.echo(f"❌ Path does not exist: {base_path}")
        raise typer.Exit(code=1)

    typer.echo(f"🔍 Scanning: {base_path}")
    total_chunks = 0
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            try:
                chunker = get_chunker(file_path)
                chunks = chunker.extract_chunks_from_file(file_path)
                for chunk in chunks:
                    typer.echo(f"📄 [{chunk.chunk_type}] {chunk.name or '<doc>'} ({chunk.start_line}-{chunk.end_line})")
                total_chunks += len(chunks)
            except Exception as e:
                typer.echo(f"⚠️ Skipped {file_path.name}: {e}")
    typer.echo(f"✅ Finished. Extracted {total_chunks} chunks.")


@app.command()
def embed(path: str, dry_run: bool = typer.Option(False, "--dry-run", help="Only check tokens, do not embed")):
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

    if dry_run:
        typer.echo("🔍 Running dry run token check...")
        dry_run_validate_chunks()
    else:
        typer.echo("🚧 Embedding not yet implemented.")


@app.command("db-load")
def db_load():
    typer.echo("📥 Loading chunk metadata into SQLite...")
    load_chunks_to_sqlite()


@app.command("embed-run")
def embed_run(batch_size: int = 100):
    typer.echo(f"🚀 Embedding up to {batch_size} ready chunks...")
    embed_ready_chunks(batch_size=batch_size)


if __name__ == "__main__":
    app()
