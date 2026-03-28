import asyncio, os
from dotenv import load_dotenv
load_dotenv()
from core.agents.extractor import extract

async def main():
    item = {
        "title": "Funniest Kids of the Year! Best Videos of 2025 - YouTube",
        "url": "https://www.youtube.com/watch?v=_94l3R6NSVE"
    }
    print(f"--- Testing Extraction for: {item['url']} ---")
    
    result = await extract(item)
    content = result.get("raw_content", "")
    print(f"Content Length: {len(content)}")
    print(f"Preview: {content[:150]}")
    
    if "No content extracted" in content:
        print("FAILED TO EXTRACT CONTENT.")
    else:
        print("EXTRACTION SUCCESSFUL.")

if __name__ == "__main__":
    asyncio.run(main())
