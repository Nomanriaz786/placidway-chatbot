"""HTTP layer: chat, lead capture, refresh, and the React page."""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from .limits import Cooldown, DailyQuota, RateLimiter
from .schemas import ChatRequest, LeadRequest


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **row}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def create_app(answer_fn, refresh_fn, data_dir: Path, rate_limit: int = 20, daily_limit: int = 100,
               refresh_cooldown: int = 600, status_fn=lambda: {}, frontend_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="PlacidWay knowledge chatbot", docs_url=None, redoc_url=None)
    per_ip = RateLimiter(per_minute=rate_limit)
    daily = DailyQuota(limit=daily_limit, path=data_dir / "usage.json")
    refresh_window = Cooldown(seconds=refresh_cooldown)

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.get("/api/status")
    def status():
        """Public: when the content was last updated and how much is indexed. Nothing sensitive."""
        return status_fn()

    @app.post("/api/chat")
    def chat(body: ChatRequest, request: Request):
        if not per_ip.allow(request.client.host if request.client else "unknown"):
            raise HTTPException(429, "Too many questions in a minute. Please wait a moment.")
        if not daily.take():
            raise HTTPException(429, "We've reached today's question limit. Please try again tomorrow.")
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
    def refresh():
        if not refresh_window.try_start():
            minutes = max(1, math.ceil(refresh_window.seconds_left() / 60))
            raise HTTPException(429, f"Content was refreshed recently. Please try again in {minutes} minute{'s' if minutes > 1 else ''}.")
        try:
            return refresh_fn()
        except Exception as exc:  # the old index stays live; a blocked crawl must not take the bot down
            raise HTTPException(502, "Could not fetch the PlacidWay pages from this server. Still answering from the current content.") from exc

    if frontend_dist and frontend_dist.exists():
        # Mounted last so /api/* routes take priority over the static files.
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

    return app
