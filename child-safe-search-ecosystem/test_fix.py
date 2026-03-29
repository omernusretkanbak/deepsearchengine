import asyncio
import os
import time
from dotenv import load_dotenv
from core.orchestrator import run

load_dotenv()

async def test_fix():
    print("Testing Producer Fix with gpt-4o-mini on Abacus...")
    try:
        res = await run("viral kids shorts")
        output = res.model_dump()
        
        print(f"\nModel Used: {output['automation_metadata']['model_used']}")
        print(f"Strategy: {'OK' if output['strategic_consulting_tr'] else 'EMPTY'}")
        
        prompts = output.get('production_prompts_en', {})
        print(f"Production Prompts (Hero): {prompts.get('hero_concept', 'EMPTY')}")
        
        if prompts.get('hero_concept'):
            print("\n✅ SUCCESS: Producer is working!")
        else:
            print("\n❌ FAILURE: Producer is still empty.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fix())
