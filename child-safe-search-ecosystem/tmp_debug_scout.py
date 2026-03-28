import asyncio, os, json
from dotenv import load_dotenv
load_dotenv()
from core.agents.scout import _serper, _tavily, _filter

async def main():
    topic = "viral YouTube Shorts kids 2025"
    print(f"--- Debugging for Topic: {topic} ---")
    
    s1 = await _serper(topic, 5)
    print(f"Serper found: {len(s1)} items")
    for x in s1: print(f"  - {x.get('title')}")
    
    t1 = await _tavily(topic, 5)
    print(f"Tavily found: {len(t1)} items")
    for x in t1: print(f"  - {x.get('title')}")
    
    combined = s1 + t1
    if not combined:
        print("NO RESULTS FOUND AT ALL.")
        return

    print(f"\n--- Testing Filter (combined={len(combined)}) ---")
    filtered = await _filter(combined, topic)
    print(f"After filtering: {len(filtered)} items")
    for x in filtered:
        print(f"  [KEEP] {x.get('title')}")

if __name__ == "__main__":
    asyncio.run(main())
