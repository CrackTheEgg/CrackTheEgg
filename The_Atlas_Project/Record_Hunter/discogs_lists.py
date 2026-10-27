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
    identity_response = requests.get(
        "https://api.discogs.com/oauth/identity",
        headers=headers,
        timeout=10,
    )
    identity_response.raise_for_status()

    username = identity_response.json()["username"]

    lists_response = requests.get(
        f"https://api.discogs.com/users/{username}/lists",
        headers=headers,
        params={"per_page": 100},
        timeout=10,
    )
    lists_response.raise_for_status()

except requests.RequestException as error:
    raise SystemExit(f"Discogs request failed: {error}")

lists = lists_response.json().get("lists", [])

print(f"\nLists belonging to {username}")
print(f"Lists found: {len(lists)}\n")

if not lists:
    print("No normal lists were found.")

for number, discogs_list in enumerate(lists, start=1):
    visibility = "Public" if discogs_list.get("public") else "Private"

    print(
        f"{number}. {discogs_list['name']} "
        f"[List ID: {discogs_list['id']}] "
        f"[{visibility}]"
    )
