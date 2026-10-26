"""The chat agent: one retrieval tool, structured output, then the guardrails."""

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import ToolMessage

from .guardrails import extract_prices, verify_answer
from .prompts import FALLBACK_ANSWER, SYSTEM_PROMPT
from .schemas import BotAnswer


def build_agent(model, retriever):
    @tool(response_format="content_and_artifact")
    def search_placidway(query: str):
        """Search PlacidWay's pages (ITC Immunity Therapy Center profile, packages, price list, videos, price comparison)."""
        docs = retriever.search(query)
        text = "\n\n".join(f"URL: {d.metadata['source']}\n{d.page_content}" for d in docs)
        return text, [{"url": d.metadata["source"], "text": d.page_content} for d in docs]

    return create_agent(model, tools=[search_placidway], system_prompt=SYSTEM_PROMPT, response_format=BotAnswer)


def answer_question(agent, history: list[dict]) -> dict:
    """history: [{"role": "user"|"assistant", "content": str}]; the last item is the new question."""
    result = agent.invoke({"messages": history})
    reply: BotAnswer = result["structured_response"]
    docs = _retrieved_docs(result["messages"])

    if not reply.answered:
        # A "don't know" reply must not slip in a number either.
        text = FALLBACK_ANSWER if (not reply.answer or extract_prices(reply.answer)) else reply.answer
        return _response(text, [], reply, grounded=False, reason="not in content")

    ok, reason, sources = verify_answer(reply.answer, reply.sources, docs)
    if not ok:
        return _response(FALLBACK_ANSWER, [], reply, grounded=False, reason=reason)
    return _response(reply.answer, sources, reply, grounded=True, reason="ok")


def _retrieved_docs(messages) -> list[dict]:
    """Every chunk the search tool returned during this turn."""
    return [doc for m in messages if isinstance(m, ToolMessage) and m.artifact for doc in m.artifact]


def _response(text: str, sources: list[str], reply: BotAnswer, grounded: bool, reason: str) -> dict:
    return {
        "answer": text,
        "sources": sources,
        "grounded": grounded,
        "medical_topic": reply.medical_topic,
        "offer_quote": reply.wants_quote or not grounded,
        "reason": reason,
    }
