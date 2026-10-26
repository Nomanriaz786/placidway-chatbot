"""Deterministic checks that run after the model answers.

The model drafts; this code decides whether the draft is allowed out. An answer
passes only if every cited URL was actually retrieved, and every price it
states appears on one of the pages it cites.
"""

import re

# $18,995 | 18995 USD | USD 12,500 | US$ 3,000
_PRICE = re.compile(
    r"(?:US\$|\$|USD\s?)\s?(\d[\d,]*(?:\.\d+)?)|(\d[\d,]*(?:\.\d+)?)\s?(?:USD|US\$)",
    re.IGNORECASE,
)


def _norm(number: str) -> str:
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", number):  # 18.995 written European-style
        number = number.replace(".", "")
    n = number.replace(",", "")
    return n[:-3] if n.endswith(".00") else n


def extract_prices(text: str) -> set[str]:
    return {_norm(a or b) for a, b in _PRICE.findall(text)}


def verify_answer(answer: str, sources: list[str], docs: list[dict]) -> tuple[bool, str, list[str]]:
    """docs: [{"url", "text"}] for every chunk the agent retrieved this turn.

    Returns (ok, reason, sources). A price that the model took from a retrieved
    page it forgot to cite is fine: that page is added to the sources. A price
    that appears on no retrieved page fails the answer.
    """
    if not sources:
        return False, "no source cited", []
    retrieved = {d["url"] for d in docs}
    unknown = [s for s in sources if s not in retrieved]
    if unknown:
        return False, f"cited source not retrieved: {unknown[0]}", []

    prices_by_url: dict[str, set[str]] = {}
    for d in docs:
        prices_by_url.setdefault(d["url"], set()).update(extract_prices(d["text"]))

    sources = list(dict.fromkeys(sources))
    for price in sorted(extract_prices(answer)):
        if any(price in prices_by_url.get(s, set()) for s in sources):
            continue
        holder = next((u for u, p in prices_by_url.items() if price in p), None)
        if holder is None:
            return False, f"price not found on retrieved pages: {price}", []
        sources.append(holder)
    return True, "ok", sources
