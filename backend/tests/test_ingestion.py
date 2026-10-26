from langchain_core.documents import Document

from chatbot.ingestion import clean_text, split_into_chunks

URL = "https://www.placidway.com/package/7903/x"


def test_clean_text_drops_search_widget_and_collapses_space():
    raw = "What treatment? Any Procedure Any Destination What treatment Centers Packages \n\n  Out-Patient Program 3 Weeks $18,995"
    assert clean_text(raw) == "Out-Patient Program 3 Weeks $18,995"


def test_clean_text_drops_language_menu():
    raw = "English Arabic Chinese (Simplified) Chinese (Traditional) French German Indonesian Italian Japanese Korean Romanian Russian Spanish Thai Turkish Vietnamese Urdu Real content here"
    assert clean_text(raw) == "Real content here"


def test_split_into_chunks_keeps_source_title_and_splits_long_pages():
    text = ("Out-Patient Program 3 Weeks $18,995. " * 80).strip()
    chunks = split_into_chunks([Document(page_content=text, metadata={"source": URL})], {URL: "Adeno package"})
    assert len(chunks) > 1
    assert all(c.metadata["source"] == URL and c.metadata["title"] == "Adeno package" for c in chunks)
    assert all(len(c.page_content) <= 1200 for c in chunks)
    assert all(c.page_content.startswith("[Adeno package] ") for c in chunks)
