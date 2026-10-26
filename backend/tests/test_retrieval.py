from langchain_core.documents import Document

from chatbot.retrieval import HybridRetriever, reciprocal_rank_fusion


def doc(i, text, url="u"):
    return Document(page_content=text, metadata={"source": url, "id": str(i)})


def test_price_words_match_each_other_in_keyword_search():
    from chatbot.retrieval import _tokens
    assert _tokens("Price list") == _tokens("cost list") == ["cost", "list"]
    assert "cost" in _tokens("Total Cost (USD), fees and pricing")


def test_rrf_rewards_documents_ranked_well_in_both_lists():
    a, b, c = doc(1, "a"), doc(2, "b"), doc(3, "c")
    fused = reciprocal_rank_fusion([[a, b, c], [b, c, a]])
    assert [d.page_content for d in fused] == ["b", "a", "c"]


def test_rrf_deduplicates_by_content():
    a = doc(1, "same text")
    fused = reciprocal_rank_fusion([[a], [doc(2, "same text")]])
    assert len(fused) == 1


class FakeVectorStore:
    def __init__(self, ranked):
        self.ranked = ranked

    def similarity_search(self, query, k):
        return self.ranked[:k]


def test_cost_questions_include_price_passages_of_the_matched_page():
    faq = [doc(i, f"[Adeno package] FAQ {i} adenocarcinoma care", url="adeno") for i in range(6)]
    table = doc(99, "[Adeno package] Out-Patient 3 Weeks $18,995", url="adeno")
    other_page_price = doc(98, "[Anal package] Out-Patient $18,995", url="anal")
    retriever = HybridRetriever(FakeVectorStore(faq), faq + [table, other_page_price], k=3)
    results = retriever.search("how much is adenocarcinoma care")
    assert table in results and other_page_price not in results


def test_non_cost_questions_do_not_get_extra_price_passages():
    faq = [doc(i, f"[Adeno package] FAQ {i} adenocarcinoma recovery", url="adeno") for i in range(6)]
    table = doc(99, "[Adeno package] Out-Patient 3 Weeks $18,995", url="adeno")
    results = HybridRetriever(FakeVectorStore(faq), faq + [table], k=3).search("adenocarcinoma recovery")
    assert table not in results


def test_keyword_match_is_pulled_in_even_when_vector_search_misses_it():
    faq = [doc(i, f"[Adeno package] FAQ answer number {i} about patient energy") for i in range(6)]
    table = doc(99, "[Adeno package] Program Type Duration Total Cost (USD) Out-Patient 3 Weeks $18,995")
    retriever = HybridRetriever(FakeVectorStore(faq), faq + [table], k=4)
    results = retriever.search("adeno package total cost")
    assert table in results and len(results) == 4
