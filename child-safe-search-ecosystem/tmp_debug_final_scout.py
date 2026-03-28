import asyncio, os, json, re
from dotenv import load_dotenv
load_dotenv()
from core.agents import scout
from core.utils import model_router

async def debug_scout():
    topic = "viral YouTube Shorts kids 2025"
    print(f"--- DEBUG SCOUT: {topic} ---")
    
    # 1. Search Check
    serper_safe = await scout._serper(f"educational YouTube Shorts kids {topic} 2025", 5)
    print(f"Serper Safe: {len(serper_safe)} items found.")
    
    serper_toxic = await scout._serper(f"viral controversial kids YouTube Shorts {topic} brainrot", 5)
    print(f"Serper Toxic: {len(serper_toxic)} items found.")
    
    combined = scout._dedupe(serper_safe + serper_toxic)
    print(f"Combined Unique: {len(combined)}")
    
    if not combined:
        print("ALERT: NO SEARCH RESULTS FOUND.")
        return

    # 2. Filter Check (RAW)
    print("\n--- SCOUT FILTER (ABACUS/CLAUDE) RAW CHECK ---")
    batch = json.dumps([{"i": idx, "t": x["title"]} for idx, x in enumerate(combined)])
    system = "Return JSON array of integer indices for URLs relevant to YouTube Shorts content for kids aged 4-12. Nothing else."
    user = f"Topic:{topic}\nItems:{batch}"
    
    raw_resp = await model_router.call_llm(
        "abacus", "claude-3-5-sonnet", system, user, max_tokens=150, json_mode=True
    )
    
    print("RAW FILTER OUTPUT:")
    print(raw_resp)
    
    m = re.search(r"\[[\d,\s]*\]", raw_resp)
    if m:
        indices = json.loads(m.group())
        print(f"Parsed Indices: {indices}")
        final = [combined[i] for i in indices if i < len(combined)]
        print(f"Final Count after Filter: {len(final)}")
    else:
        print("ALERT: REGEX FAILED TO FIND INDICES ARRAY.")

if __name__ == "__main__":
    asyncio.run(debug_scout())
