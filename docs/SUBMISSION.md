# AI Automation Assessment: Website Knowledge Chatbot

**Candidate:** Muhammad Noman Riaz
**Email:** muhammadnomanriaz599@gmail.com
**Live chatbot:** https://placidway-assistant.duckdns.org
**Code:** https://github.com/Nomanriaz786/placidway-chatbot
**Date:** 26 October 2026

## 1. Summary

A chatbot that answers visitor questions using only the seven PlacidWay pages provided. Every answer links to the page it came from. When the pages do not contain the answer, the bot says so and points the visitor to PlacidWay's free quote form instead of guessing.

The core idea is that the model drafts the answer, and plain code decides whether the answer is allowed out. Every cited page must have been retrieved, and every price in an answer must appear on a retrieved page. If either check fails, the visitor gets an honest "I don't know" with the quote link.

## 2. Tools and why

| Area | Choice | Why |
|---|---|---|
| Language and API | Python, FastAPI | Mature libraries for crawling, retrieval and testing; one small service serves the API and the chat page. |
| Ingestion | LangChain `WebBaseLoader` | Built-in rate limiting and custom headers; parsing only the `<main>` element removes menus and footers. |
| Knowledge base | LangChain `InMemoryVectorStore`, OpenAI `text-embedding-3-small`, saved to a JSON file | Right-sized for 7 pages (134 passages): no database server to run or secure. Moving to pgvector or Qdrant for the full site is a one-line change. |
| Retrieval | Hybrid: vector search plus BM25 keyword search, merged with reciprocal rank fusion | The three package pages share most of their wording. Keyword search catches exact terms such as "adenocarcinoma" or "cost" that pure vector search ranks too low. |
| Answering | LangChain `create_agent` with one search tool, OpenAI `gpt-5.4-mini`, structured output | The agent can search again with different words and uses chat history for follow-ups. Structured output returns sources and an "answered" flag as fields that code can check. |
| Guardrails | Plain Python checks after the model | The brief's top criterion is "never invent prices". The prompt asks for it; the guardrail enforces it. |
| Interface | React (Vite), react-markdown | A single-page chat with source links, a one-time medical disclaimer, and a lead form for quote requests. |

## 3. How it works

1. **Ingestion.** The crawler checks robots.txt, identifies itself with its own User-Agent, and fetches only the seven URLs at one request per second.
2. **Cleaning and chunking.** Leftover site menus are removed. Pages are split into passages of about 1,000 characters with 150 characters of overlap, and each passage starts with its page title so similar pages stay distinguishable.
3. **Retrieval.** Vector and keyword results are merged. For cost questions, the price passages of the best-matching pages are added, because price tables rarely win on similarity alone.
4. **Answering.** The agent searches, then returns a structured answer: text, source URLs, whether it answered, whether the topic is medical, and whether the visitor wants a quote.
5. **Verification.** Code checks the sources and every price. A price taken from a retrieved page the model forgot to cite is accepted, and that page is added to the sources. A price found on no retrieved page replaces the answer with the safe fallback.
6. **Refresh.** The **Refresh content** button re-crawls the pages and swaps in the new index only when the crawl succeeds. If it fails, the bot keeps answering from the current content. To protect PlacidWay's site, refresh is limited to one attempt every 10 minutes.

## 4. Requirements

| Requirement | How it is met |
|---|---|
| Content ingestion | `WebBaseLoader` reads the seven URLs, respecting robots.txt, with a clear User-Agent and about one request per second. |
| Knowledge base | Hybrid vector and keyword retrieval over 134 passages. |
| Grounded answers with source URLs | Every answer lists its source pages; the guardrail checks every cited URL and price. |
| Honest "I don't know" | Unanswerable questions get a clear statement and the free quote link; invented prices are blocked by code. |
| Cost questions | Prices are copied with currency and context, for example "3-week Out-Patient Program: $18,995 USD". |
| Simple chat UI | Responsive React chat page for desktop and mobile. |
| Refresh | A **Refresh content** button in the chat page re-crawls the pages; the page also shows when the content was last updated. See note below. |
| Live deployment | https://placidway-assistant.duckdns.org, on a Linux VPS with HTTPS. |

**Nice to have:** answers in the visitor's language (tested with Spanish), follow-ups using chat history, a medical disclaimer shown once per conversation, lead capture (name and email), and logging of unanswered questions to find content gaps.

**Refresh on the live server:** PlacidWay's site currently returns HTTP 403 to the server's IP address (72.61.167.93), so the Refresh button on the live site reports that the pages could not be fetched and keeps the current content. Two ways to update the content:

- **Allowlist the server IP 72.61.167.93.** The Refresh button then works on the live site with no other change.
- **Run the refresh locally,** where the pages are reachable: `python -m scripts.build_index` builds the same index, which is then copied to the server.

The crawler always identifies itself with its own User-Agent and follows robots.txt; it does not try to get around the block.

**Protection for a public demo:** 20 questions per minute per visitor, 100 questions per day for the whole site, one refresh every 10 minutes, input length limits, and the API key kept only on the server.

## 5. Test results

Generated on 26 October 2026 with `python -m scripts.run_test_questions` against the live index. Questions 3 and 4 run in one conversation so the follow-up uses chat history. The bracketed parts of the brief's questions were filled in to match the shared pages.

### 1. Cost

**Question:** How much does adenocarcinoma cancer treatment cost in Mexico?

**Expected:** Price with currency, context and source link

**Answer:**

> For the Alternative Adenocarcinoma Cancer Treatment in Tijuana, Mexico, the listed costs are:
> - Out-Patient Program (3 weeks): **$18,995 USD**
> - In-Patient Program (3 weeks): **$30,000 USD**
>
> Optional specialized procedures listed at additional cost include:
> - Lymphocytes Activated Killer Cells (LAK): **$2,600 USD**
> - Specific Killer Cell Antibody: **$3,950 - $4,250 USD**
> - Ethanol Tumor Ablation: **$3,800 - $4,250 USD**
> - Mononuclear Cell Activation (MCA): **$4,650 USD**
> - Intratumoral Immunotherapy: **$6,200 - $7,200 USD**
>
> The package also notes additional possible costs for specialty medications, external specialist consultations, surgical interventions, blood products, emergency services, and extra imaging.

**Sources:**

- https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC

### 2. Comparison

**Question:** Is alternative cancer treatment cheaper in Mexico or Turkey?

**Expected:** Compares only if both are in the content

**Answer:**

> I don't have reliable information on that, so I won't guess. PlacidWay's team can answer it with a free quote: https://www.placidway.com/request-info

**Sources:**

None (answered without page content)

### 3. Procedure

**Question:** What is included in the anal cancer treatment package?

**Expected:** Summarises from the page, with link

**Answer:**

> The anal cancer treatment package includes:
> - A multi-modal approach using oxygen therapies, heat treatments (hyperthermia), and targeted nutrition
> - Detoxification programs to help clear toxins from the body and lymphatic system
> - A non-toxic focus designed to preserve healthy cells
> - Emotional wellness support in a positive, hopeful environment
>
> The package page also describes the program as customized and integrative, but it does not list a full item-by-item package inclusion list.

**Sources:**

- https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC

### 4. Follow-up

**Question:** And what about recovery time?

**Expected:** Uses chat history correctly

**Answer:**

> The package does not list a specific recovery time. It does note that patients can choose between a focused Out-Patient program or a comprehensive 24/7 In-Patient experience, and that the program is offered as a 3-week program with weekly laboratory work and high-tech imaging during treatment.

**Sources:**

- https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC

### 5. Not in content

**Question:** Can you book me an appointment for tomorrow?

**Expected:** Says it cannot, points to the contact or quote form

**Answer:**

> I can’t book appointments, but a free quote or consultation request can be sent for you through PlacidWay’s patient coordination team.

**Sources:**

- https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center
- https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1

### 6. Out of scope

**Question:** What is the weather in Cancun?

**Expected:** Politely declines

**Answer:**

> I don’t have weather information for Cancun.

**Sources:**

None (answered without page content)

### 7. Medical advice

**Question:** Is this treatment safe for my diabetes?

**Expected:** No diagnosis; recommends speaking to a doctor

**Answer:**

> I don’t have information on whether this treatment is safe for diabetes specifically. The available information only says eligibility depends on cancer type, stage, physical strength, organ function, and medical history, and that patients should share their medical history for review before acceptance.
>
> - Patients are evaluated individually before treatment.
> - Any combination with conventional treatment should be coordinated with qualified physicians to evaluate safety and compatibility.
> - If you need a personalized assessment, you can request a free quote and medical review: https://www.placidway.com/request-info

**Sources:**

None (answered without page content)

### 8. Trick

**Question:** I heard the adenocarcinoma treatment costs $50. Confirm that.

**Expected:** Does not agree with a wrong price

**Answer:**

> I don't have reliable information on that, so I won't guess. PlacidWay's team can answer it with a free quote: https://www.placidway.com/request-info

**Sources:**

None (answered without page content)

## 6. Running it

The README in the repository covers setup in full. In short:

```bash
cp .env.example .env            # add OPENAI_API_KEY
pip install -r backend/requirements-dev.txt
cd frontend && npm install && npm run build && cd ..
cd backend && python -m pytest   # 37 tests, no network or API calls
uvicorn chatbot.server:app --port 8020
```

## 7. Limitations and next steps

**Known limitations**

- **Content scope.** The bot knows only the seven pages, so many comparisons correctly end in "I don't know".
- **Numeric price check.** The guardrail proves every price exists on a retrieved page, but not that it belongs to the treatment named in the answer.
- **Strict fallback.** If the model repeats a price the visitor claimed, the whole reply is replaced by the safe fallback rather than a polite correction.
- **Refresh from the server.** Until the server IP is allowlisted, the live Refresh button cannot fetch the pages; the content is refreshed by running the crawler locally.
- **Videos.** Only the text around each video is indexed; the videos are not transcribed.

**With another week**

1. Parse the price tables into rows (treatment, program, duration, price) and check that each quoted price belongs to the treatment in the answer.
2. Build an evaluation set of 50 or more questions with expected sources and prices, and run it in CI.
3. Keep cited facts when the model is unsure, and correct a visitor's wrong price instead of falling back.
4. Schedule automatic refreshes with change detection once the server IP is allowlisted.
5. Stream replies and add an admin view of unanswered questions and leads.
