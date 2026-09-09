# JARVIS — AI Second Brain

A multi-agent AI personal assistant that ingests your documents, understands your goals, and acts as a persistent second brain. It answers questions, tracks habits, sets reminders, and executes actions — with a full chat UI and voice interface built in.

---

## What It Does

- **Conversational AI** — chat with your knowledge base using natural language
- **Document Ingestion** — upload PDFs, DOCX, and PPTX files; JARVIS reads and indexes them
- **Voice Interface** — speak to JARVIS and hear responses (Azure Speech SDK)
- **Task & Habit Tracking** — create tasks, set reminders, log habits
- **WhatsApp & SMS** — send messages through Whapi and Twilio integrations
- **Memory** — conversation history and behavioural pattern learning across sessions
- **Multi-agent Pipeline** — a LangGraph state graph coordinates retrieval, planning, and execution

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│               Frontend  (Next.js + Tailwind)             │
│       Chat UI  •  Voice Input/Output  •  Dark Theme      │
└───────────────────────────┬──────────────────────────────┘
                            │  /chat  /voice-to-text  /text-to-voice
                            ▼
┌──────────────────────────────────────────────────────────┐
│                    Backend API  (FastAPI)                 │
│   /chat  /confirm  /voice-*   │  /knowledge  /auth/*     │
│   (port 8001)                 │  (port 8000)             │
└───────────────────────────┬──────────────────────────────┘
                            │
                     ┌──────▼──────┐
                     │  LangGraph  │
                     │  Workflow   │
                     └──────┬──────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
   ┌──────────┐       ┌──────────┐        ┌──────────┐
   │ Retriever│       │ Planner  │        │ Executor │
   │  Agent   │       │  Agent   │        │  Agent   │
   └────┬─────┘       └────┬─────┘        └────┬─────┘
        │                  │                   │
        ▼                  ▼                   ▼
   ┌─────────┐      ┌────────────┐      ┌───────────┐
   │ Memory  │      │Task Decomp │      │  Toolbox  │
   │ Manager │      │Action Plan │      │  (5 tools)│
   └─────────┘      └────────────┘      └───────────┘
        │
    ┌───┴────┐
    ▼        ▼
 SQLite   Azure AI
  ORM     Search
```

### Request Pipeline

1. **Safety Check** — input validation, injection detection, rate limiting
2. **Retriever** — query expansion + hybrid vector/keyword search + structured DB lookup
3. **Planner** — LLM-driven strategy selection: reasoning, planning, or direct action
4. **Task Decomposer** — breaks the strategy into discrete executable tasks
5. **Action Planner** — maps tasks to tool calls with typed parameters
6. **Confirmation** — human-in-the-loop gate before irreversible actions
7. **Executor** — runs tools and generates the final output
8. **Learning** — tracks behaviour patterns and user preferences over time
9. **Response** — persists the conversation and returns a structured result

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + React 18 + TailwindCSS |
| Voice | Azure Speech SDK (STT + TTS) |
| LLM | Azure OpenAI GPT-4o |
| Embeddings | Azure OpenAI text-embedding-3-small (1536 dims) |
| Vector Search | Azure AI Search (HNSW index) |
| Relational DB | SQLAlchemy async + SQLite (dev) / PostgreSQL (prod) |
| Workflow | LangGraph StateGraph |
| API | FastAPI + Uvicorn |
| Auth | JWT (HS256) via python-jose |
| Document Parsing | PyMuPDF, python-docx, python-pptx |
| Containerisation | Docker + Docker Compose |

---

## Getting Started

### Option A — Docker

```bash
cp .env.example .env
# Fill in your Azure credentials in .env
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:3000 |
| Assistant API | http://localhost:8001 |
| Core API | http://localhost:8000 |

### Option B — Local

**Backend**

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your Azure credentials in .env

python main.py                                        # Core API on :8000
python -m uvicorn backend.api.server:app --port 8001  # Assistant API on :8001
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Configuration

Copy `.env.example` to `.env` and set the following:

```env
# Required — Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Required — Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=your-index-name

# Optional — Voice
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus

# Optional — WhatsApp (Whapi)
WHAPI_TOKEN=your-whapi-token

# Optional — SMS (Twilio)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890

# Security
SECRET_KEY=your-random-secret-key   # python -c "import secrets; print(secrets.token_hex(32))"
DEBUG=false
```

The system runs with in-memory vector search and local SQLite if no Azure credentials are provided.

---

## API Reference

### Assistant API — port 8001

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message; receive an agent response |
| `POST` | `/confirm` | Confirm or reject a pending action |
| `POST` | `/voice-to-text` | Audio file → transcribed text |
| `POST` | `/text-to-voice` | Text → WAV audio response |
| `POST` | `/voice-to-voice` | Audio in → agent → audio out |
| `GET` | `/health` | Service health + voice availability |

### Core API — port 8000

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health and service status |
| `POST` | `/auth/register` | Create a new account |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `POST` | `/knowledge/query` | Query the knowledge base |
| `POST` | `/documents/upload` | Upload and ingest a document |
| `GET` | `/documents` | List ingested documents |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks |
| `POST` | `/reminders` | Create a reminder |
| `GET` | `/reminders` | List reminders |
| `POST` | `/habits` | Create a habit |
| `GET` | `/habits` | List habits |
| `POST` | `/habits/{id}/log` | Log a habit completion |
| `GET` | `/conversations` | Retrieve conversation history |

---

## Project Structure

```
├── main.py                         # Entry point
├── requirements.txt
├── docker-compose.yml
├── api/
│   └── api_server.py               # Core API (auth, documents, tasks, habits)
├── backend/
│   ├── api/server.py               # Assistant API (chat, voice, confirm)
│   ├── services/
│   │   ├── agent_service.py
│   │   └── voice_service.py
│   └── models/request_models.py
├── frontend/
│   └── src/
│       ├── pages/index.tsx
│       ├── components/
│       │   ├── Header.tsx
│       │   ├── ChatWindow.tsx
│       │   ├── ChatBubble.tsx
│       │   ├── ChatInput.tsx
│       │   └── TypingIndicator.tsx
│       └── services/api.ts
├── app/
│   ├── agents/
│   │   ├── retriever/retriever.py
│   │   ├── planner/planner.py
│   │   ├── planner/task_decomposer.py
│   │   ├── planner/action_planner.py
│   │   └── executor/executor.py
│   ├── graph/workflow.py
│   ├── learning/behavior_analyzer.py
│   ├── memory/
│   │   ├── memory_manager.py
│   │   ├── structured_db.py
│   │   └── vector_db.py
│   ├── safety/safety_check.py
│   ├── toolbox/toolbox.py
│   ├── tools/                      # email, sms, whatsapp, reminder, habit_tracker
│   └── utils/
│       ├── azure_llm.py
│       ├── azure_search.py
│       ├── config.py
│       └── logger.py
└── Dockerfile
```

---

## License

MIT
