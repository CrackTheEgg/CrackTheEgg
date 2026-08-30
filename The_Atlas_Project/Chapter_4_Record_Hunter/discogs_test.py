import os

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")

if not token:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")

headers = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "DiscogsAgentTest/0.1",
}

try:
    response = requests.get(
        "https://api.discogs.com/oauth/identity",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
except requests.RequestException as error:
    raise SystemExit(f"Discogs connection failed: {error}")

account = response.json()
print(f"Connected successfully as: {account['username']}")
