import asyncio
from dotenv import load_dotenv
load_dotenv()

from core.orchestrator import run

async def test():
    print("[TEST] Starting full pipeline...")
    result = await run("viral YouTube Shorts kids 2025")
    print(f"[TEST] Results: {len(result.results)}")
    print(f"[TEST] Trends: {len(result.macro_trends_4_to_12_age)}")
    print(f"[TEST] Time: {result.automation_metadata.execution_time_seconds}s")
    
    for r in result.results[:3]:
        print(f"\n  Title: {r.title}")
        print(f"  Metrics: {r.key_metrics}")
        print(f"  Safety: {r.content_safety_category}")

asyncio.run(test())
