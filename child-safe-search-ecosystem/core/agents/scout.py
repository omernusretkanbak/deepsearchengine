"""
Scout Agent — Hybrid Serper + Tavily search with Gemini Flash-Lite filtering.

Token strategy:
  • Serper  : bulk cheap Google results ($0.0005/call)
  • Tavily  : AI-enriched supplemental ($0.005/call)
  • Gemini Flash-Lite: relevance filter — compact prompt, max_tokens=150
"""

import os
import json
import re
import asyncio
import httpx
from tavily import AsyncTavilyClient
from core.utils.model_router import call_llm

_SERPER_URL  = "https://google.serper.dev/search"
_SCOUT_MODEL = os.getenv("SCOUT_MODEL", "gemini-2.0-flash-lite")
_MAX_CHARS_TITLE = 120  # truncate titles before sending to LLM


# ── Search providers ─────────────────────────────────────────

async def _serper(query: str, num: int = 10) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(
                _SERPER_URL,
                headers={"X-API-KEY": os.environ["SERPER_API_KEY"],
                         "Content-Type": "application/json"},
                json={"q": query, "num": num, "gl": "us", "hl": "en"},
            )
            return [
                {"title": i.get("title","")[:_MAX_CHARS_TITLE],
                 "url":   i.get("link","")}
                for i in r.json().get("organic", [])
            ]
    except Exception:
        return []


async def _tavily(query: str, n: int = 5) -> list[dict]:
    try:
        client = AsyncTavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        r = await client.search(query, max_results=n, include_raw_content=False)
        return [
            {"title": i.get("title","")[:_MAX_CHARS_TITLE],
             "url":   i.get("url","")}
            for i in r.get("results", [])
        ]
    except Exception:
        return []


def _dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for i in items:
        u = i.get("url","")
        if u and u not in seen:
            # SADECE VİDEOLAR: Playlist ve Kanal sayfalarını Python seviyesinde kökten yasakla
            if "youtube.com/playlist" in u or "youtube.com/channel" in u or "youtube.com/c/" in u or "/@" in u:
                continue
            seen.add(u)
            out.append(i)
    return out


# ── LLM relevance filter ─────────────────────────────────────

async def _filter(items: list[dict], topic: str) -> list[dict]:
    """Single compact Gemini call → returns indices of relevant items."""
    if not items:
        return []
    batch = json.dumps([{"i": idx, "t": x["title"]} for idx, x in enumerate(items)])
    system = "Return JSON array of integer indices for URLs relevant to YouTube Shorts content for kids aged 4-12. Nothing else."
    user   = f"Topic:{topic}\nItems:{batch}"
    try:
        resp = await call_llm("abacus", "route-llm", system, user, max_tokens=150, json_mode=True)


        # Handle cases where response is directly list or contains [indices]

        m = re.search(r'\[[\d,\s]*\]', resp)
        if m:
            indices = json.loads(m.group())
            return [items[i] for i in indices if isinstance(i, int) and i < len(items)]
    except Exception:
        pass
    return items  # fallback: keep all


# ── Public interface ──────────────────────────────────────────

async def discover(topic: str, max_results: int = 15) -> list[dict]:
    """
    Hybrid search: Serper (bulk) + Tavily (enriched).
    Searches BOTH safe and toxic/viral angles for full-spectrum data.
    """
    q_safe  = f"educational YouTube Shorts kids {topic} 2025"
    q_toxic = f"viral controversial kids YouTube Shorts {topic} brainrot"

    # Sequential searches to avoid rate limits
    serper_safe    = await _serper(q_safe,  num=10)
    await asyncio.sleep(0.5)
    serper_toxic   = await _serper(q_toxic, num=10)
    await asyncio.sleep(0.5)
    tavily_enriched = await _tavily(q_safe,  n=5)


    combined = _dedupe(serper_safe + serper_toxic + tavily_enriched)
    filtered = await _filter(combined, topic)
    return filtered[:max_results]
