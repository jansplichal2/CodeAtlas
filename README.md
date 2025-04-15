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

```bash
# 1. Chunk the codebase and inspect structure
codeatlas init ./my_project

# 2. Save chunks to .chunks/ and validate token limits
codeatlas embed ./my_project --dry-run

# 3. Load valid chunks into SQLite
codeatlas db-load

# 4. Embed, index in Qdrant, update DB, and delete chunk files
codeatlas index
