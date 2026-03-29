import asyncio
import json
import time
import os
from dotenv import load_dotenv
from core.orchestrator import run
import traceback

# Load environment variables (API keys)
load_dotenv()

async def test_full_pipeline():
    print("Testing Dual-Agent Pipeline (Analyst -> Producer)...")
    start = time.time()
    try:
        res = await run("viral kids shorts")
        end = time.time()
        
        output_dict = res.model_dump()
        
        print("\n=== PIPELINE COMPLETED ===")
        print(f"Total Time: {end-start:.2f} seconds")
        print(f"Model Stack: {output_dict['automation_metadata']['model_used']}")
        print(f"Total Videos Analyzed: {len(output_dict['results'])}")
        
        # Check Strategy
        strategy = output_dict.get('strategic_consulting_tr', '')
        print(f"\n[Analyst] Strategy Generated: {'YES' if strategy and 'üretilemedi' not in strategy else 'NO'}")
        print(f"Preview: {strategy[:100]}...")
        
        # Check Production Prompts
        prompts = output_dict.get('production_prompts_en', {})
        print(f"\n[Producer] Prompts Generated: {'YES' if prompts and prompts.get('hero_concept') else 'NO'}")
        if prompts:
            print(f" - Hero: {prompts.get('hero_concept', '')[:50]}...")
            print(f" - Script Length: {len(prompts.get('script', ''))} chars")
            
    except Exception as e:
        print("\n=== PIPELINE FAILED ===")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
