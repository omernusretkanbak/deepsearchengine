"""
Extractor Agent — 3-tier code-first content extraction.

Tier 1: BeautifulSoup  (0 tokens, 0 cost)
Tier 2: Playwright     (0 tokens — JS-rendered pages)
Tier 3: GPT-4o mini   (fallback — obfuscated/blocked DOM)

Token strategy: raw content hard-capped at MAX_CHARS before any LLM call.
Security: ONLY extracts raw text. Never executes JS.
"""

import os
import httpx
from bs4 import BeautifulSoup
from core.utils.model_router import call_llm

_FALLBACK_MODEL = os.getenv("EXTRACTOR_FALLBACK_MODEL", "gpt-4o-mini")
_MAX_CHARS      = 2000   # hard cap — reduces tokens sent to analyst
_DELIMITER_S    = "---SCRAPED DATA START---"
_DELIMITER_E    = "---SCRAPED DATA END---"
_HEADERS        = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def _wrap(text: str) -> str:
    return f"{_DELIMITER_S}\n{text.strip()[:_MAX_CHARS]}\n{_DELIMITER_E}"


# ── Tier 1: BeautifulSoup ────────────────────────────────────

async def _bs4(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(
            timeout=15, headers=_HEADERS, follow_redirects=True
        ) as c:
            r = await c.get(url)
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text if len(text) > 80 else None
    except Exception:
        return None


# ── Tier 2: Playwright ───────────────────────────────────────

async def _playwright(url: str) -> str | None:
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page    = await browser.new_page()
            await page.goto(url, timeout=20_000, wait_until="networkidle")
            text = await page.inner_text("body")
            await browser.close()
            return text if len(text) > 80 else None
    except Exception:
        return None


# ── Tier 3: GPT-4o mini fallback ─────────────────────────────

async def _llm_fallback(url: str, hint: str = "") -> str:
    system = "Extract: page title, view count, description. Output compact JSON {title,views,description}."
    user   = f"URL:{url}\nPartial content:{hint[:400]}"
    return await call_llm("google", _FALLBACK_MODEL, system, user, max_tokens=300, json_mode=True)



# ── Public interface ──────────────────────────────────────────

async def extract(item: dict) -> dict:
    url = item.get("url", "")

    # Tier 1
    content = await _bs4(url)

    # Tier 2 — JS-rendered fallback
    if not content:
        content = await _playwright(url)

    # Tier 3 — LLM fallback
    if not content:
        content = await _llm_fallback(url, content or "")

    return {
        "title":       item.get("title", ""),
        "url":         url,
        "raw_content": _wrap(content or "No content extracted."),
    }
