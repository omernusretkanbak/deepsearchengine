import asyncio, os, json
from dotenv import load_dotenv
load_dotenv()
from core.agents.analyst import classify_batch
from core.utils.schemas import SearchResult, MacroTrend

async def main():
    topic = "viral YouTube Shorts kids 2025"
    mock_items = [
        {
            "title": "Funniest Kids of the Year! Best Videos of 2025 - YouTube",
            "url": "https://www.youtube.com/watch?v=_94l3R6NSVE",
            "raw_content": "---SCRAPED DATA START---\nFunniest Kids of the Year! Best Videos of 2025 - YouTube. Kids laughing and playing in park. Viral trend 2025.\n---SCRAPED DATA END---"
        }
    ]
    
    print(f"--- Testing Analyst for: {topic} ---")
    classified = await classify_batch(mock_items, topic)
    print("Classified RAW Keys:", classified.keys())
    
    # Check Result validation
    print("\n--- Validating Results ---")
    results_list = classified.get("results", [])
    if not results_list:
        print("NO RESULTS IN ANALYST RESPONSE.")
    
    for r in results_list:
        try:
            val = SearchResult.model_validate(r)
            print(f"  [VALID] {val.title}")
        except Exception as e:
            print(f"  [INVALID] {r.get('title')} | Error: {e}")

    # Check Trend validation
    print("\n--- Validating Macro Trends ---")
    trends_list = classified.get("macro_trends_4_to_12_age", [])
    for t in trends_list:
        try:
            val = MacroTrend.model_validate(t)
            print(f"  [VALID] Trend found")
        except Exception as e:
            print(f"  [INVALID] Trend | Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
