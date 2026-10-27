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

    wantlist_response = requests.get(
        f"https://api.discogs.com/users/{username}/wants",
        headers=headers,
        params={"per_page": 100},
        timeout=10,
    )
    wantlist_response.raise_for_status()

except requests.RequestException as error:
    raise SystemExit(f"Discogs request failed: {error}")

wants = wantlist_response.json().get("wants", [])

print(f"\nWantlist for {username}")
print(f"Records found: {len(wants)}\n")

if not wants:
    print("Your wantlist is currently empty.")

for number, item in enumerate(wants, start=1):
    release = item["basic_information"]

    artist_names = ", ".join(
        artist["name"] for artist in release.get("artists", [])
    )

    print(
        f"{number}. {artist_names} - {release['title']} "
        f"({release.get('year') or 'Year unknown'}) "
        f"[Release ID: {item['id']}]"
    )
