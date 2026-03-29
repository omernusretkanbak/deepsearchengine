import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_yt_search():
    api_key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YOUTUBE_DATA_API_V3_API_KEY")
    query = "kids animation"
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&videoDuration=short&order=viewCount&maxResults=10&key={api_key}"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        print(f"Status: {r.status_code}")
        for item in data.get("items", []):
            vid = item['id']['videoId']
            title = item['snippet']['title']
            print(f"https://www.youtube.com/shorts/{vid} - {title}")

asyncio.run(test_yt_search())
