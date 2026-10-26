"""Load the 7 source pages, clean them, chunk them and build the vector index."""

import re
import urllib.robotparser
from pathlib import Path

import requests
from bs4 import SoupStrainer
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .sources import SOURCES, USER_AGENT

# Site chrome that survives inside <main> and would pollute retrieval.
_NOISE = [
    re.compile(r"What treatment\? Any Procedure Any Destination What treatment Centers Packages\s*"),
    re.compile(r"English Arabic Chinese \(Simplified\) Chinese \(Traditional\) French German Indonesian "
               r"Italian Japanese Korean Romanian Russian Spanish Thai Turkish Vietnamese Urdu\s*"),
]


def clean_text(text: str) -> str:
    for pattern in _NOISE:
        text = pattern.sub(" ", text)
    return " ".join(text.split())


def allowed_by_robots(urls: list[str]) -> list[str]:
    robots = requests.get("https://www.placidway.com/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(robots.text.splitlines())
    return [u for u in urls if parser.can_fetch(USER_AGENT, u)]


def load_pages(urls: list[str]) -> list[Document]:
    loader = WebBaseLoader(
        web_paths=urls,
        header_template={"User-Agent": USER_AGENT},
        requests_per_second=1,  # the brief asks for about one request per second
        encoding="utf-8",
        bs_kwargs={"parse_only": SoupStrainer("main")},
        bs_get_text_kwargs={"separator": " "},
        raise_for_status=True,
        show_progress=False,
    )
    docs = loader.load()  # sequential, honours requests_per_second via its own rate limiter
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
    return [d for d in docs if d.page_content]


def split_into_chunks(docs: list[Document], titles: dict[str, str]) -> list[Document]:
    # ~1,000 characters keeps a price table row with its heading and "includes" text.
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150, separators=[". ", " ", ""])
    chunks = splitter.split_documents(docs)
    for c in chunks:
        url = c.metadata["source"]
        title = titles.get(url, url)
        c.metadata = {"source": url, "title": title}
        # The 3 package pages share most of their wording; the title tells them apart.
        c.page_content = f"[{title}] {c.page_content.lstrip('. ')}"
    return chunks


def build_index(embeddings, index_path: Path) -> dict:
    urls = allowed_by_robots(list(SOURCES))
    docs = load_pages(urls)
    chunks = split_into_chunks(docs, SOURCES)
    store = InMemoryVectorStore(embedding=embeddings)
    store.add_documents(chunks)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    store.dump(str(index_path))
    return {"pages": len(docs), "chunks": len(chunks), "skipped_by_robots": len(SOURCES) - len(urls)}
