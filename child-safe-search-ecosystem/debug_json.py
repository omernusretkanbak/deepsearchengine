import asyncio
import os
import json
from core.orchestrator import run
from core.agents import analyst

# Patch analyst _parse to save the raw response to a file on crash
original_parse = analyst._parse

def patched_parse(resp: str):
    res = original_parse(resp)
    if not res.get("results"):
        with open("crashed_resp.txt", "w", encoding="utf-8") as f:
            f.write(resp)
        print("CRASH SAVED TO crashed_resp.txt")
    return res

analyst._parse = patched_parse

async def test():
    await run("most viewed high quality animation movie like viral short videos for kids")

if __name__ == "__main__":
    asyncio.run(test())
