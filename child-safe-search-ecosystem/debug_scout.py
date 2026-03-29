import asyncio
import os
from dotenv import load_dotenv
from core.agents.scout import discover

load_dotenv()

async def debug_scout():
    print("Checking YOUTUBE_DATA_API_V3_API_KEY...")
    key = os.getenv("YOUTUBE_DATA_API_V3_API_KEY")
    print(f"Key exists: {'YES' if key else 'NO'}")
    
    query = "kids animation shorts"
    print(f"\nSearching for: {query}")
    results = await discover(query)
    
    print(f"\nResults found: {len(results)}")
    for r in results:
        print(f" - {r['title']} | {r['url']}")

if __name__ == "__main__":
    asyncio.run(debug_scout())
