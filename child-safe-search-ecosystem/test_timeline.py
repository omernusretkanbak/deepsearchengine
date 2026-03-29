import asyncio
import os
import json
from dotenv import load_dotenv
from core.orchestrator import run

load_dotenv()

async def test_timeline():
    print("Testing Full Timeline Array Automation Output...")
    try:
        res = await run("viral kids animation shorts")
        output = res.model_dump()
        
        prompts = output.get('production_prompts_en', {})
        print("\n=== TOP LEVEL METADATA ===")
        print(f"Hero Concept: {prompts.get('hero_concept', '')[:50]}...")
        print(f"Image Anchor: {prompts.get('image_anchor_prompt', '')[:50]}...")
        
        scenes = prompts.get('scenes', [])
        print(f"\n=== SCENES PARSED: {len(scenes)} ===")
        
        for s in scenes:
            print(f"[{s.get('start_timestamp_sec')}-{s.get('end_timestamp_sec')}s]")
            print(f"  Visual : {s.get('video_prompt')}")
            print(f"  Audio  : {s.get('voiceover_text')}\n")
            
        if len(scenes) > 1:
            print("✅ SUCCESS: Loopable Data Structure Verified!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_timeline())
