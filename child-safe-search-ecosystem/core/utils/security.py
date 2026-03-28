import re

# Compiled patterns — covers all 4 provider key formats
_PATTERNS = [
    re.compile(r'sk-ant-[a-zA-Z0-9\-_]{20,}'),   # Anthropic
    re.compile(r'sk-[a-zA-Z0-9]{20,}'),            # OpenAI
    re.compile(r'AIza[a-zA-Z0-9\-_]{35,}'),        # Google
    re.compile(r'tvly-[a-zA-Z0-9]{20,}'),          # Tavily
    re.compile(r'(?i)bearer\s+[a-zA-Z0-9\-_\.]{16,}'),  # Generic Bearer
]


def scrub(text: str) -> str:
    """Redact all known API key patterns from a string."""
    for p in _PATTERNS:
        text = p.sub('***REDACTED***', text)
    return text
