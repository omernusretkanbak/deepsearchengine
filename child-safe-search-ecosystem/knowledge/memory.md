# Deep Search Ecosystem — Persistent Memory

## Scraping Strategies
- YouTube Shorts: JS-rendered → Playwright required
- youtube.com/shorts/* : body text extraction sufficient after JS load

## Classification Edge Cases
- "Skibidi Toilet" series → DEVELOPMENTALLY_HARMFUL (absurd violence loop)
- "Blippi" → SAFE_AND_EDUCATIONAL (HIGH parental trust)

## Known Rate Limits
- YouTube: ~60 req/min before soft-block
- Serper: 100 req/min (free tier)
- Tavily: 20 req/min (free tier)

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
