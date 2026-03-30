import asyncio
import os
from dotenv import load_dotenv
from core.orchestrator import run

load_dotenv()

async def test_storyboard():
    print("Testing Storyboard Transformation [Visual vs Audio]...")
    try:
        res = await run("viral kids shorts")
        output = res.model_dump()
        
        prompts = output.get('production_prompts_en', {})
        
        scenes = prompts.get('scenes', [])
        
        print(f"\n--- PROFESSIONAL STORYBOARD (Scenes: {len(scenes)}) ---")
        for s in scenes:
            num = s.get("scene_number")
            vis = s.get("video_prompt", "")
            vo  = s.get("voiceover_text", "")
            print(f"Scene {num}: [Visual: {vis[:60]}...] | [Audio: {vo[:60]}...]")

        if len(scenes) > 0 and "video_prompt" in scenes[0]:
            print("\n✅ SUCCESS: New Scenes Array format detected!")
        else:
            print("\n❌ FAILURE: format not as expected (scenes list missing).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_storyboard())
