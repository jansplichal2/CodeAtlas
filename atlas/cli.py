import typer
from pathlib import Path
from atlas.indexing.chunk_dispatcher import get_chunker

app = typer.Typer()


@app.command()
def main():
    pass


@app.command()
def init(path: str):
    """
    Initialize project by chunking a codebase.
    """
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
                    typer.echo(f"📄 [{chunk.chunk_type}] {chunk.name or '<doc>'} "
                               f"({chunk.start_line}-{chunk.end_line})")
                total_chunks += len(chunks)
            except Exception as e:
                typer.echo(f"⚠️ Skipped {file_path.name}: {e}")

    typer.echo(f"✅ Finished. Extracted {total_chunks} chunks.")


if __name__ == "__main__":
    app()
