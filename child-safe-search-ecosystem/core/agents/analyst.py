"""
Analyst Agent — Claude 3.7 Sonnet batch classifier.

Token strategy:
  • ONE single Claude call for ALL items (not one-per-URL).
  • Scraped content truncated to 1200 chars per item before sending.
  • Delimiters stripped from raw_content to save tokens inside the batch.
  • json_mode NOT used (Anthropic doesn't support it natively); JSON parsing is robust.

Critical rule from directive: DO NOT FILTER BAD CONTENT — include everything, tag accurately.
"""

import os
import json
import re
from core.utils.model_router import call_llm

_MODEL      = os.getenv("ANALYST_MODEL", "claude-3-7-sonnet-20250219")
_MAX_ITEM   = 1200   # chars per item content — controls token spend
_MAX_TOKENS = 4000   # enough for 15 items × ~250 tokens each

_SYSTEM = (
    "You are a child content classifier for YouTube Shorts market analysis (4-12yo audience). "
    "Classify ALL provided items. DO NOT filter or omit any content. "
    "Safety categories (ENUM): SAFE_AND_EDUCATIONAL | DEVELOPMENTALLY_HARMFUL | RELIGIOUS_OR_POLITICAL | "
    "SEXUALLY_SUGGESTIVE | SUBSTANCE_ABUSE_OR_ASSOCIATION | EXCESSIVE_VIOLENCE. "
    "Parental trust (ENUM): HIGH | MEDIUM | LOW | DO_NOT_USE. "
    "Crucial Metrics Extraction: Look for 'views', 'view count', and numbers in the 'METRICS:' and 'META:' blocks. "
    "Always provide a 'key_metrics' estimate (e.g., '1.2M views') if any data is found. Output ONLY VALID JSON."
)


_USER_TMPL = """\
Topic: {topic}

Items:
{items}

Return ONLY this JSON structure:
{{
  "results": [
    {{
      "id": 0,
      "title": "...",
      "url": "...",
      "summary": "1-2 sentence summary",
      "key_metrics": "views/retention if found, else 'N/A'",
      "content_safety_category": "ENUM",
      "parental_trust_potential": "ENUM",
      "niche_recommendation_value": "how to safely adapt the viral hook, or avoidance warning",
      "tags": ["tag1", "tag2"],
      "server_debug_snapshot": "first 150 chars of raw content"
    }}
  ],
  "macro_trends_4_to_12_age": [
    {{
      "video_format": "...",
      "view_volume_estimate": "...",
      "why_it_works": "psychological/visual hook explanation"
    }}
  ]
}}"""


def _strip_delimiters(text: str) -> str:
    return (
        text.replace("---SCRAPED DATA START---", "")
            .replace("---SCRAPED DATA END---", "")
            .strip()
    )


def _parse(resp: str) -> dict:
    """Robust JSON extraction — handles markdown fences and partial wrapping."""
    # Try direct parse
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        pass
    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", resp).strip().rstrip("`")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Last resort: find first {...} block
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return {"results": [], "macro_trends_4_to_12_age": []}


async def classify_batch(items: list[dict], topic: str) -> dict:
    """Single Claude call — classifies all items + derives macro trends."""
    if not items:
        return {"results": [], "macro_trends_4_to_12_age": []}

    batch = []
    for idx, item in enumerate(items):
        content = _strip_delimiters(item.get("raw_content", ""))
        batch.append({
            "id":      idx,
            "title":   item.get("title", ""),
            "url":     item.get("url", ""),
            "content": content[:_MAX_ITEM],
        })

    user_prompt = _USER_TMPL.format(
        topic=topic,
        items=json.dumps(batch, ensure_ascii=False, separators=(",", ":")),
    )

    resp = await call_llm(
        "abacus", _MODEL, _SYSTEM, user_prompt, max_tokens=_MAX_TOKENS, json_mode=True
    )
    return _parse(resp)


