# Cognix — Implementation Handbook

> **Who this is for:** A B.Tech CSE AIML student building their first serious full-stack AI project.
> **How to use this:** Read each phase top to bottom. Do not jump ahead. Each phase builds on the previous one.
> **Golden rule:** A working simple version beats an unfinished complex one. Always.

---

## What Is Cognix? (Plain English)

Cognix is an AI-powered research assistant. The user types a topic like *"Impact of AI in healthcare"*, and the system:

1. Breaks the topic into focused research questions
2. Searches the web for real sources
3. Scores each source for quality and relevance
4. Reads and summarizes the useful ones
5. Checks if it has gathered enough information
6. Writes a full markdown research report
7. Lets the user ask follow-up questions, answered using the researched material

The user watches all of this happen in real time on screen — step by step.

This is what makes it impressive: it is not just "call ChatGPT and show the output." It is a controlled, observable, multi-step AI workflow that plans, searches, evaluates, and writes — with the user watching every step.

---

## Why This Project Is Strong for Your Resume

| What you build | What it shows interviewers |
|---|---|
| LangGraph agentic workflow | You understand AI orchestration, not just LLM calls |
| RAG chat on session data | You understand how real AI apps use retrieved context |
| pgvector in PostgreSQL | You understand vector search without a separate vector DB |
| SSE real-time progress stream | You understand async backend patterns |
| Source evaluation + scoring | You understand AI judgment and structured output |
| LangSmith tracing | You understand AI observability |
| Full-stack deployment | You can ship something real |

---

## Tech Stack (With Simple Explanations)

### Backend
| Tool | What it does | Why we use it |
|---|---|---|
| **FastAPI** | Python web framework | Fast, modern, async-ready, great docs |
| **PostgreSQL** | Main database | Stores everything: users, sessions, reports, chat |
| **pgvector** | Plugin for PostgreSQL | Lets PostgreSQL store and search embeddings (no separate vector DB needed) |
| **SQLAlchemy (async)** | Talk to the database from Python | Clean, industry-standard ORM |
| **Alembic** | Manage database schema changes | Like Git for your database tables |
| **uv** | Python package manager | Faster and simpler than pip |

### AI / Agentic Layer
| Tool | What it does | Why we use it |
|---|---|---|
| **LangGraph** | Builds the step-by-step AI workflow | Industry-standard for agentic AI systems |
| **Groq API** | The LLM (language model) | Very fast, has a generous free tier |
| **Tavily API** | Web search | Built for AI agents, returns clean structured results |
| **OpenAI Embeddings API** | Converts text to vectors | Reliable and widely used (`text-embedding-3-small`) |
| **BeautifulSoup** | Reads and cleans web page content | Simple Python library, no API needed |
| **LangSmith** | Traces and logs every LLM call | Free tier, lets you debug and demo the AI workflow visually |

### Frontend
| Tool | What it does | Why we use it |
|---|---|---|
| **Next.js (App Router)** | React framework | Industry standard for modern web apps |
| **TypeScript** | JavaScript with types | Catches bugs early, expected in professional projects |
| **Tailwind CSS** | Styling utility classes | Fast to write, no custom CSS files needed |
| **shadcn/ui** | Ready-made polished UI components | Looks professional with minimal effort |
| **Zustand** | Manage app state (like logged-in user) | Much simpler than Redux |
| **Axios** | Make API calls from the frontend | Simple and widely used |

### Deployment
| Service | What you deploy there | Cost |
|---|---|---|
| **Vercel** | Next.js frontend | Free tier |
| **Render** | FastAPI backend | Free tier |
| **Neon** | PostgreSQL + pgvector | Free tier, pgvector supported out of the box |

---

## Project Folder Structure

```
cognix/
├── backend/
│   ├── app/
│   │   ├── api/          ← HTTP route files (thin, no business logic here)
│   │   ├── core/         ← Settings, JWT security, shared dependencies
│   │   ├── database/     ← DB connection setup
│   │   ├── models/       ← SQLAlchemy table definitions
│   │   ├── schemas/      ← Pydantic request/response shapes
│   │   ├── services/     ← All business logic lives here
│   │   ├── graph/        ← LangGraph workflow definition
│   │   └── main.py       ← App entry point
│   ├── alembic/          ← Migration files (auto-generated)
│   ├── pyproject.toml    ← Dependencies
│   └── .env.example      ← Environment variable template
│
├── frontend/
│   ├── app/              ← Next.js App Router pages
│   ├── components/       ← Reusable UI components
│   ├── lib/              ← API client, helpers
│   ├── store/            ← Zustand state stores
│   └── types/            ← TypeScript type definitions
│
├── README.md
└── .gitignore
```

**Rule to remember:** Routes only handle HTTP. Services do all the work. Nodes in LangGraph only call services — they do not contain logic themselves. Keep things separated.

---

## Database Tables

Think of these as spreadsheets. Each table is one kind of data.

### `users`
Stores registered accounts.
```
id | email | password_hash | created_at
```

### `research_sessions`
One row per research job the user starts.
```
id | user_id | topic | status | current_step | report_markdown | error_message | created_at | updated_at
```
`status` and `current_step` drive the live progress stream.

### `research_questions`
The questions the AI planner generates for a topic.
```
id | session_id | question | created_at
```

### `research_sources`
Each web source found and evaluated.
```
id | session_id | title | source_url | snippet | relevance_score | credibility_score | usefulness_score | extracted_text | summary | created_at
```

### `document_chunks`
The extracted text broken into small pieces, stored with their vector embeddings for RAG search.
```
id | session_id | source_id | chunk_index | content | embedding (VECTOR 1536) | created_at
```

### `chat_messages`
Every message in the chat (both user and assistant).
```
id | session_id | role | content | created_at
```

---

## Session Status Flow

The `status` field on a session moves through these values as the workflow runs. This is what drives the live progress stepper on the frontend.

```
pending → planning → searching → evaluating_sources → extracting
→ summarizing → checking_sufficiency → embedding → generating_report
→ completed
                                            (or) → failed
```

---

## API Endpoints

### Auth
```
POST   /auth/signup       ← Create account
POST   /auth/login        ← Get JWT token
GET    /auth/me           ← Get current user info
```

### Sessions
```
POST   /sessions                        ← Create a new research session
GET    /sessions                        ← List all sessions for the logged-in user
GET    /sessions/{session_id}           ← Get one session's full details
POST   /sessions/{session_id}/run       ← Start the agentic workflow (async)
GET    /sessions/{session_id}/progress  ← SSE stream of real-time step updates
```

### Chat
```
POST   /sessions/{session_id}/chat      ← Send a message, get RAG-based reply
GET    /sessions/{session_id}/messages  ← Load full chat history
```

### Optional (add after core is done)
```
GET    /sessions/{session_id}/sources   ← Get all evaluated sources
GET    /sessions/{session_id}/questions ← Get all research questions
```

---

## The Agentic Workflow (How It Works Inside)

This is the heart of the project. The workflow is a series of steps connected by LangGraph.

### Hard limits (keep the AI predictable and cheap)
- Maximum **4 research questions** per topic
- Maximum **8 final sources** used
- Maximum **2 search passes** total
- Maximum **1 retry** if sufficiency check fails
- Chunk size: **800 tokens**

### The LangGraph State (what gets passed between steps)

```python
class ResearchState(TypedDict):
    session_id: int
    topic: str
    questions: list[str]
    search_results: list[dict]
    selected_sources: list[dict]
    extracted_sources: list[dict]
    summaries: list[str]
    enough_information: bool
    missing_areas: list[str]
    retry_count: int          # never goes above 1
    report_markdown: str
```

### The Workflow Nodes

Each node does one thing and updates the session status in the database.

```
[planner_node]
    ↓
[search_node]
    ↓
[evaluator_node]
    ↓
[extraction_node]
    ↓
[summarization_node]
    ↓
[sufficiency_node] ──→ (if not enough AND retry_count < 1) ──→ [search_node]
    ↓ (if enough, or retry used up)
[embedding_node]
    ↓
[report_node]
    ↓
  DONE
```

### What each node does

**planner_node**
- Calls the LLM with the topic
- Gets back 3–4 focused research questions
- Saves questions to the database
- Updates session status to `planning`

**search_node**
- For each research question, calls Tavily search
- Collects raw search results (URL, title, snippet)
- Updates session status to `searching`

**evaluator_node**
- For each result, asks the LLM to score it: relevance (1–5), credibility (1–5), usefulness (1–5)
- Keeps the top 8 by total score
- Saves scores to the database
- Updates session status to `evaluating_sources`

**extraction_node**
- For each selected source, downloads the web page using `httpx`
- Cleans the HTML using BeautifulSoup (keeps only main text)
- Saves extracted text to the database
- Skips pages that cannot be scraped (no crashing)
- Updates session status to `extracting`

**summarization_node**
- For each extracted source, asks the LLM to write a 2–3 paragraph summary
- Saves summaries to the database
- Updates session status to `summarizing`

**sufficiency_node**
- Feeds all summaries to the LLM
- Asks: "Is this enough to write a complete report on [topic]? What is missing?"
- Gets back `enough: true/false` and a list of missing areas
- If not enough and retry count is 0, goes back to search_node with refined questions
- Otherwise, continues forward
- Updates session status to `checking_sufficiency`

**embedding_node**
- Splits extracted text into ~800-token chunks
- Calls OpenAI Embeddings API to get a vector for each chunk
- Saves chunks + vectors to the `document_chunks` table using pgvector
- Updates session status to `embedding`

**report_node**
- Feeds all summaries, questions, and topic to the LLM
- Asks for a complete structured markdown report
- Saves the markdown to the session's `report_markdown` column
- Updates session status to `completed`

---

## How Async Workflow + SSE Works

The research workflow takes 30–90 seconds. You cannot make the user wait for an HTTP response that long.

**The pattern:**

1. User hits `POST /sessions/{id}/run`
2. Backend starts the workflow in the background using `asyncio.create_task`
3. Backend immediately returns `{"status": "started"}` — the HTTP request ends here
4. Meanwhile, the workflow runs in the background, updating the session's `current_step` at each node
5. The frontend connects to `GET /sessions/{id}/progress` — this is the SSE endpoint
6. The SSE endpoint polls the database every second and streams the current step to the browser
7. The frontend reads this stream and lights up the progress stepper in real time
8. When the step reaches `completed` or `failed`, the SSE stream closes

```python
# Route: start workflow
@router.post("/sessions/{session_id}/run")
async def run_research(session_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify session belongs to user
    session = await get_session_or_404(db, session_id, current_user.id)
    # Start workflow in background — does NOT block the response
    asyncio.create_task(run_workflow(session_id))
    return {"status": "started"}

# Route: SSE progress stream
@router.get("/sessions/{session_id}/progress")
async def stream_progress(session_id: int, db: AsyncSession = Depends(get_db)):
    async def event_generator():
        while True:
            session = await get_session(db, session_id)
            data = {"step": session.current_step, "status": session.status}
            yield f"data: {json.dumps(data)}\n\n"
            if session.status in ("completed", "failed"):
                break
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## How RAG Chat Works

RAG = Retrieval-Augmented Generation. Instead of asking the LLM to answer from memory, you find the most relevant pieces of text from your own stored data and include them in the prompt.

**Step by step:**

1. User types a question in the chat
2. Backend converts the question into a vector using the Embeddings API
3. pgvector searches the `document_chunks` table for the most similar chunks — filtered by `session_id`
4. Backend takes the top 5 chunks and builds a prompt:
   ```
   You are a research assistant. Answer the question using only the context below.
   Context: [chunk 1] [chunk 2] [chunk 3] ...
   Question: [user's question]
   ```
5. LLM answers using only that context
6. Both the user message and the assistant reply are saved to `chat_messages`
7. Next time the user opens the session, the full chat history loads

**Why filter by `session_id`?** Each session has its own researched material. The vectors from "AI in healthcare" should not mix with vectors from "climate change." The filter keeps each session's chat grounded in its own data.

---

## Error Handling (Simple Rules)

| What goes wrong | What to do |
|---|---|
| Tavily search fails | Retry once. If it fails again, continue with whatever results you have. |
| LLM returns bad JSON | Retry the call with a stricter prompt. Max 2 retries. |
| Web page can't be scraped | Skip it. Log a warning. Move on. |
| Embedding API fails | Retry once. If it fails again, set session status to `failed`. |
| Any unexpected crash | Catch it at the workflow level. Set status to `failed`. Save the error message. |

**Golden rule for error handling:** The session must NEVER get stuck in `searching` or `extracting` forever. Always update the status — even if it is `failed`.

---

## LangSmith Setup (2 Minutes, Worth It)

LangSmith traces every LLM call automatically. You can show interviewers the exact trace of a full research workflow — inputs, outputs, token usage, latency.

Add these to your `.env` file:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key_from_smith.langchain.com
LANGCHAIN_PROJECT=cognix
```

That's it. LangChain and LangGraph will send traces automatically.

---

## Build Phases (Your Recipe)

Follow these in order. Do not start Phase 5 until Phase 4 is working.

---

### Phase 1 — Backend Foundation
**Estimated time: 1–2 days**
**Goal: Backend runs, database connects, health check works.**

1. Create the `cognix/backend/` folder
2. Install `uv` and set up the project: `uv init`
3. Add dependencies: `fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `python-dotenv`, `pydantic-settings`
4. Create `main.py` with a `/health` route that returns `{"status": "ok"}`
5. Create `core/config.py` using `pydantic-settings` to load `.env` variables
6. Create `database/connection.py` with async SQLAlchemy engine and session factory
7. Enable pgvector in your Neon database: run `CREATE EXTENSION IF NOT EXISTS vector;`
8. Set up Alembic: `alembic init alembic`
9. Run the backend: `uvicorn app.main:app --reload`

✅ **Done when:** `/health` returns 200, database connection does not error.

---

### Phase 2 — Authentication
**Estimated time: 1–2 days**
**Goal: Users can sign up, log in, and protected routes work.**

1. Add dependencies: `passlib[bcrypt]`, `python-jose[cryptography]`
2. Create `models/user.py` — the User SQLAlchemy model
3. Run `alembic revision --autogenerate -m "add users table"` and `alembic upgrade head`
4. Create `core/security.py` — functions for hashing passwords and creating/verifying JWTs
5. Create `schemas/auth.py` — Pydantic models for signup/login request and response
6. Create `api/auth.py` — the three routes: `/auth/signup`, `/auth/login`, `/auth/me`
7. Create `core/dependencies.py` — the `get_current_user` dependency that reads the JWT from the Authorization header

✅ **Done when:** You can sign up via Postman, log in and get a token, and call `/auth/me` with that token.

---

### Phase 3 — Session Base
**Estimated time: 1 day**
**Goal: Users can create and list research sessions.**

1. Create `models/session.py` — the ResearchSession, ResearchQuestion, ResearchSource models
2. Run Alembic migration
3. Create `schemas/session.py` — request/response shapes
4. Create `api/sessions.py` — `POST /sessions`, `GET /sessions`, `GET /sessions/{id}`
5. All routes use `get_current_user` so only the owner can access their sessions

✅ **Done when:** You can create a session with a topic and list your sessions via Postman.

---

### Phase 4 — Core Services
**Estimated time: 3–4 days**
**Goal: Each AI/data service works on its own.**

Build each service as a standalone async function. Test each one individually in a simple script before wiring them together.

**`services/planner_service.py`**
```python
async def generate_questions(topic: str) -> list[str]:
    # Call Groq LLM
    # Prompt: "Generate 4 focused research questions for: {topic}"
    # Return list of question strings
```

**`services/search_service.py`**
```python
async def search_web(questions: list[str]) -> list[dict]:
    # For each question, call Tavily search API
    # Return list of {title, url, snippet, score}
```

**`services/evaluator_service.py`**
```python
async def evaluate_sources(sources: list[dict], topic: str) -> list[dict]:
    # For each source, ask LLM to score relevance, credibility, usefulness (1-5 each)
    # Sort by total score, return top 8
    # Use structured output / JSON mode in the LLM call
```

**`services/extraction_service.py`**
```python
async def extract_content(url: str) -> str:
    # Use httpx to download the page
    # Use BeautifulSoup to get only the text (strip nav, footer, ads)
    # Return cleaned text string
    # Return "" if the page can't be fetched — never crash
```

**`services/summarization_service.py`**
```python
async def summarize_source(extracted_text: str, topic: str) -> str:
    # Ask LLM: "Summarize this text in 2-3 paragraphs, focusing on {topic}"
    # Return summary string
```

**`services/sufficiency_service.py`**
```python
async def check_sufficiency(topic: str, summaries: list[str]) -> dict:
    # Ask LLM: "Given these summaries, is there enough info to write a report on {topic}?"
    # Return {"enough": True/False, "missing_areas": ["area1", "area2"]}
    # Use JSON mode
```

**`services/embedding_service.py`**
```python
async def embed_and_store(session_id: int, source_id: int, text: str, db):
    # Split text into ~800-token chunks
    # For each chunk, call OpenAI embeddings API
    # Save to document_chunks table with pgvector embedding
```

**`services/report_service.py`**
```python
async def generate_report(topic: str, questions: list, summaries: list) -> str:
    # Ask LLM to write a complete markdown research report
    # Include sections: Introduction, Key Findings, Source Summaries, Conclusion
    # Return markdown string
```

**`services/retrieval_service.py`**
```python
async def retrieve_chunks(session_id: int, query: str, db) -> list[str]:
    # Embed the query using OpenAI
    # Run pgvector similarity search filtered by session_id
    # Return top 5 chunk content strings
```

**`services/chat_service.py`**
```python
async def answer_question(session_id: int, question: str, db) -> str:
    # Call retrieval_service to get relevant chunks
    # Build prompt: "Answer using only this context: [chunks]\nQuestion: {question}"
    # Call LLM and return the answer string
```

✅ **Done when:** Each service function works when you call it directly in a test script.

---

### Phase 5 — LangGraph Workflow
**Estimated time: 2–3 days**
**Goal: `POST /sessions/{id}/run` triggers the full agentic pipeline.**

1. Create `graph/workflow.py`
2. Define `ResearchState` TypedDict (see the state definition above)
3. Build each node as a thin function that:
   - receives the state
   - calls the matching service
   - updates the session's `current_step` in the database
   - returns the updated state
4. Create the graph, add nodes, add edges, add the conditional edge from `sufficiency_node`
5. Compile the graph
6. Create `async def run_workflow(session_id: int)` that builds the initial state and calls `graph.ainvoke(state)`
7. In `api/sessions.py`, add `POST /sessions/{id}/run` that calls `asyncio.create_task(run_workflow(session_id))`

✅ **Done when:** Triggering the run endpoint causes the session status to move through all steps and ends at `completed` with a `report_markdown` saved.

---

### Phase 6 — SSE Progress Endpoint
**Estimated time: half a day**
**Goal: Frontend can watch live step updates.**

1. Add `GET /sessions/{session_id}/progress` to `api/sessions.py`
2. The endpoint returns a `StreamingResponse` with `media_type="text/event-stream"`
3. Inside, loop every 1 second: read `current_step` from the database, `yield` it as `data: {...}\n\n`
4. Stop the loop when status is `completed` or `failed`

✅ **Done when:** Hitting the endpoint in the browser shows live text appearing as the workflow progresses.

---

### Phase 7 — RAG Chat Backend
**Estimated time: 1 day**
**Goal: Users can ask questions about a session's research.**

1. Create `models/chat.py` — the ChatMessage model, and DocumentChunk model with pgvector column
2. Run Alembic migration — include `CREATE INDEX ... USING ivfflat` for the embedding column
3. Add `POST /sessions/{id}/chat` — calls `chat_service.answer_question`, saves both messages, returns the reply
4. Add `GET /sessions/{id}/messages` — returns all chat messages for the session

✅ **Done when:** You can send a question via Postman and get a relevant answer grounded in the session's research.

---

### Phase 8 — Frontend Foundation
**Estimated time: 1–2 days**
**Goal: Next.js app runs, auth works, API calls succeed.**

1. Create Next.js app: `npx create-next-app@latest frontend --typescript --tailwind --app`
2. Install shadcn/ui: `npx shadcn@latest init` — choose dark mode as default
3. Install extras: `npm install axios zustand react-markdown`
4. Create `lib/api.ts` — an Axios instance with base URL and auth token header
5. Create `store/authStore.ts` — Zustand store for `{ user, token, login, logout }`
6. Create a simple layout with a top navigation bar
7. Add route protection: if no token, redirect to `/login`

✅ **Done when:** App loads, you can log in, and the token is saved and sent on API calls.

---

### Phase 9 — Frontend Pages
**Estimated time: 3–4 days**
**Goal: The full user flow works from the browser.**

**Login page (`/login`)**
- Email + password fields using shadcn Input and Button
- Calls `POST /auth/login`, saves token, redirects to dashboard
- Shows error message on failure

**Signup page (`/signup`)**
- Same layout as login
- Calls `POST /auth/signup`

**Dashboard page (`/dashboard`)**
- Lists all research sessions (topic, status badge, date)
- "New Research" button → opens a dialog with a topic input field
- Clicking a session → navigates to `/sessions/[id]`

**Session detail page (`/sessions/[id]`)**

This is the main page. Build it in this order:

1. **Progress Stepper** — a vertical list of all step names. Connects to the SSE endpoint on load. Each step lights up (green check) as the workflow reaches it. Use a simple `EventSource` in a `useEffect`. This is the "wow" element of the whole project.

2. **Research Questions** — a list of the planned questions, shown after planning step completes.

3. **Sources section** — cards showing source title, URL, and the three scores. Shown after evaluating step.

4. **Markdown Report** — use `react-markdown` to render the report. Add `remark-gfm` for tables and lists. Shown after `completed`.

5. **Chat interface** — at the bottom of the page. Input box + send button. Messages appear above in a scrollable container. User messages on the right, assistant on the left.

✅ **Done when:** You can start a new research topic, watch the stepper light up, see the report render, and ask follow-up questions.

---

### Phase 10 — Resume Old Session Chat
**Estimated time: half a day**
**Goal: Old sessions can be reopened and continued.**

When navigating to `/sessions/[id]` for a completed session:
- Load session details (topic, report)
- Load sources
- Load existing chat messages from `GET /sessions/{id}/messages`
- Render them in the chat interface
- Allow new questions — they save as new messages in the same session

No new backend work needed — the existing routes handle this.

✅ **Done when:** Closing and reopening a session shows the full previous chat history.

---

### Phase 11 — Polish
**Estimated time: 1–2 days**
**Goal: The app feels complete and professional.**

- Add loading skeletons (shadcn Skeleton) while data is fetching
- Add empty states ("No sessions yet — start your first research!")
- Add toast notifications (shadcn Toast) for success and error messages
- Make the progress stepper animated (a simple CSS transition is fine)
- Test the full flow end to end at least 3 times with different topics
- Fix any crashes or stuck states you find

---

### Phase 12 — Deployment and README
**Estimated time: 1–2 days**
**Goal: Project is live, GitHub is clean, README is impressive.**

**Deploy backend to Render:**
1. Push backend to GitHub
2. Create new Web Service on Render, connect repo
3. Set build command: `uv sync`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables in Render's dashboard

**Deploy frontend to Vercel:**
1. Push frontend to GitHub
2. Import repo in Vercel
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL

**Set up Neon database:**
1. Create free account at neon.tech
2. Create a project — copy the connection string
3. Run `CREATE EXTENSION IF NOT EXISTS vector;` in the Neon SQL console
4. Run your Alembic migrations against the Neon URL

**Environment variables you need:**
```env
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=any-long-random-string
TAVILY_API_KEY=
GROQ_API_KEY=
OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=cognix
```

**README must include:**
- What the project does (2 sentences)
- Live demo link
- Tech stack list
- Architecture diagram (copy the text diagram from this plan)
- How to run locally (step by step)
- Screenshots of the progress stepper, report, and chat
- Your name and LinkedIn

---

## Common Mistakes to Avoid

| Mistake | What to do instead |
|---|---|
| Writing business logic inside a route file | Move it to a service function |
| Running the workflow synchronously in the HTTP request | Always use `asyncio.create_task` |
| Starting the frontend before the backend works | Backend first. Always. |
| Letting the workflow crash silently | Always catch exceptions, set status to `failed` |
| Skipping LangSmith setup | Takes 2 minutes, makes your demo 10x more impressive |
| Building Phase 5 before testing Phase 4 services | Test each service alone first |
| Letting the sufficiency checker loop forever | Hard limit: `if retry_count >= 1: continue anyway` |
| Using ChromaDB on Render | Use pgvector instead — no filesystem issues |

---

## What "Done" Looks Like

When Cognix V1 is complete, you can do this in a live demo:

1. Log in to the app
2. Click "New Research", type a topic
3. Watch the progress stepper light up step by step in real time
4. See the research questions appear
5. See source cards with scores appear
6. See the full markdown report render
7. Type a question in the chat and get a grounded, relevant answer
8. Open your LangSmith dashboard and show the full trace of the workflow to the interviewer

That is a complete, explainable, technically strong, real AI project — and most candidates at your level will not have anything close to it.

---

## After V1 (Ideas for V2)

Only look at these after V1 is fully working and deployed.

- Run searches for all questions in parallel (faster workflow)
- Add a WebSocket instead of SSE for bidirectional updates
- Add LangGraph state checkpointing (pause and resume a workflow)
- Add PDF export of the report
- Add better source reranking using a cross-encoder model
- Add a verification agent that fact-checks the report
- Add a background job queue (ARQ) for production scale

---

*Build in order. Ship each phase before starting the next. Cognix is impressive because it is complete — not because it is complex.*
