"""
Multi-provider LLM router.
Lazy-initializes clients. Exposes a single async call_llm() interface.
Token-compact: system prompts kept short by design — max_tokens enforced on every call.
"""

import os
import asyncio
import logging
import anthropic

import openai as _openai
from google import genai
from google.genai import types as gtypes
from functools import lru_cache


# ── Client factories (one instance per provider) ─────────────

@lru_cache(maxsize=1)
def _anthropic() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@lru_cache(maxsize=1)
def _openai_client() -> _openai.AsyncOpenAI:
    return _openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


@lru_cache(maxsize=1)
def _google() -> genai.Client:
    return genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


@lru_cache(maxsize=1)
def _abacus_client() -> _openai.AsyncOpenAI:
    # Abacus RouteLLM sometimes expects 'apiKey' header specifically
    return _openai.AsyncOpenAI(
        api_key=os.environ["ABACUSAI_API_KEY"],
        base_url="https://routellm.abacus.ai/v1",
        default_headers={"apiKey": os.environ["ABACUSAI_API_KEY"]}
    )


# ── Unified async interface ───────────────────────────────────


async def call_llm(
    provider: str,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 1024,
    json_mode: bool = False,
) -> str:
    """
    provider: "anthropic" | "google" | "openai"
    json_mode: forces JSON-only output (reduces parsing tokens)
    Includes 3x retry for rate limits.
    """
    last_err = None
    for attempt in range(1, 6):

        try:
            if provider == "anthropic":
                msg = await _anthropic().messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                return msg.content[0].text

            elif provider == "google":
                cfg = gtypes.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json" if json_mode else "text/plain",
                )
                resp = await _google().aio.models.generate_content(
                    model=model,
                    contents=user,
                    config=cfg,
                )
                return resp.text

            elif provider == "openai":
                kwargs: dict = dict(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = await _openai_client().chat.completions.create(**kwargs)
                return resp.choices[0].message.content

            elif provider == "abacus":
                messages = [
                    {"role": "user", "content": f"{system}\n\nUSER REQUEST: {user}"}
                ]
                kwargs: dict = dict(
                    model=model,
                    max_tokens=max_tokens,
                    messages=messages,
                )
                if json_mode and "route-llm" not in model:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = await _abacus_client().chat.completions.create(**kwargs)
                return resp.choices[0].message.content

            else:

                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            last_err = e
            msg = str(e).lower()
            # 429 (Rate Limit), 503 (Overload), Timeout veya Bağlantı kopmaları
            if any(k in msg for k in ["429", "exhausted", "rate limit", "503", "timeout", "connection", "read"]):
                import random
                # Akıllı bekleyiş (Exponential Backoff + Jitter)
                wait = (2 ** attempt) + random.uniform(1.0, 3.0)
                print(f"[RETRY {attempt}/5] LLM {provider} network/rate limit error. Sleeping for {wait:.2f}s...")
                await asyncio.sleep(wait)
                continue

            raise e

    # EĞER BÜTÜN DENEMELERE RAĞMEN ÇÖKERSE: "Google Gemini" Fallback'ine geç!
    if provider != "google":
        print(f"[LLM FATAL] Provider '{provider}' failed completely. Swapping to Google Gemini-1.5-Flash as last resort.")
        return await call_llm("google", "gemini-1.5-flash", system, user, max_tokens, json_mode)

    raise last_err
