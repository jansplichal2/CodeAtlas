# CodeAtlas++ Dev UI Backend

A minimalistic developer-facing backend with frontend UI for interacting with CodeAtlas services.


---

## Features

- **REST API** for querying:
  - Relational DB
  - Vector DB
  - Graph DB (Joern)
  - LLMs (OpenAI, Anthropic)
- **Minimalist frontend**.
- **Dark theme**, elegant and clean UI.

---

## Project Structure

```
web/
├── main.py            # FastAPI app, mounts frontend and API
├── api/
│   └── query.py       # API endpoint handling /api/query
├── services/
│   ├── relational.py  # Relational DB service logic (stub)
│   ├── vector.py      # Vector DB service logic (stub)
│   ├── graph.py       # Graph DB service logic (stub)
│   └── llm.py         # LLM interaction logic (stub)
├── models/
│   └── query_request.py # Pydantic request model
├── static/
│   ├── styles.css     # Frontend CSS
│   └── scripts.js     # Frontend JS
├── templates/
│   └── index.html     # Frontend HTML
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## Getting Started



**Run the FastAPI app:**
```bash
uvicorn atlas.web.main:app --reload
```

**Access the frontend:**
```
http://localhost:8000/
```

**API Endpoint:**
```
POST http://localhost:8000/api/query
```

---

## API Specification

### POST `/api/query`

**Request Body (JSON):**
```json
{
  "service": "relational",  // or "vector", "graph", "llm"
  "query": "SELECT * FROM Users;",
  "llmProvider": "openai",   // optional if service == "llm"
  "llmModel": "ChatGPT 4o"   // optional if service == "llm"
}
```

**Successful Response:**
```json
{
  "status": "success",
  "service": "relational",
  "result": { "rows": [{"id": 1, "name": "Alice"}] }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Detailed error description."
}
```

---

## Future Enhancements

- Real database and vector search integrations.
- Real LLM API calls to OpenAI, Anthropic.
- Add authentication for dev-only access.
- Expand frontend with better input validation.
- Support `/api/v1/` style versioning.

---

## License

Internal project for CodeAtlas++ development. No public license specified yet.

---

> Built with speed, minimalism, and elegance for developers.
