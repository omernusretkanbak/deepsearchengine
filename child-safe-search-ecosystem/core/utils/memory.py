from pathlib import Path
from datetime import datetime

_MEMORY = Path(__file__).resolve().parents[2] / "knowledge" / "memory.md"



def read() -> str:
    return _MEMORY.read_text(encoding="utf-8") if _MEMORY.exists() else ""


def append(section: str, content: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n### [{ts}] {section}\n{content}\n"
    with _MEMORY.open("a", encoding="utf-8") as f:
        f.write(entry)
