import os
import json
import re
from core.utils.model_router import call_llm

_MODEL      = os.getenv("PRODUCER_MODEL", "gpt-4o-mini") # Fast, great for creative prompts if structure is simple
_MAX_TOKENS = 3000

_SYSTEM = (
    "You are an Elite Media Director and AI Prompt Engineer. "
    "Your client wants to create highly engaging, viral YouTube Shorts for kids (4-12 yo), "
    "but ethically strictly avoids 'brainrot' or harmful content. "
    "You will receive a TURKISH STRATEGY that tells you how to capture the viewer's attention. "
    "Your ONLY job is to convert that strategy into a hyper-detailed, strictly structured English JSON plan. "
    "CRITICAL STORYBOARD RULE: The 'script' field must NOT be a simple paragraph. It MUST be a time-stamped "
    "storyboard following this format for each beat: '[Start-End Time] | Visual: (what happens on screen) | Audio: (what is said)'. "
    "The 'voiceover_text' field must be CLEAN TEXT (pure narration) only, no timestamps, ready for TTS tools. "
    "CRITICAL HERO RULE: Use anthropomorphized, cute healthy foods (Brave Broccoli, Speedy Strawberry, Strong Egg)."
)

_USER_TMPL = """\
TURKISH STRATEGY TO IMPLEMENT:
{{strategy}}

Return ONLY this exact JSON structure:
{
  "hero_concept": "Detailed description of the healthy food character.",
  "image_prompt": "Midjourney prompt for the hero, vertical 9:16 aspect ratio.",
  "script": "[00:00-00:05] | Visual: (Scene description) | Audio: (Script text)\\n[00:05-00:10] | Visual: (Scene description) | Audio: (Script text)...",
  "video_prompt": "Instructions to animate the visual scenes above, specifying camera movements and aspect ratio.",
  "voiceover_text": "Pure English speech text for TTS - CLEAN, NO metadata."
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
