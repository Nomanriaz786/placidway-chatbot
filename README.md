# PlacidWay Website Knowledge Chatbot

A chatbot that answers patient questions using only the content of seven PlacidWay pages, cites the page each answer came from, and says "I don't know" instead of guessing.

**Live:** https://placidway-assistant.duckdns.org

## How it works

```
7 PlacidWay URLs
   │  WebBaseLoader (robots.txt checked, clear User-Agent, 1 request/second, <main> content only)
   ▼
clean text ──► RecursiveCharacterTextSplitter (1,000 chars, 150 overlap, page title on every chunk)
   ▼
InMemoryVectorStore (OpenAI text-embedding-3-small), saved to data/index.json
   ▼
HybridRetriever: vector search + BM25 keyword search, merged with reciprocal rank fusion;
                 cost questions also get the price passages of the matched pages
   ▼
LangChain agent (create_agent, gpt-5.4-mini) with one tool, search_placidway,
returning a structured BotAnswer: answer, sources, answered, medical_topic, wants_quote
   ▼
Guardrails (plain code, not the model):
  • every cited URL must be a page that was actually retrieved this turn
  • every price in the answer must appear on a retrieved page (missing citations are added)
  • otherwise the reply is replaced with "I don't know" + the free-quote link
   ▼
FastAPI  ──►  React (Vite) single-page chat with source links, one-time medical disclaimer and quote form
```

## Why these choices

| Choice | Reason |
|---|---|
| **LangChain `WebBaseLoader`** | Standard loader with built-in rate limiting and custom headers; `SoupStrainer("main")` drops menus and footers at parse time. |
| **`create_agent` with one retrieval tool** | The model decides what to search, can search again with different words, and handles follow-ups ("what about recovery time?") from the chat history. |
| **Structured output (`BotAnswer`)** | Sources and the "answered" flag come back as fields, so code can check them instead of parsing prose. |
| **Hybrid retrieval** | The three package pages share most of their wording. Vector search finds meaning; BM25 catches exact words like "adenocarcinoma" or "cost". |
| **Code guardrails after the model** | The brief's top criterion is "never invent prices". A prompt asks for that; the guardrail enforces it. |
| **`InMemoryVectorStore`** | 7 pages, about 134 chunks. No database server to run or secure. Swapping to Chroma or pgvector only changes `server.py`. |
| **Stateless server** | The browser sends the last 10 messages with each question. Nothing about a conversation is stored on the server. |

## Project structure

```
backend/
  chatbot/
    config.py       settings from .env
    sources.py      the 7 allowed URLs, User-Agent, quote link
    ingestion.py    robots check, loading, cleaning, chunking, index build
    retrieval.py    hybrid retriever (vector + BM25 + rank fusion)
    prompts.py      system prompt and fallback answer
    schemas.py      BotAnswer and API request models
    agent.py        LangChain agent and the question-answer flow
    guardrails.py   citation and price checks
    limits.py       per-IP rate limit and site-wide daily quota
    api.py          FastAPI routes: chat, lead, refresh, health
    server.py       production wiring (models, index, refresh)
  scripts/build_index.py          crawls the 7 pages and writes data/index.json
  scripts/run_test_questions.py   runs the 8 test questions into docs/TEST_RESULTS.md
  tests/            pytest suite (no network or API calls)
frontend/           React + Vite chat page
docs/               test results and write-up
```

## Run it locally

Requirements: Python 3.11+, Node 18+, an OpenAI API key.

```bash
cp .env.example .env              # add OPENAI_API_KEY and a long random ADMIN_TOKEN
python -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt     # Windows: .venv\Scripts\pip

cd frontend && npm install && npm run build && cd ..

cd backend
../.venv/bin/python -m pytest                              # 34 tests, no API calls
../.venv/bin/uvicorn chatbot.server:app --port 8020       # builds the index on first start
```

Open http://127.0.0.1:8020.

## API

| Method | Path | Notes |
|---|---|---|
| POST | `/api/chat` | `{"messages": [{"role": "user", "content": "..."}]}`, up to 12 messages of 1,000 characters each; 20 requests per minute per IP; 100 questions per day for the whole site (`DAILY_LIMIT`) |
| POST | `/api/lead` | `{"name", "email", "question"}`, stored in `data/leads.jsonl` |
| POST | `/api/refresh` | header `X-Admin-Token`; re-crawls the 7 pages and swaps the index in when it is ready |
| GET | `/api/health` | liveness check |

Questions the bot could not answer are logged to `data/unanswered.jsonl` to show content gaps.

## Refreshing content

```bash
curl -X POST https://<host>/api/refresh -H "X-Admin-Token: $ADMIN_TOKEN"
```

The refresh re-crawls the 7 pages and swaps in the new index only when the crawl succeeds. If the crawl fails, the endpoint returns 502 and the bot keeps answering from the current index.

PlacidWay's site currently refuses requests from the hosting provider's IP range (HTTP 403), so on the live server the index is built from an allowed network with `python -m scripts.build_index` and copied to `data/index.json`. Allowlisting the server's IP would let `/api/refresh` work on the server directly. The crawler never disguises itself: it always sends its own User-Agent and follows robots.txt.

## Security

- The OpenAI key and admin token live only in the server's `.env` (git-ignored); nothing secret reaches the browser.
- Strict request validation (roles, lengths, message count), per-IP rate limiting, and a constant-time admin-token comparison.
- A site-wide daily quota (100 questions per UTC day by default, saved in `data/usage.json`) caps API cost while keeping the demo public, with no login.
- The crawler fetches only the 7 listed URLs and respects robots.txt.

## Tools and models

Python 3.13, FastAPI, LangChain 1.4 (`create_agent`, `WebBaseLoader`, `InMemoryVectorStore`, `BM25Retriever`), OpenAI `gpt-5.4-mini` and `text-embedding-3-small`, React 18, Vite 5.

See [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md) for the 8 test questions and [docs/WRITEUP.md](docs/WRITEUP.md) for limitations and next steps.
