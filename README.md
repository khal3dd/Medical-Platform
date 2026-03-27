# ⚕️ Medical Platform

A backend-first AI medical platform that provides **safe, educational health support** across multiple medical departments. Built with FastAPI + OpenRouter + RAG pipeline using ChromaDB and HuggingFace embeddings.

---

## ⚠️ Medical Disclaimer

This platform is for **general educational purposes only**. It is **not** a diagnostic tool, does not replace a licensed physician, and does not provide treatment or medication advice. Always consult a qualified healthcare professional for medical concerns.

---

## Features

- 💬 Conversational chat with multi-turn memory (in-memory, per session)
- 🏥 Multi-tenant support — each department has its own knowledge base and prompt
- 🧠 LLM via OpenRouter (any model supported)
- 📄 PDF ingestion pipeline — upload medical documents per department
- 🔍 RAG (Retrieval-Augmented Generation) — answers grounded in your documents
- 🗄️ ChromaDB local vector store (one collection per tenant)
- 🤗 HuggingFace local embeddings (multilingual — Arabic + English)
- 🚨 Emergency escalation for red-flag symptoms
- 🔒 Out-of-scope refusal for unsafe requests
- 🌐 Plain HTML/CSS/JS frontend served by FastAPI

---

## Supported Departments (Tenants)

| Tenant ID | Department |
|---|---|
| `liver` | Liver Care / Hepatology |
| `cardiology` | Cardiology |
| `nephrology` | Nephrology |

Tenants are configured via `ALLOWED_TENANTS` in `.env`.

---

## Project Structure
```
medical-platform/
├── src/
│   ├── backend/
│   │   ├── main.py                  # FastAPI app entrypoint
│   │   ├── core/
│   │   │   ├── config.py            # App settings via pydantic-settings
│   │   │   ├── logger.py            # Centralized file + console logging
│   │   │   └── prompts.py           # Dynamic tenant-aware prompt builder
│   │   ├── enums/
│   │   │   ├── chat.py              # MessageRole enum
│   │   │   └── responses.py         # ResponseSignal error codes
│   │   ├── schemas/
│   │   │   └── chat.py              # Request/response Pydantic models
│   │   ├── routers/
│   │   │   ├── chat.py              # Chat endpoints
│   │   │   └── ingestion.py         # PDF upload & management endpoints
│   │   ├── services/
│   │   │   ├── chat_service.py      # Session management + LLM orchestration
│   │   │   ├── ingestion_service.py # PDF ingestion pipeline
│   │   │   └── orchestrator.py      # RAG orchestrator
│   │   ├── providers/
│   │   │   ├── llm_provider.py      # OpenRouter API wrapper
│   │   │   ├── embeddings.py        # HuggingFace local embeddings
│   │   │   └── vector_store.py      # ChromaDB multi-tenant wrapper
│   │   └── utils/
│   │       ├── disk.py              # File/disk utilities
│   │       └── pdf_processor.py     # PDF text extraction + chunking
│   └── frontend/
│       ├── index.html               # Chat UI with department selector
│       ├── style.css                # Styling
│       └── config.json              # Frontend config (API URL)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quickstart

### 1. Clone & navigate
```bash
git clone <your-repo-url>
cd medical-platform
```

### 2. Create virtual environment
```bash
conda create -n medical-platform python=3.11 -y
conda activate medical-platform
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 5. Run the backend
```bash
cd src/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open the frontend
```
http://localhost:8000
```

---

## API Reference

> All endpoints require the `X-Tenant-ID` header.
> Example: `X-Tenant-ID: liver`

---

### Chat

#### `POST /api/v1/chat`

Send a message and receive a response.

**Headers:**
```
X-Tenant-ID: liver
```

**Request:**
```json
{
  "session_id": "user-abc-123",
  "message": "What foods should I avoid with liver disease?"
}
```

**Response:**
```json
{
  "session_id": "user-abc-123",
  "reply": "For liver disease, it is generally recommended to avoid...",
  "turn_count": 2
}
```

---

#### `DELETE /api/v1/chat/{session_id}`

Clear conversation history for a session.

---

#### `GET /api/v1/chat/health`

Health check endpoint.

---

### Ingestion

#### `POST /api/v1/ingestion/upload`

Upload a PDF and add it to the tenant's vector store.

**Headers:**
```
X-Tenant-ID: liver
```

**Request:** `multipart/form-data`
- `file`: PDF file

**Response:**
```json
{
  "tenant_id": "liver",
  "file_name": "liver_guidelines.pdf",
  "chunks_count": 9,
  "status": "success"
}
```

---

#### `DELETE /api/v1/ingestion/document/{file_name}`

Delete a specific document from the tenant's vector store.

**Headers:**
```
X-Tenant-ID: liver
```

**Response:**
```json
{
  "status": "success",
  "message": "Document 'liver_guidelines.pdf' deleted from tenant 'liver'."
}
```

---

#### `GET /api/v1/ingestion/status`

Get the number of chunks stored for a tenant.

**Headers:**
```
X-Tenant-ID: liver
```

**Response:**
```json
{
  "tenant_id": "liver",
  "chunks_in_store": 9
}
```

---

## Multi-Tenancy

Each department (tenant) has:
- Its own **ChromaDB collection** — documents are isolated per tenant
- Its own **system prompt** — LLM is specialized per department
- Its own **document knowledge base** — upload PDFs per department

The tenant is identified via the `X-Tenant-ID` header in every request.
```
X-Tenant-ID: liver      → liver collection + liver prompt
X-Tenant-ID: cardiology → cardiology collection + cardiology prompt
X-Tenant-ID: nephrology → nephrology collection + nephrology prompt
```

---

## RAG Pipeline
```
① Upload PDF via POST /api/v1/ingestion/upload (with X-Tenant-ID)
        ↓
② Text extracted from PDF (PyMuPDF)
        ↓
③ Text split into chunks (500 words, 50 overlap)
        ↓
④ Chunks converted to vectors (HuggingFace local model)
        ↓
⑤ Vectors stored in tenant's ChromaDB collection
        ↓
⑥ User asks a question via POST /api/v1/chat (with X-Tenant-ID)
        ↓
⑦ Question converted to vector
        ↓
⑧ Top 3 closest chunks retrieved from tenant's collection
        ↓
⑨ Chunks injected into LLM prompt as context
        ↓
⑩ LLM answers based on the document content
```

If no documents are uploaded for a tenant, the chatbot falls back to general LLM knowledge.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `LLM_MODEL` | `arcee-ai/trinity-large-preview:free` | Model identifier |
| `LLM_MAX_TOKENS` | `1024` | Max tokens in LLM response |
| `LLM_TEMPERATURE` | `0.3` | LLM temperature |
| `APP_HOST` | `0.0.0.0` | Uvicorn host |
| `APP_PORT` | `8000` | Uvicorn port |
| `SESSION_MAX_TURNS` | `20` | Max conversation turns per session |
| `ALLOWED_TENANTS` | `["liver","cardiology","nephrology"]` | Allowed tenant IDs |
| `VECTOR_STORE_PATH` | `./vector_store` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | HuggingFace model |
| `CHUNK_SIZE` | `500` | Words per chunk |
| `CHUNK_OVERLAP` | `50` | Overlapping words between chunks |
| `RETRIEVAL_TOP_K` | `3` | Chunks retrieved per query |
| `UPLOAD_DIR` | `./uploads` | PDF upload directory |
| `LOG_LEVEL` | `DEBUG` | Logging level |
| `LOG_FILE` | `./logs/app.log` | Log file path |

---

## Error Codes

| Code | Meaning |
|---|---|
| `ERR-1000` | Internal server error |
| `ERR-1001` | Bad gateway |
| `ERR-1002` | Service unavailable |
| `ERR-2002` | Session not found |
| `ERR-3001` | LLM call failed |
| `ERR-3002` | LLM rate limit exceeded |
| `ERR-3003` | LLM connection error |
| `ERR-4000` | File type not supported |
| `ERR-4001` | File upload failed |
| `ERR-4002` | Document has no readable text |
| `ERR-5000` | Invalid input |
| `ERR-5001` | Message too long |

---

## Safety Design

The platform enforces safety at the **prompt level**:

- Each tenant has a specialized system prompt scoped to its department
- Explicit prohibition of diagnosis, prescriptions, and unsafe claims
- Emergency symptoms trigger immediate urgent-care escalation
- Out-of-scope questions are politely refused
- RAG context is clearly separated from general knowledge

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| LLM | OpenRouter (any model) |
| Embeddings | HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector DB | ChromaDB (local, multi-tenant) |
| PDF Processing | PyMuPDF |
| Settings | pydantic-settings |
| Frontend | Plain HTML/CSS/JS |

---

## License

MIT
