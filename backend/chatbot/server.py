"""Production wiring: real models, the saved index, and refresh. Run with: uvicorn chatbot.server:app"""

import json
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from . import config
from .agent import answer_question, build_agent
from .api import create_app
from .ingestion import build_index
from .retrieval import HybridRetriever

embeddings = OpenAIEmbeddings(model=config.EMBED_MODEL)
model = ChatOpenAI(model=config.CHAT_MODEL, temperature=0, timeout=60)


def _load_agent():
    if not config.INDEX_PATH.exists():
        build_index(embeddings, config.INDEX_PATH)
    store = InMemoryVectorStore.load(str(config.INDEX_PATH), embeddings)
    chunks = [Document(page_content=r["text"], metadata=r["metadata"]) for r in store.store.values()]
    return build_agent(model, HybridRetriever(store, chunks))


state = {"agent": _load_agent()}


_status_cache: dict = {}


def content_status() -> dict:
    """Last update time and size of the saved index; re-read only when index.json changes."""
    mtime = config.INDEX_PATH.stat().st_mtime
    if _status_cache.get("mtime") != mtime:
        records = json.loads(config.INDEX_PATH.read_text(encoding="utf-8")).values()
        _status_cache.update(mtime=mtime, status={
            "updated_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(timespec="seconds"),
            "pages": len({r["metadata"]["source"] for r in records}),
            "passages": len(records),
        })
    return _status_cache["status"]


def refresh() -> dict:
    stats = build_index(embeddings, config.INDEX_PATH)
    state["agent"] = _load_agent()  # swap in the new index only after it is fully built
    return stats


app = create_app(
    answer_fn=lambda history: answer_question(state["agent"], history),
    refresh_fn=refresh,
    data_dir=config.DATA_DIR,
    daily_limit=config.DAILY_LIMIT,
    refresh_cooldown=config.REFRESH_COOLDOWN,
    status_fn=content_status,
    frontend_dist=config.FRONTEND_DIST,
)
