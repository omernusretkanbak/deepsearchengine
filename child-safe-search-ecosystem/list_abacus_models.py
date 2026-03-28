import httpx, os, json
from dotenv import load_dotenv
load_dotenv()
try:
    url = "https://api.abacus.ai/api/v0/listRouteLLMModels"
    api_key = os.environ.get("ABACUSAI_API_KEY")
    response = httpx.get(url, headers={"apiKey": api_key})
    data = response.json()
    if data.get("success"):
        models = data.get("result", [])
        for m in models:
            print(f"ID: {m.get('id')} | Name: {m.get('name')}")
    else:
        print(f"Error: {data}")
except Exception as e:
    print(f"Exception: {e}")
