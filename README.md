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

```bash
.chunks/               # Individual serialized code chunks
.codeatlas.sqlite      # SQLite DB for tracking chunks
atlas/
├── indexing/          # Chunkers, dispatcher, embedder
├── memory/            # SQLite schema, loader
├── config.py          # Central paths & constants
├── cli.py             # Typer-based CLI entry point
