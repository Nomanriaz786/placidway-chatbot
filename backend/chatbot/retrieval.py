"""Hybrid retrieval: vector search for meaning, BM25 for exact words, merged by rank."""

import re

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


# Patients say "price", pages say "Total Cost": treat these words as one for keyword search.
_SAME_AS_COST = {"price", "prices", "pricing", "priced", "cost", "costs", "fee", "fees", "charge", "charges"}


def _tokens(text: str) -> list[str]:
    return ["cost" if t in _SAME_AS_COST else t for t in re.findall(r"[a-z0-9$]+", text.lower())]


def reciprocal_rank_fusion(result_lists: list[list[Document]], k: int = 60) -> list[Document]:
    """Score each document by 1/(k + rank) in every list it appears in, then sort by total score."""
    scores: dict[str, float] = {}
    docs: dict[str, Document] = {}
    for results in result_lists:
        for rank, d in enumerate(results):
            key = d.page_content
            docs.setdefault(key, d)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
    return [docs[key] for key in sorted(scores, key=scores.get, reverse=True)]


_COST_QUESTION = re.compile(r"how much|price|cost|fee|charge|cheap|expensive|usd|\$|cuánto|precio|كم|سعر", re.IGNORECASE)
_HAS_PRICE = re.compile(r"\$\s?\d|\bUSD\b", re.IGNORECASE)


class HybridRetriever:
    def __init__(self, vector_store, chunks: list[Document], k: int = 10, extra_price_passages: int = 4):
        self.vector_store = vector_store
        self.bm25 = BM25Retriever.from_documents(chunks, preprocess_func=_tokens, k=k)
        self.price_chunks = [c for c in chunks if _HAS_PRICE.search(c.page_content)]
        self.k = k
        self.extra_price_passages = extra_price_passages

    def search(self, query: str) -> list[Document]:
        semantic = self.vector_store.similarity_search(query, k=self.k)
        keyword = self.bm25.invoke(query)
        results = reciprocal_rank_fusion([semantic, keyword])[: self.k]
        if _COST_QUESTION.search(query):
            results += self._price_passages_for(results)
        return results

    def _price_passages_for(self, results: list[Document]) -> list[Document]:
        """Price tables rarely win on similarity, so for cost questions add the price passages of the top pages."""
        top_pages = list(dict.fromkeys(d.metadata["source"] for d in results[:3]))
        seen = {d.page_content for d in results}
        extra = [c for c in self.price_chunks if c.metadata["source"] in top_pages and c.page_content not in seen]
        return extra[: self.extra_price_passages]
