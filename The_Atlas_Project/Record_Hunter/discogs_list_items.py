import os

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")
list_id = 1711500

if not token:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")

headers = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "DiscogsAgentTest/0.1",
}

try:
    response = requests.get(
        f"https://api.discogs.com/lists/{list_id}",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

except requests.RequestException as error:
    raise SystemExit(f"Discogs request failed: {error}")

discogs_list = response.json()
items = discogs_list.get("items", [])

print(f"\nList: {discogs_list['name']}")
print(f"Items found: {len(items)}\n")

if not items:
    print("This list is empty.")

for number, item in enumerate(items, start=1):
    item_type = item.get("type", "unknown").title()
    title = item.get("display_title", "Title unavailable")
    item_id = item.get("id", "Unknown")

    print(
        f"{number}. {title} "
        f"[{item_type} ID: {item_id}]"
    )
