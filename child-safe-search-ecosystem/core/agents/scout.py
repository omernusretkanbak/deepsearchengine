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

async def _youtube_search(query: str, max_results: int = 10) -> list[dict]:
    """Sorguyu doğrudan YouTube'a yollar ve 'En Çok İzlenenlere' (order=viewCount) göre temiz shorts listesi çeker."""
    api_key = os.getenv("YOUTUBE_DATA_API_V3_API_KEY", os.getenv("YOUTUBE_API_KEY", ""))
    if not api_key:
        return []
    
    # API URL parameters: type=video, videoDuration=short forces Shorts!
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&videoDuration=short&order=viewCount&maxResults={max_results}&key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(url)
            if r.status_code != 200:
                print(f"[YT SEARCH ERROR] {r.text}")
                return []
            
            data = r.json()
            return [
                {
                    "title": i['snippet']['title'][:_MAX_CHARS_TITLE],
                    "url": f"https://www.youtube.com/watch?v={i['id']['videoId']}"
                }
                for i in data.get("items", [])
            ]
    except Exception as e:
        print(f"[YT SEARCH CRASH] {e}")
        return []


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
    Hybrid search: Native YouTube API (Most Viewed) + Serper (bulk) + Tavily (enriched).
    Searches BOTH safe and toxic/viral angles for full-spectrum data.
    """
    # 1. Native YouTube VİRAL ARAMASI (Garantili Milyon İzlenmeler)
    yt_query = f"{topic}"
    yt_viral_shorts = await _youtube_search(yt_query, max_results=10)
    
    # 2. Genel Google Web Araması (Zenginlik ve Farklı açılar katmak için)
    q_safe  = f"educational YouTube Shorts kids {topic} 2025"
    q_toxic = f"viral controversial kids YouTube Shorts {topic} brainrot"

    # Sequential searches to avoid rate limits
    serper_safe    = await _serper(q_safe,  num=5)
    await asyncio.sleep(0.5)
    serper_toxic   = await _serper(q_toxic, num=5)
    await asyncio.sleep(0.5)
    tavily_enriched = await _tavily(q_safe,  n=3)

    # Birleştir -> yt_viral_shorts ilk sırada olduğu için kalitede (İzlenme bazlı) önceliklidir!
    print(f"[SCOUT DEBUG] YT: {len(yt_viral_shorts)} | Serper: {len(serper_safe)+len(serper_toxic)} | Tavily: {len(tavily_enriched)}")
    combined = _dedupe(yt_viral_shorts + serper_safe + serper_toxic + tavily_enriched)
    print(f"[SCOUT DEBUG] Combined & Deduped: {len(combined)}")
    filtered = await _filter(combined, topic)
    print(f"[SCOUT DEBUG] After Filter: {len(filtered)}")
    return filtered[:max_results]
