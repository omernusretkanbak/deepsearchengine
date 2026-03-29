import asyncio
import os
from dotenv import load_dotenv
from core.utils.model_router import call_llm

load_dotenv()

async def debug_llm():
    print("--- TESTING ABACUS (Primary) ---")
    try:
        resp = await call_llm("abacus", "route-llm", "You are a helpful assistant.", "Say hi.", max_tokens=10)
        print(f"Abacus Success: {resp}")
    except Exception as e:
        print(f"Abacus Failed: {e}")

    print("\n--- TESTING GOOGLE (Fallback) ---")
    try:
        resp = await call_llm("google", "gemini-1.5-flash", "You are a helpful assistant.", "Say hi.", max_tokens=10)
        print(f"Google Success: {resp}")
    except Exception as e:
        print(f"Google Failed: {e}")

    print("\n--- TESTING OPENAI ---")
    try:
        resp = await call_llm("openai", "gpt-4o-mini", "You are a helpful assistant.", "Say hi.", max_tokens=10)
        print(f"OpenAI Success: {resp}")
    except Exception as e:
        print(f"OpenAI Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_llm())
