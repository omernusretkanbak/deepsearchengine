import os
import json
import re
from core.utils.model_router import call_llm

_MODEL      = os.getenv("PRODUCER_MODEL", "gemini-2.0-flash-lite") # Fast, great for creative prompts if structure is simple
_MAX_TOKENS = 3000

_SYSTEM = (
    "You are an Elite Media Director and AI Prompt Engineer. "
    "Your client wants to create highly engaging, massively viral YouTube Shorts for kids (4-12 yo), "
    "but ethically strictly avoids 'brainrot' or harmful content. "
    "You will receive a TURKISH STRATEGY (written by the Lead Analyst) that tells you exactly how to capture the viewer's attention. "
    "Your ONLY job is to convert that strategy into a hyper-detailed, strictly structured English 5-stage JSON production plan. "
    "CRITICAL RULE FOR HEROES: To make children love healthy choices, the 'heroes' of your scripts MUST always be "
    "anthropomorphized, cute, animated healthy foods (like a brave broccoli, a speedy strawberry, or strong milk/egg characters). "
    "CRITICAL JSON RULE: DO NOT use manual line breaks (literal newlines) or unescaped quotes inside any JSON string. "
    "Use '\\n' for newlines to prevent JSON parse errors. "
    "Output ONLY VALID JSON."
)

_USER_TMPL = """\
TURKISH STRATEGY TO IMPLEMENT:
{{strategy}}

Return ONLY this exact JSON structure:
{
  "hero_concept": "Describe the healthy food hero character (e.g., A brave, hyper-energetic running Strawberry wearing tiny sneakers)",
  "image_prompt": "Midjourney/DALL-E English prompt to generate this character in an engaging background. Must end with --ar 9:16",
  "script": "A 9:16 vertical video English script (fast-paced, high energy, safe content) featuring this hero.\\nUse '\\n' for newlines.",
  "video_prompt": "Sora/Runway image-to-video AI prompt to animate this image. Specify the aspect ratio mapping to 9:16 and let the AI determine the best duration for the fast-paced loop.",
  "voiceover_text": "The exact pure English text for the voiceover (TTS) tool to read, enthusiastically!"
}"""

def _parse(resp: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", resp).strip().rstrip("`")
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        return {}
    json_str = m.group()
    try:
        return json.loads(json_str) # Try native
    except json.JSONDecodeError:
        pass
    
    # Aggressive Scrubber if it fails
    scrubbed_json = json_str.replace('\n', '\\n').replace('\r', '')
    try:
        return json.loads(scrubbed_json)
    except Exception:
        return {}

async def generate(strategy: str) -> dict:
    """Takes the strategic_consulting_tr text and converts it into pure English production prompts."""
    # If strategy is totally empty or an error message, we skip heavy LLM usage
    if not strategy or "üretilemedi" in strategy.lower():
        return {}
        
    user_prompt = _USER_TMPL.replace("{{strategy}}", strategy)
    
    resp = await call_llm(
        "abacus", _MODEL, _SYSTEM, user_prompt, max_tokens=_MAX_TOKENS, json_mode=True
    )
    print(f"[PRODUCER DEBUG] LLM Response Length: {len(resp)}")
    return _parse(resp)
