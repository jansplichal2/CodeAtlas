# 🗺️ CodeAtlas++ MVP Roadmap

> **Goal**: Build a developer-assist tool that enables reasoning over entire codebases using LLMs, vector search, and task memory. Target MVP in 8–10 weeks.

---

## ✅ Phase 1: Core Foundation (Week 1–2)

**Objectives:**
- Parse codebase into meaningful chunks (function/class/module)
- Generate embeddings
- Store code metadata and semantic index

**Tasks:**
- [ ] CLI tool: `codeatlas init <path-to-repo>`
- [ ] AST parser for supported languages (start with Python)
- [ ] Embedding generator (OpenAI `text-embedding-3-small` or CodeBERT)
- [ ] Vector DB setup (Chroma or Qdrant)
- [ ] Store: file path, symbol, dependencies

---

## 🧠 Phase 2: Query & Reasoning Agent (Week 3–5)

**Objectives:**
- Enable high-level developer queries over the codebase
- Use LLM to generate diffs, explanations, and changelogs

**Tasks:**
- [ ] Define natural query format: `"Refactor this module for X"`
- [ ] Retrieve relevant code chunks via vector search
- [ ] Prompt LLM with goal + code context
- [ ] Return:
  - [ ] Natural language explanation
  - [ ] Code patch (diff)
  - [ ] Risk or review notes
  - [ ] Draft changelog

---

## 🗃️ Phase 3: Task Memory & History (Week 6–7)

**Objectives:**
- Track agent output across multiple queries
- Allow undo, reattempts, and contextual follow-ups

**Tasks:**
- [ ] Store per-task memory:
  - [ ] Prompt
  - [ ] Code changes
  - [ ] Reasoning
  - [ ] Approval state
- [ ] SQLite or lightweight Postgres store
- [ ] Command: `codeatlas history`, `codeatlas explain <change-id>`

---

## 🔁 Phase 4: Git Integration & Dev Loop (Week 8–9)

**Objectives:**
- Help developer stage, commit, and review AI-generated changes

**Tasks:**
- [ ] Display diff + rationale
- [ ] Command: `codeatlas review`
- [ ] Command: `codeatlas commit`
- [ ] Optional: `codeatlas pr` to open GitHub/GitLab PR

---

## 🎯 Future Enhancements (Post-MVP)

- [ ] Add Claude/Gemini support for longer context window
- [ ] Frontend UI (Streamlit/React)
- [ ] Screenshot → layout parser (via GPT-4 Vision)
- [ ] Agent planner for multi-step refactors
- [ ] Add support for additional languages (TypeScript, SQL, etc.)

---

## 🧭 Suggested Tech Stack

| Layer          | Tools / Libraries                     |
|----------------|----------------------------------------|
| LLM API        | OpenAI GPT-4, Claude 2.1              |
| Embeddings     | OpenAI `text-embedding-3-small`       |
| Vector DB      | Chroma, Weaviate, or Qdrant           |
| Parser         | `ast`, `tree-sitter`, or `jedi`       |
| Storage        | SQLite or Postgres                    |
| CLI            | Click, Typer, or Argparse             |
| Optional UI    | Streamlit or React (later phase)      |

---

## 🧩 MVP Deliverables

- CLI tool to initialize and analyze codebase
- Vector DB with semantically chunked code
- Agent that can reason over goals and propose diffs
- Review loop with memory and history
- Git integration (diffs, commit, PR)

---

> Status: **In design**
> Timeline: **~8–10 weeks**
> Team: **Solo dev, expandable**
