# Write-up: limitations and next steps

## Known limitations

- **Content scope.** The bot knows only the seven pages it was given, so most comparisons ("Mexico or Turkey?") correctly end in "I don't know". That is by design, but a patient may see it often.
- **Price guardrail is numeric.** It proves every price in an answer exists on a retrieved page, but it cannot prove the price is attached to the right treatment. A wrong-row mix-up on the price list would pass the check.
- **Strict fallback.** When the model repeats a price the user claimed (the "$50" trick), the whole reply is replaced by the safe fallback rather than a polite correction. Safe, but less helpful.
- **Partial answers.** If the model marks an answer as not found, any partly useful facts in it are shown without source links.
- **Single process.** The index and the rate limiter live in memory. That is fine for one VPS process; more instances would need a shared vector store and Redis.
- **Refresh from the server.** PlacidWay returns 403 to the hosting provider's IP range, so the live index is built from an allowed network and uploaded. The refresh endpoint fails safely (keeps the current index) until the server's IP is allowlisted.
- **Videos page.** Only the text around each video is indexed; the videos themselves are not transcribed.

## What I would do with another week

1. **Row-level price checks:** parse the price tables into structured rows (treatment, program, duration, price) and check that each quoted price belongs to the treatment named in the answer.
2. **An evaluation set:** 50+ questions with expected sources and prices, run in CI so prompt or retrieval changes cannot quietly reduce accuracy.
3. **Better partial answers:** keep cited facts when the model is unsure, and correct a user's wrong price instead of falling back.
4. **Scheduled refresh** (once the server IP is allowlisted) with change detection (hash each page) and an alert when a page changes structure.
5. **Streaming replies** and an admin view of unanswered questions and leads.
