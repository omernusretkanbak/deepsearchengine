# Deep Search Ecosystem — Persistent Memory

## Scraping Strategies
- YouTube Shorts: JS-rendered → Playwright required
- YouTube Consent Bypass: Auto-clicking "Accept all" is fragile. Best method is pre-injecting Google's Consent Cookie (`name="SOCS"`) before navigation.
- Docker & Playwright: Always use `args=["--no-sandbox", "--disable-dev-shm-usage"]` to prevent memory crashes. ALWAYS provide a BS4 fallback if Playwright returns None.
- Metrics Extraction: DOM changes daily. Use a shotgun approach: Meta `description` tag + OG Tags + CSS Selectors (`yt-formatted-string.factoid-value`) + Regex on `body`.

## Classification Edge Cases
- "Skibidi Toilet" series → DEVELOPMENTALLY_HARMFUL (absurd violence loop)
- "Blippi" → SAFE_AND_EDUCATIONAL (HIGH parental trust)

## Known Rate Limits
- YouTube: ~60 req/min before soft-block / CAPTCHA.
- Serper: Generous limits, 100 req/min (free tier).
- Tavily: 20 req/min (free tier, 1000/month strict quota).
- LLMs (Free Tiers): Google Gemini hits 429 at ~15 RPM. Abacus can hit 429 easily on concurrency.

## 🛡️ Anti-Bot & Marathon Architecture Tricks
- **Jitter:** Never use fixed timeouts (`wait_for_timeout(3000)`). Always use `random.uniform(X, Y)` to mimic human latency and prevent bot detection.
- **Pacing:** When running concurrent extraction, use `asyncio.Semaphore(2)` and add `asyncio.sleep(random.uniform(2.0, 4.0))` between dispatches to fly under the rate-limit radar.
- **Exponential Backoff:** Always wrap API calls (LLMs/Search) in a `try/except` loop catching `429`, `503`, and `timeout`. Sleep for `(2 ** attempt) + random.uniform(1.0, 3.0)` seconds before retrying.

## DOM Patterns
- YouTube shorts blocked JS → playwright + wait_for_selector("#title")

### [2026-03-28 22:38] Run
query=viral YouTube Shorts kids 2025 | results=11 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:20] Run
query=viral YouTube Shorts kids 2025 | results=7 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:21] Run
query=viral YouTube Shorts kids 2025 | results=9 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:26] Run
query=viral YouTube Shorts kids 2025 | results=10 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:27] Run
query=viral YouTube Shorts kids 2025 | results=10 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:40] Run
query=viral YouTube Shorts kids 2025 | results=9 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 02:55] Run
query=viral YouTube Shorts kids 2025 | results=6 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm

### [2026-03-29 10:27] Run
query=viral YouTube Shorts kids 2025 | results=2 | models=gemini-1.5-flash + gemini-1.5-flash + gemini-1.5-flash + route-llm
