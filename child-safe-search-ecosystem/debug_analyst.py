import asyncio
import os
import json
from dotenv import load_dotenv
from core.agents import analyst

load_dotenv()

async def debug_analyst_direct():
    print("--- TESTING ANALYST DIRECTLY ---")
    mock_items = [
        {
            "title": "Cool Video",
            "url": "https://youtube.com/watch?v=123",
            "raw_content": "---SCRAPED DATA START---\nThis is a cool kids video about colors. 1.2M views.\n---SCRAPED DATA END---"
        }
    ]
    query = "kids colors"
    
    try:
        res = await analyst.classify_batch(mock_items, query)
        print("\n=== SUCCESS ===")
        print(f"Results Count: {len(res.get('results', []))}")
        print(f"Full Strategy: {res.get('strategic_consulting_tr', '')[:100]}...")
    except Exception as e:
        print("\n=== FAILED ===")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_analyst_direct())
