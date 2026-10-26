from chatbot.guardrails import extract_prices, verify_answer

PRICE_PAGE = "https://www.placidway.com/price-list/5/x"
PACKAGE = "https://www.placidway.com/package/7903/x"

DOCS = [
    {"url": PRICE_PAGE, "text": "Breast Cancer $18995 Chat with Center. Colorectal Cancer 18995 USD"},
    {"url": PACKAGE, "text": "Package price starting from USD 12,500 includes 21 days of treatment."},
]


def test_extract_prices_reads_symbol_and_code_formats():
    assert extract_prices("from $18,995 or 12500 USD and USD 3,000") == {"18995", "12500", "3000"}


def test_extract_prices_reads_european_thousands_separator():
    # Spanish replies often write 18.995 USD
    assert extract_prices("cuesta 18.995 USD") == {"18995"}


def test_extract_prices_ignores_plain_numbers():
    assert extract_prices("21 days, 6 reviews, 2026") == set()


def test_grounded_answer_passes_and_keeps_its_sources():
    ok, reason, sources = verify_answer("Breast cancer costs $18,995 (USD).", [PRICE_PAGE], DOCS)
    assert ok, reason
    assert sources == [PRICE_PAGE]


def test_invented_price_fails():
    ok, reason, _ = verify_answer("It costs $9,999.", [PRICE_PAGE], DOCS)
    assert not ok and "9999" in reason


def test_citation_must_be_a_retrieved_page():
    ok, reason, _ = verify_answer("Breast cancer costs $18995.", ["https://example.com/made-up"], DOCS)
    assert not ok and "source" in reason


def test_answer_needs_at_least_one_source():
    ok, _, _ = verify_answer("Breast cancer costs $18995.", [], DOCS)
    assert not ok


def test_price_from_an_uncited_retrieved_page_adds_that_page_as_a_source():
    ok, reason, sources = verify_answer("The package starts from USD 12,500.", [PRICE_PAGE], DOCS)
    assert ok, reason
    assert sources == [PRICE_PAGE, PACKAGE]
