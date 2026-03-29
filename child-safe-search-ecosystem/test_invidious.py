import requests

def test_invidious():
    video_id = "XPfwhGZMxKQ"
    instances = [
        "https://vid.priv.au", 
        "https://invidious.fdn.fr", 
        "https://invidious.nerdvpn.de"
    ]
    for inst in instances:
        try:
            url = f"{inst}/api/v1/videos/{video_id}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                print(f"SUCCESS on {inst}:")
                print(f"Views: {data.get('viewCount')}")
                return
        except Exception as e:
            print(f"FAILED on {inst}: {e}")

test_invidious()
