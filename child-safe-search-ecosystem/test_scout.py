import asyncio
from core.agents import scout
from dotenv import load_dotenv
import json

load_dotenv()

async def test_scout():
    topic = "viral kids 2025 shorts"
    print(f"Testing scout for topic: {topic}")
    
    # 1. Test raw serper
    q_safe  = f"educational YouTube Shorts kids {topic} 2025"
    s_safe = await scout._serper(q_safe, num=10)
    print(f"Serper Safe returned {len(s_safe)} items")
    
    q_toxic = f"viral controversial kids YouTube Shorts {topic} brainrot"
    s_toxic = await scout._serper(q_toxic, num=10)
    print(f"Serper Toxic returned {len(s_toxic)} items")
    
    # 2. Test Dedupe
    combined = scout._dedupe(s_safe + s_toxic)
    print(f"Dedupe length: {len(combined)}")
    for i in combined:
        print(f"  - {i['url']}")
        
    # 3. Test filter
    filtered = await scout._filter(combined, topic)
    print(f"Filtered length: {len(filtered)}")
    print(json.dumps(filtered, indent=2))

asyncio.run(test_scout())
