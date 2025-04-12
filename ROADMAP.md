# 🧭 Roadmap: Semantic Codebase Understanding System

This roadmap outlines the key milestones for building a system that semantically understands a mixed legacy codebase using chunking, embeddings, relational metadata, and LLM-powered reasoning.

---

## ✅ Milestone 1: Chunking Source Files

**Goal:** Convert raw code into coherent, semantically meaningful chunks.

### Tasks:
- [ ] Detect file types: Java, SQL, JSP, XML
- [ ] Use file-type specific chunking:
  - Java: methods/classes via `tree-sitter` or `javalang`
  - SQL: statements or `BEGIN...END` blocks via `sqlparse`
  - JSP: scriptlets, `<c:*>`, `${}` expressions
  - XML: nodes like `<bean>`, `<sql>`, `<config>`
- [ ] Tag each chunk with:
  - File path
  - Language
  - Start/end line numbers
  - Chunk type (e.g. `method`, `sql_block`, `jsp_scriptlet`)

**Output:** List of well-scoped chunks with metadata.

---

## ✅ Milestone 2: Populate Relational DB (SQLite)

**Goal:** Make the codebase searchable, filterable, and analyzable via SQL.

### Tasks:
- [ ] Design SQLite schema (`chunks`, `tables_used`, `columns_used`, etc.)
- [ ] Insert all chunks with:
  - Chunk ID
  - Chunk text
  - Metadata (file, function, type, etc.)
- [ ] Optional enrichment:
  - Table/column references (from SQL)
  - Function names
  - Comment headers (for future summaries)

**Output:** A structured, SQL-queryable mirror of the codebase.

---

## ✅ Milestone 3: Embed & Store in Vector DB

**Goal:** Enable semantic retrieval using vector similarity search.

### Tasks:
- [ ] Choose embedding model:
  - `text-embedding-3-small` (cheaper)
  - `text-embedding-3-large` (richer)
  - Local fallback: `nomic-embed-text`, `bge-large`
- [ ] Token-limit + batch chunks (max 8192 tokens per chunk)
- [ ] Generate embeddings
- [ ] Store embeddings in vector DB (e.g. Qdrant), along with:
  - Chunk ID
  - Shallow metadata (`file`, `method`, `table`)

**Output:** Vectorized semantic index for similarity queries.

---

## ✅ Milestone 4: Implement LLM-powered Agent

**Goal:** Enable intelligent interaction with the codebase via natural language.

### Tasks:
- [ ] User inputs natural-language query
- [ ] Embed query and search vector DB for relevant chunks
- [ ] Use SQLite for refinement/filtering
- [ ] Build prompt with context-rich retrieved chunks
- [ ] Send to LLM and return response
- [ ] (Optional) Enable follow-up questions or chain-of-thought reasoning

### Example Prompts:
- “What does `Buyer.statusCode` represent?”
- “Where is `validateOrder` called with `null` arguments?”
- “Summarize logic affecting `buyer` table rows.”

**Output:** First functional version of your code-aware assistant.

---

## 🧠 Optional Future Milestones

- [ ] Enum value inference and annotation
- [ ] Auto-generate documentation per column/function
- [ ] Interactive UI or web frontend
- [ ] Graph DB (e.g. Neo4j) for call graphs and flow analysis
- [ ] CLI wrapper with prompt templates
- [ ] Export annotated codebase to Markdown or Docusaurus

---

## 🛠 Technologies Considered

- **Chunking:** `tree-sitter`, `javalang`, `sqlparse`, regex fallback
- **Relational DB:** SQLite or DuckDB
- **Vector DB:** Qdrant (preferred), Chroma (dev), Weaviate (schema-rich)
- **LLM:** OpenAI API or local instruct model
- **Embedding Model:** OpenAI `text-embedding-3`, `nomic-embed-text`, `bge-large`

---

*Author: Jan Splichal  
*Created: [2025-04-11]*  
