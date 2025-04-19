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
.
├── README.md
├── ROADMAP.md
├── atlas
│   ├── chunking
│   │   ├── __init__.py
│   │   ├── base_chunker.py
│   │   ├── chunk_dispatcher.py
│   │   ├── chunker.py
│   │   ├── java_chunker.py
│   │   ├── python_chunker.py
│   │   └── sql_chunker.py
│   ├── cli.py
│   ├── config.py
│   ├── embedding
│   │   ├── base_embedder.py
│   │   ├── embedder.py
│   │   ├── embedding_dispatcher.py
│   │   └── openai_embedder.py
│   ├── qdrant
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── sqlite
│   │   ├── __init__.py
│   │   └── loader.py
│   └── utils.py
├── requirements.txt
├── result.txt
├── tests
    ├── __init__.py
    ├── test_chunking_java.py
    ├── test_chunking_python.py
    └── test_chunking_sql.py
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
python -m atlas.cli <command> [OPTIONS]
```

---

## Commands

### `chunk`

Chunk all matching files under a root directory for further processing.

```bash
atlas.cli chunk <ROOT> -e <EXT> [-e <EXT> ...] [-x <DIR> ...]
```

**Arguments:**

- `ROOT`: Path to the root directory to scan.

**Options:**

- `-e`, `--ext`: File extensions to include (e.g., `py`, `sql`, `java`). **Required.**
- `-x`, `--exclude-dir`: Directory names to exclude (e.g., `venv`, `__pycache__`). Optional.

### `validate`

Validate the syntax or structure of previously chunked files.

```bash
atlas.cli validate
```

Runs internal validators on chunks stored in `.chunks/` and reports issues.

### `errors`

Display only the chunks with validation errors.

```bash
atlas.cli errors
```

Useful for inspecting what needs fixing before embedding or loading.

### `load-sqlite`

Load chunk metadata into SQLite.

```bash
atlas.cli load-sqlite
```

Loads information about all valid chunks into the configured local SQLite database.

### `embed`

Embed all valid chunks using the configured embedding provider and model.

```bash
atlas.cli embed
```

Embeddings are attached to each chunk and saved for vector indexing.

### `load-qdrant`

Push embedded chunks into Qdrant vector DB.

```bash
atlas.cli load-qdrant
```

Uses the stored embeddings and metadata to populate your Qdrant collection.

### `cleanup`

Remove all generated chunks from the `.chunks/` folder.

```bash
atlas.cli cleanup
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
atlas.cli chunk src/ -e py -e sql -x __pycache__

# Validate chunks
atlas.cli validate

# View errors if any
atlas.cli errors

# Load metadata into SQLite
atlas.cli load-sqlite

# Embed chunks
atlas.cli embed

# Index in Qdrant
atlas.cli load-qdrant
```


