"""Cost protection for a public chatbot: a per-IP rate limit and a site-wide daily quota."""

import json
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


class RateLimiter:
    """At most `per_minute` requests per IP in any 60-second window.

    shortcut: in-memory and per process; fine for one VPS process, use Redis if this ever scales out.
    """

    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, ip: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[ip]
            while hits and now - hits[0] > 60:
                hits.popleft()
            if len(hits) >= self.per_minute:
                return False
            hits.append(now)
            return True


class DailyQuota:
    """At most `limit` questions per UTC day across all visitors, saved to disk so restarts don't reset it."""

    def __init__(self, limit: int, path: Path, today=utc_today):
        self.limit = limit
        self.path = path
        self.today = today
        self._lock = threading.Lock()

    def take(self) -> bool:
        with self._lock:
            day = self.today()
            usage = self._read()
            used = usage.get("count", 0) if usage.get("date") == day else 0
            if used >= self.limit:
                return False
            self._write({"date": day, "count": used + 1})
            return True

    def _read(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return {}

    def _write(self, usage: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(usage), encoding="utf-8")


class Cooldown:
    """One attempt per `seconds` window for the whole site, so a public button cannot hammer the source site."""

    def __init__(self, seconds: int, clock=time.monotonic):
        self.seconds = seconds
        self.clock = clock
        self._last: float | None = None
        self._lock = threading.Lock()

    def try_start(self) -> bool:
        with self._lock:
            now = self.clock()
            if self._last is not None and now - self._last < self.seconds:
                return False
            self._last = now
            return True

    def seconds_left(self) -> int:
        if self._last is None:
            return 0
        return max(0, round(self.seconds - (self.clock() - self._last)))
