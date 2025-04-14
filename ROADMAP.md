# 📍 CodeAtlas++ Roadmap

A step-by-step plan to build an AI-powered semantic explorer for legacy codebases.

---

## ✅ Phase 1: Chunking System

- [x] Python chunker using `ast`
- [x] Java chunker using `javalang`
- [x] SQL chunker using regex splitting
- [x] Heuristic subchunking for long methods and classes
- [x] Language-aware dispatcher (`chunk_dispatcher.py`)
- [x] Unit tests for all language chunkers

---

## ✅ Phase 2: Chunk Storage and Validation

- [x] Serialize all chunks to individual `.chunks/*.json` files
- [x] Implement `--dry-run` with `tiktoken` to check token limits
- [x] CLI command: `codeatlas embed --dry-run`

---

## ✅ Phase 3: Chunk Metadata in SQLite

- [x] Central config module (`config.py`) for paths and constants
- [x] SQLite schema and storage module for `chunks` table
- [x] CLI command: `codeatlas db-load` to insert metadata into SQLite
- [x] Token counts and status tracking in DB

---

## 🚧 Phase 4: Embedding + Vector Indexing

- [ ] Select `ready` chunks from SQLite
- [ ] Generate embeddings using OpenAI API
- [ ] Index vectors into Qdrant
- [ ] Mark successfully indexed chunks as `embedded` in SQLite
- [ ] Handle failed embeddings (retry, mark `failed`, preserve file)

---

## ⏳ Phase 5: Query + Agent Framework (planned)

- [ ] Semantic search over indexed chunks
- [ ] Explain / summarize code using LLM
- [ ] Suggest refactors across chunk boundaries
- [ ] Multi-file context-aware querying

---

## ⏳ Phase 6: Language Extensions (planned)

- [ ] Add support for TypeScript and C#
- [ ] Optional LLM-driven chunking refinement
- [ ] Custom adapters for framework-heavy codebases

---

## ⏳ Phase 7: Interface + UX (planned)

- [ ] CLI interface for query + insight generation
- [ ] Web UI / TUI for visual graph of code relationships
- [ ] Export annotated code to Markdown or HTML

  