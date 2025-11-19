import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

async def test_google_search():
    # Debug: check if we can read the file manually
    try:
        with open(dotenv_path, "r") as f:
            content = f.read()
            if "GOOGLE_SEARCH_API_KEY" in content:
                print(f"DEBUG: Found 'GOOGLE_SEARCH_API_KEY' string in {dotenv_path}")
            else:
                print(f"DEBUG: Did NOT find 'GOOGLE_SEARCH_API_KEY' string in {dotenv_path}")
    except Exception as e:
        print(f"DEBUG: Could not read .env file: {e}")

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    print(f"Checking Google Search Configuration...")
    if api_key:
        print(f"API Key found: Yes ({api_key[:5]}...)")
    else:
        print("API Key found: No")
        
    print(f"Engine ID found: {'Yes' if cx else 'No'} ({cx if cx else 'None'})")
    
    if not api_key or not cx:
        print("\nERROR: Missing configuration!")
        print("Current working directory:", os.getcwd())
        print("Looking for .env file in:", os.path.abspath(".env"))
        print("Does .env exist?", os.path.exists(".env"))
        return

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": "Grace Autonomous AI",
        "num": 1
    }
    
    print("\nSending test query: 'Grace Autonomous AI'...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print("\nSUCCESS: Google Search API is working!")
                if "items" in data:
                    first_result = data["items"][0]
                    print(f"\nFirst Result Title: {first_result.get('title')}")
                    print(f"First Result Link: {first_result.get('link')}")
                else:
                    print("\nAPI worked but returned no results (this is okay, connection is valid).")
            else:
                print(f"\nFAILURE: API returned status {response.status}")
                text = await response.text()
                print(f"Response: {text}")

if __name__ == "__main__":
    # Install aiohttp if missing (simple check)
    try:
        import aiohttp
    except ImportError:
        print("Installing missing dependency: aiohttp...")
        os.system(f"{sys.executable} -m pip install aiohttp python-dotenv")
        import aiohttp

    asyncio.run(test_google_search())
