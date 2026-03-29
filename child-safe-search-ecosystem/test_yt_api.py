import asyncio
from core.agents.extractor import _youtube_api
from dotenv import load_dotenv

load_dotenv()

async def test():
    urls = [
        "https://www.youtube.com/shorts/XPfwhGZMxKQ", # Shorts
        "https://www.youtube.com/watch?v=WiXLVmc4_BA", # Video
        "https://www.youtube.com/playlist?list=PL1mcKAV0d2iM7GaykXqMox8ngVtki6LJZ" # Playlist
    ]
    for url in urls:
        print(f"Testing: {url}")
        res = await _youtube_api(url)
        print(f"Result: {res}\n")

asyncio.run(test())
