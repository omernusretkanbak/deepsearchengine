"""
Extractor Agent — 3-tier code-first content extraction.

Tier 1: BeautifulSoup  (0 tokens, 0 cost) — NON-YouTube only
Tier 2: Playwright     (0 tokens — JS-rendered pages, YouTube always)
Tier 3: LLM fallback   (last resort)

Token strategy: raw content hard-capped at MAX_CHARS before any LLM call.
Security: ONLY extracts raw text. Never executes JS.
"""

import os
import re
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

# YouTube consent bypass cookies — skips the "Before you continue" wall globally
_YT_COOKIES = [
    {
        "name": "SOCS",
        "value": "CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwMzI0LjA3X3AxGgJlbiADGgYIgOi8tAY",
        "domain": ".youtube.com",
        "path": "/",
    },
    {
        "name": "CONSENT",
        "value": "YES+cb.20230501-14-p0.en+FX+430",
        "domain": ".youtube.com",
        "path": "/",
    }
]


def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def _wrap(text: str) -> str:
    return f"{_DELIMITER_S}\n{text.strip()[:_MAX_CHARS]}\n{_DELIMITER_E}"


def _extract_view_count_from_text(text: str) -> str:
    """Regex ile metin içinden izlenme sayılarını yakala."""
    patterns = [
        r'([\d,.]+[MKBmkb]?\s*(?:views|izlenme|görüntülenme))',
        r'([\d,.]+\s*(?:view|izlenme))',
        r'(\d{1,3}(?:[.,]\d{3})*(?:\s*(?:views|izlenme)))',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


# ── Tier 1: BeautifulSoup (NON-YouTube only) ─────────────────

async def _bs4(url: str) -> str | None:
    """YouTube URL'leri için KULLANILMAZ — BS4 JS render edemez."""
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


# ── Tier 2: Playwright (YouTube DAİMA buradan geçer) ─────────

async def _playwright(url: str) -> str | None:
    try:
        from playwright.async_api import async_playwright
        import random
        is_yt = _is_youtube(url)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                locale="en-US",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                ),
            )

            # YouTube ise consent cookie'yi ÖNCEDEN enjekte et
            if is_yt:
                await context.add_cookies(_YT_COOKIES)

            page = await context.new_page()
            await page.goto(url, timeout=30_000, wait_until="domcontentloaded")

            if is_yt:
                # Sayfanın tam yüklenmesini bekle (anti-bot atlatmak için jitter ekle)
                await page.wait_for_timeout(int(random.uniform(3500, 5500)))

                # Consent sayfasına yönlendirildiyse buton ile de geç
                current = page.url
                if "consent" in current:
                    # Sunucunun lokasyonuna göre Almanca ve diğer dillerdeki onay butonları
                    for btn in ["Accept all", "I agree", "Tümünü kabul et", "Alle akzeptieren", "Zustimmen"]:
                        try:
                            locator = page.get_by_role("button", name=btn)
                            if await locator.is_visible(timeout=2000):
                                await locator.click()
                                await page.wait_for_timeout(int(random.uniform(2500, 4500)))
                                break
                        except Exception:
                            continue

                # --- Metrikleri topla ---
                metrics_parts = []

                # 1) Meta description (en güvenilir: "X views" içerir)
                try:
                    meta = await page.get_attribute(
                        'meta[name="description"]', "content", timeout=3000
                    )
                    if meta:
                        metrics_parts.append(f"META: {meta[:300]}")
                except Exception:
                    pass

                # 2) OG description (YouTube bunu da doldurur)
                try:
                    og = await page.get_attribute(
                        'meta[property="og:description"]', "content", timeout=2000
                    )
                    if og and og not in str(metrics_parts):
                        metrics_parts.append(f"OG: {og[:200]}")
                except Exception:
                    pass

                # 3) DOM seçicileri ile doğrudan metrik çekme
                selectors = [
                    "#view-count",
                    "yt-formatted-string.factoid-value",
                    "span.view-count",
                    "[aria-label*='views']",
                    "ytd-watch-info-text .yt-core-attributed-string",
                ]
                try:
                    dom_metrics = await page.eval_on_selector_all(
                        ", ".join(selectors),
                        "els => els.map(el => (el.getAttribute('aria-label') || el.innerText || '').trim()).filter(t => t.length > 0)"
                    )
                    if dom_metrics:
                        metrics_parts.append("DOM: " + " | ".join(dom_metrics[:5]))
                except Exception:
                    pass

                metrics_block = "\n".join(metrics_parts)
                body_text = await page.inner_text("body")

                # Regex ile body text'ten de izlenme yakala
                regex_views = _extract_view_count_from_text(body_text)
                if regex_views:
                    metrics_block += f"\nREGEX_VIEWS: {regex_views}"

                await browser.close()

                if metrics_block:
                    final = f"METRICS:\n{metrics_block}\n\nCONTENT:\n{body_text}"
                else:
                    final = body_text

                return final if len(final) > 80 else None

            else:
                # YouTube olmayan siteler
                text = await page.inner_text("body")
                await browser.close()
                return text if len(text) > 80 else None

    except Exception:
        return None


# ── Tier 0: Official APIs ────────────────────────────────────

async def _youtube_api(url: str) -> str | None:
    api_key = os.getenv("YOUTUBE_DATA_API_V3_API_KEY", os.getenv("YOUTUBE_API_KEY", ""))
    if not api_key:
        return None
        
    # Regex ile video ID'sini çıkar (11 karakterli eşsiz kimlik)
    vid_match = re.search(r'(?:v=|shorts/|youtu\.be/)([\w-]{11})', url)
    if not vid_match:
        return "NON_VIDEO_CONTENT: Playlist or Channel. No trackable video metrics."
        
    video_id = vid_match.group(1)
    
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
            r = await c.get(api_url)
            if r.status_code != 200:
                print(f"[YT API ERROR] {r.text}")
                return None
            
            data = r.json()
            items = data.get("items", [])
            if not items:
                return "Video deleted, private, or inaccessible."
            
            snippet = items[0].get("snippet", {})
            stats = items[0].get("statistics", {})
            
            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            views = int(stats.get("viewCount", "0"))
            
            # İzlenmeyi daha okunaklı yapalım (Analist'in işini kolaylaştır)
            if views > 1_000_000:
                views_str = f"{views / 1_000_000:.1f}M views"
            elif views > 1_000:
                views_str = f"{views / 1_000:.1f}K views"
            else:
                views_str = f"{views} views"

            return f"METRICS:\nVIEWS: {views_str}\n\nCONTENT:\n{title}\n\n{desc}"
    except Exception as e:
        print(f"[YT API CRASH] {e}")
        return None


# ── Tier 3: LLM fallback ─────────────────────────────────────

async def _llm_fallback(url: str, hint: str = "") -> str:
    system = "Extract: page title, view count, like count, description. Output compact JSON {title,views,likes,description}."
    user   = f"URL:{url}\nPartial content:{hint[:400]}"
    return await call_llm("google", "gemini-1.5-flash", system, user, max_tokens=300, json_mode=True)


# ── Public interface ──────────────────────────────────────────

async def extract(item: dict) -> dict:
    url = item.get("url", "")

    if _is_youtube(url):
        # YouTube → Resmî API ile ışık hızında sıfır hatayla veri çek
        content = await _youtube_api(url)
    else:
        # Diğer siteler → BS4 önce, Playwright yedek
        content = await _bs4(url)
        if not content:
            content = await _playwright(url)
        if not content:
            content = await _llm_fallback(url, content or "")

    return {
        "title":       item.get("title", ""),
        "url":         url,
        "raw_content": _wrap(content or "No content extracted."),
    }
