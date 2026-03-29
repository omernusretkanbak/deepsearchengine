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
        
        print("\n--- PROFESSIONAL STORYBOARD (Script Field) ---")
        print(prompts.get('script', 'EMPTY'))
        
        print("\n--- PURE NARRATION (Voiceover Field) ---")
        print(prompts.get('voiceover_text', 'EMPTY'))
        
        if "|" in prompts.get('script', '') and "[" in prompts.get('script', ''):
            print("\n✅ SUCCESS: Storyboard format detected!")
        else:
            print("\n❌ FAILURE: format not as expected.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_storyboard())
