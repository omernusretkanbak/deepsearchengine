"""
Orchestrator — coordinates Scout → Extractor (concurrent) → Analyst pipeline.
Uses memory.md for pre/post-computation learning.
All logs are credential-scrubbed before writing.
"""

import os
import time
import asyncio
from core.agents import scout, extractor, analyst
from core.utils import memory, security
from core.utils.schemas import (
    DeepSearchOutput, AutomationMetadata, SearchResult, MacroTrend,
)

_TIMEOUT     = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
_MAX_RESULTS = int(os.getenv("MAX_RESULTS", "15"))

_MODEL_TAG = (
    f"{os.getenv('ORCHESTRATOR_MODEL','gemini-2.5-pro-preview-03-25')} + "
    f"{os.getenv('SCOUT_MODEL','gemini-2.0-flash-lite')} + "
    f"{os.getenv('EXTRACTOR_FALLBACK_MODEL','gpt-4o-mini')} + "
    f"{os.getenv('ANALYST_MODEL','claude-3-7-sonnet-20250219')}"
)


async def run(query: str) -> DeepSearchOutput:
    start = time.monotonic()

    # ── Pre-computation: load memory ──────────────────────────
    memory.read()   # available for future prompt injection if needed

    # ── Phase 1: Scout ────────────────────────────────────────
    try:
        urls = await asyncio.wait_for(
            scout.discover(query, _MAX_RESULTS), timeout=_TIMEOUT
        )
    except (asyncio.TimeoutError, Exception):
        urls = []

    if not urls:
        return _empty(query, time.monotonic() - start)

    # ── Phase 2: Extractor (STRICTLY sequential to avoid 429) ──
    sem = asyncio.Semaphore(1)

    async def _safe_extract(item):
        async with sem:
            try:
                # Add a small delay between tasks for a "healthy flow"
                await asyncio.sleep(1.0)
                return await asyncio.wait_for(extractor.extract(item), timeout=50)
            except Exception:
                return None

    tasks = [_safe_extract(item) for item in urls]
    extracted: list[dict] = []


    for fut in asyncio.as_completed(tasks):
        try:
            extracted.append(await fut)
        except Exception:
            pass

    if not extracted:
        return _empty(query, time.monotonic() - start)

    # ── Phase 3: Analyst (batch — single LLM call) ────────────
    try:
        classified = await asyncio.wait_for(
            analyst.classify_batch(extracted, query),
            timeout=_TIMEOUT * 2,
        )
    except (asyncio.TimeoutError, Exception):
        classified = {"results": [], "macro_trends_4_to_12_age": []}

    # ── Post-computation: update memory ───────────────────────
    n = len(classified.get("results", []))
    if n:
        memory.append(
            "Run",
            security.scrub(f"query={query} | results={n} | models={_MODEL_TAG}"),
        )

    # ── Assemble output ───────────────────────────────────────
    results: list[SearchResult] = []
    for r in classified.get("results", []):
        try:
            results.append(SearchResult.model_validate(r))
        except Exception:
            pass

    trends: list[MacroTrend] = []
    for t in classified.get("macro_trends_4_to_12_age", []):
        try:
            trends.append(MacroTrend.model_validate(t))
        except Exception:
            pass

    return DeepSearchOutput(
        research_topic=query,
        macro_trends_4_to_12_age=trends,
        results=results,
        automation_metadata=AutomationMetadata(
            execution_time_seconds=round(time.monotonic() - start, 2),
            model_used=_MODEL_TAG,
        ),
    )


def _empty(query: str, elapsed: float) -> DeepSearchOutput:
    return DeepSearchOutput(
        research_topic=query,
        macro_trends_4_to_12_age=[],
        results=[],
        automation_metadata=AutomationMetadata(
            execution_time_seconds=round(elapsed, 2),
            model_used=_MODEL_TAG,
        ),
    )
