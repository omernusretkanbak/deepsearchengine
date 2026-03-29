import yt_dlp
import json

def test_ytdlp():
    url = "https://www.youtube.com/shorts/XPfwhGZMxKQ"
    
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'extract_flat': False,
        'extractor_args': {'youtube': {'client': ['android', 'ios']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print("SUCCESS! Metrics retrieved:")
            print(f"Title: {info.get('title')}")
            print(f"View Count: {info.get('view_count')}")
            print(f"Like Count: {info.get('like_count')}")
            print(f"Description: {info.get('description', '')[:100]}")
    except Exception as e:
        print(f"FAILED: {e}")

test_ytdlp()
