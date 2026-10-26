"""Crawl the 7 source pages and write data/index.json.

Usage (from backend/):  python -m scripts.build_index

PlacidWay blocks some datacenter IP ranges, so if the server's own refresh is
refused, run this from an allowed network and copy data/index.json to the
server's data/ folder, then restart the service.
"""

from langchain_openai import OpenAIEmbeddings

from chatbot import config
from chatbot.ingestion import build_index

if __name__ == "__main__":
    stats = build_index(OpenAIEmbeddings(model=config.EMBED_MODEL), config.INDEX_PATH)
    print(f"{stats['pages']} pages, {stats['chunks']} chunks -> {config.INDEX_PATH}")
