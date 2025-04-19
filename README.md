# 🧠 CodeAtlas++

**CodeAtlas++** is an AI-powered tool for semantically exploring and reasoning about legacy codebases.  
It uses language-aware chunking, token-safe validation, vector embeddings, and metadata tracking to support deep code understanding at scale.

---

## 🚀 Features

- Multi-language code chunking (Python, Java, SQL)
- Heuristic subchunking for large functions and classes
- Token-limit dry run using OpenAI tokenizer
- File-based chunk persistence (`.chunks/`)
- SQLite metadata tracking (`.codeatlas.sqlite`)
- CLI-first interface for automation and scripting

---

## 📦 Project Structure

```
.chunks/               # Individual serialized code chunks
.codeatlas.sqlite      # SQLite DB for tracking chunks
atlas/
├── indexing/          # Chunkers, dispatcher, embedder
├── memory/            # SQLite schema, loader
├── config.py          # Central paths & constants
├── cli.py             # Typer-based CLI entry point
```

---

## 🧭 Full Embedding & Indexing Flow

# CodeAtlas++ CLI

This command-line interface provides end-to-end support for analyzing source files, chunking them for semantic embedding, and storing the results in SQLite and Qdrant vector DBs.

All commands are accessible through the main `atlas` CLI app.

## 🔧 Installation

```bash
pip install -e .
```

## 📦 CLI Usage

```bash
python -m atlas <command> [OPTIONS]
```

---

## Commands

### `chunk`

Chunk all matching files under a root directory for further processing.

```bash
atlas chunk <ROOT> -e <EXT> [-e <EXT> ...] [-x <DIR> ...]
```

**Arguments:**

- `ROOT`: Path to the root directory to scan.

**Options:**

- `-e`, `--ext`: File extensions to include (e.g., `py`, `sql`, `java`). **Required.**
- `-x`, `--exclude-dir`: Directory names to exclude (e.g., `venv`, `__pycache__`). Optional.

### `validate`

Validate the syntax or structure of previously chunked files.

```bash
atlas validate
```

Runs internal validators on chunks stored in `.chunks/` and reports issues.

### `errors`

Display only the chunks with validation errors.

```bash
atlas errors
```

Useful for inspecting what needs fixing before embedding or loading.

### `load-sqlite`

Load chunk metadata into SQLite.

```bash
atlas load-sqlite
```

Loads information about all valid chunks into the configured local SQLite database.

### `embed`

Embed all valid chunks using the configured embedding provider and model.

```bash
atlas embed
```

Embeddings are attached to each chunk and saved for vector indexing.

### `load-qdrant`

Push embedded chunks into Qdrant vector DB.

```bash
atlas load-qdrant
```

Uses the stored embeddings and metadata to populate your Qdrant collection.

### `cleanup`

Remove all generated chunks from the `.chunks/` folder.

```bash
atlas cleanup
```

Use this if you want a clean slate before reprocessing files.

---

## 🔍 Developer Notes

- `--ext` can be repeated multiple times to include different types of files.
- Directories that start with a `.` (e.g., `.git`) are **automatically excluded**.
- Files and chunk metadata are saved under a `.chunks/` directory at the project root.
- `embed` and `load-qdrant` expect `.chunks/` to be populated and validated.

---

## Example Workflow

```bash
# Chunk all Python and SQL files
atlas chunk src/ -e py -e sql -x __pycache__

# Validate chunks
atlas validate

# View errors if any
atlas errors

# Load metadata into SQLite
atlas load-sqlite

# Embed chunks
atlas embed

# Index in Qdrant
atlas load-qdrant
```


