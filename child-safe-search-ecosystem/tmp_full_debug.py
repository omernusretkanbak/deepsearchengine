import asyncio, os, json, time
from dotenv import load_dotenv
load_dotenv()
from core.agents import scout, extractor, analyst
from core.utils import model_router

async def debug_full_pipeline():
    query = "viral YouTube Shorts kids 2025"
    print(f"--- DEBUG START: {query} ---")
    
    # 1. Scout
    items = await scout.discover(query, 3)
    print(f"Scout found {len(items)} items.")
    
    # 2. Extract
    extracted = []
    for item in items:
        res = await extractor.extract(item)
        extracted.append(res)
        print(f"Extracted: {item['title'][:40]}... ({len(res['raw_content'])} chars)")
    
    # 3. Analyst (RAW CHECK)
    print("\n--- ANALYST RAW RESPONSE CHECK ---")
    batch = []
    for idx, item in enumerate(extracted):
        content = item.get("raw_content", "")
        batch.append({
            "id": idx,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": content[:1000],
        })
    
    user_prompt = analyst._USER_TMPL.format(
        topic=query,
        items=json.dumps(batch, ensure_ascii=False, separators=(",", ":")),
    )
    
    # Direct LLM call to see EXACT output
    raw_resp = await model_router.call_llm(
        "google", os.getenv("ANALYST_MODEL"), analyst._SYSTEM, user_prompt, max_tokens=2000, json_mode=True
    )
    
    print("RAW LLM OUTPUT:")
    print(raw_resp)
    
    # 4. Parse Check
    parsed = analyst._parse(raw_resp)
    print("\nParsed Results Count:", len(parsed.get("results", [])))
    if not parsed.get("results"):
        print("ALERT: NO RESULTS AFTER PARSING.")

if __name__ == "__main__":
    asyncio.run(debug_full_pipeline())
