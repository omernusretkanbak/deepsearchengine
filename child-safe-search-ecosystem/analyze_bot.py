import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def analyze_video(video_id: str):
    api_key = os.environ.get("YOUTUBE_DATA_API_V3_API_KEY", os.environ.get("YOUTUBE_API_KEY", ""))
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    
    async with httpx.AsyncClient() as c:
        r = await c.get(url)
        data = r.json()
        
        if not data.get("items"):
            print("Video not found or deleted.")
            return

        item = data["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]
        
        title = snippet.get("title")
        channel = snippet.get("channelTitle")
        published = snippet.get("publishedAt")
        
        views = int(stats.get("viewCount", "0"))
        likes = int(stats.get("likeCount", "0"))
        comments = int(stats.get("commentCount", "0"))
        
        # Calculate engagement rates
        like_ratio = (likes / views * 100) if views > 0 else 0
        comment_ratio = (comments / views * 100) if views > 0 else 0
        
        print(f"--- Video Analysis: {video_id} ---")
        print(f"Title: {title}")
        print(f"Channel: {channel}")
        print(f"Published: {published}")
        print(f"Views: {views:,}")
        print(f"Likes: {likes:,}  (Ratio: {like_ratio:.4f}%)")
        print(f"Comments: {comments:,} (Ratio: {comment_ratio:.4f}%)")
        
        if like_ratio < 0.5:
            print("[ALERT] Exceptionally LOW Like Ratio! Normal shorts have 3-5%. This heavily implies padded/bot views or Ads.")
        if comment_ratio < 0.01:
            print("[ALERT] Exceptionally LOW Comment Ratio! This implies bot activity, disabled comments (kid content), or fake engagement.")

asyncio.run(analyze_video("mRPstTWZvQM"))
