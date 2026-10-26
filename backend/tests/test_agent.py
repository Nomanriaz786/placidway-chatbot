from langchain_core.messages import AIMessage, ToolMessage

from chatbot.agent import answer_question
from chatbot.prompts import FALLBACK_ANSWER
from chatbot.schemas import BotAnswer

URL = "https://www.placidway.com/price-list/5/x"


class FakeAgent:
    def __init__(self, out: BotAnswer, docs: list[dict]):
        self.out, self.docs = out, docs

    def invoke(self, state):
        assert state["messages"][-1]["role"] == "user"
        msgs = [AIMessage(content=""), ToolMessage(content="...", tool_call_id="1", artifact=self.docs)]
        return {"messages": msgs, "structured_response": self.out}


DOCS = [{"url": URL, "text": "Breast Cancer $18995"}]
Q = [{"role": "user", "content": "How much is breast cancer treatment?"}]


def bot(text, sources, answered=True):
    return BotAnswer(answer=text, sources=sources, answered=answered, medical_topic=True, wants_quote=False)


def test_grounded_answer_is_returned_with_sources():
    r = answer_question(FakeAgent(bot("It is $18,995 USD.", [URL]), DOCS), Q)
    assert r["grounded"] and r["answer"] == "It is $18,995 USD." and r["sources"] == [URL]


def test_invented_price_is_replaced_by_fallback():
    r = answer_question(FakeAgent(bot("It is $5,000.", [URL]), DOCS), Q)
    assert not r["grounded"] and r["answer"] == FALLBACK_ANSWER and r["offer_quote"]


def test_unanswered_reply_with_a_price_is_still_blocked():
    r = answer_question(FakeAgent(bot("Not listed, but usually around $4,000.", [], answered=False), DOCS), Q)
    assert r["answer"] == FALLBACK_ANSWER


def test_unanswered_reply_without_prices_keeps_model_wording():
    r = answer_question(FakeAgent(bot("I can't book appointments, but you can request a free quote.", [], answered=False), DOCS), Q)
    assert r["answer"].startswith("I can't book") and r["offer_quote"] and r["sources"] == []
