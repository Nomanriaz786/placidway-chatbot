"""HTTP layer: chat, lead capture, refresh, and the React page."""

import hmac
import json
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from .schemas import ChatRequest, LeadRequest


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **row}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def create_app(answer_fn, refresh_fn, data_dir: Path, admin_token: str, rate_limit: int = 20,
               frontend_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="PlacidWay knowledge chatbot", docs_url=None, redoc_url=None)
    hits: dict[str, deque] = defaultdict(deque)
    lock = threading.Lock()

    def limited(ip: str) -> bool:
        # shortcut: in-memory, per process; fine for one VPS process, use Redis if this ever scales out
        now = time.monotonic()
        with lock:
            q = hits[ip]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= rate_limit:
                return True
            q.append(now)
            return False

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.post("/api/chat")
    def chat(body: ChatRequest, request: Request):
        if limited(request.client.host if request.client else "unknown"):
            raise HTTPException(429, "Too many questions in a minute. Please wait a moment.")
        history = [m.model_dump() for m in body.messages]
        result = answer_fn(history)
        if not result["grounded"]:
            _append(data_dir / "unanswered.jsonl", {"question": history[-1]["content"], "reason": result["reason"]})
        result.pop("reason", None)
        return result

    @app.post("/api/lead")
    def lead(body: LeadRequest):
        _append(data_dir / "leads.jsonl", body.model_dump())
        return {"ok": True}

    @app.post("/api/refresh")
    def refresh(x_admin_token: str = Header(default="")):
        if not admin_token or not hmac.compare_digest(x_admin_token, admin_token):
            raise HTTPException(401, "invalid token")
        try:
            return refresh_fn()
        except Exception as exc:  # the old index stays live; a blocked crawl must not take the bot down
            raise HTTPException(502, f"Refresh failed ({exc.__class__.__name__}); still serving the current index.") from exc

    if frontend_dist and frontend_dist.exists():
        # Mounted last so /api/* routes take priority over the static files.
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    return app
