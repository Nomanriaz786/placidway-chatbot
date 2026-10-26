import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# WebBaseLoader reads USER_AGENT from the environment; set it before it is imported.
os.environ.setdefault("USER_AGENT", "PlacidWayAssessmentBot/1.0")

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.4-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
DATA_DIR = ROOT / os.getenv("DATA_DIR", "data")
INDEX_PATH = DATA_DIR / "index.json"
FRONTEND_DIST = ROOT / "frontend" / "dist"
