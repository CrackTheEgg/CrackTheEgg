import os

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")
list_id = 1711500

if not token:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Discogs token={token}",
        "User-Agent": "DiscogsAgentTest/0.1",
    }
)


def get_json(url, params=None):
    try:
        response = session.get(
            url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        raise SystemExit(f"Discogs request failed: {error}")


# Identify the authenticated account.
identity = get_json("https://api.discogs.com/oauth/identity")
username = identity["username"]

# Retrieve the selected normal list.
discogs_list = get_json(
    f"https://api.discogs.com/lists/{list_id}"
)

list_releases = [
    item
    for item in discogs_list.get("items", [])
    if item.get("type", "").lower() == "release"
]

# Retrieve every page of the user's collection.
collection_releases = []
page = 1

while True:
    collection_page = get_json(
        (
            f"https://api.discogs.com/users/{username}"
            "/collection/folders/0/releases"
        ),
        params={
            "page": page,
            "per_page": 100,
        },
    )

    collection_releases.extend(
        collection_page.get("releases", [])
    )

    pagination = collection_page.get("pagination", {})
    total_pages = pagination.get("pages", 1)

    if page >= total_pages:
        break

    page += 1

collection_ids = {
    release["id"] for release in collection_releases
}

owned = [
    item for item in list_releases
    if item["id"] in collection_ids
]

not_owned = [
    item for item in list_releases
    if item["id"] not in collection_ids
]

print(f"\nList: {discogs_list['name']}")
print(f"Releases in list: {len(list_releases)}")
print(f"Exact releases already owned: {len(owned)}")
print(f"Exact releases not owned: {len(not_owned)}")

print("\nALREADY OWNED — EXCLUDED")

if not owned:
    print("None")

for number, item in enumerate(owned, start=1):
    print(
        f"{number}. {item['display_title']} "
        f"[Release ID: {item['id']}]"
    )

print("\nNOT OWNED — RETAINED")

if not not_owned:
    print("None")

for number, item in enumerate(not_owned, start=1):
    print(
        f"{number}. {item['display_title']} "
        f"[Release ID: {item['id']}]"
    )

print("\nMARKETPLACE CHECK — MISSING RELEASES")

available = []
unavailable = []

for item in not_owned:
    statistics = get_json(
        (
            "https://api.discogs.com/marketplace/stats/"
            f"{item['id']}"
        ),
        params={"curr_abbr": "GBP"},
    )

    copies_for_sale = statistics.get("num_for_sale") or 0
    lowest_price = statistics.get("lowest_price")

    result = {
        "title": item["display_title"],
        "release_id": item["id"],
        "copies_for_sale": copies_for_sale,
        "lowest_price": lowest_price,
    }

    if copies_for_sale > 0 and lowest_price:
        available.append(result)
    else:
        unavailable.append(result)

print(f"\nMissing releases checked: {len(not_owned)}")
print(f"Available for sale: {len(available)}")
print(f"Currently unavailable: {len(unavailable)}")

print("\nAVAILABLE FOR SALE")

if not available:
    print("None")

for number, result in enumerate(available, start=1):
    price = result["lowest_price"]
    price_value = float(price["value"])

    print(f"\n{number}. {result['title']}")
    print(f"   Release ID: {result['release_id']}")
    print(f"   Copies for sale: {result['copies_for_sale']}")
    print(
        f"   Lowest advertised price: "
        f"{price['currency']} {price_value:.2f}"
    )

print("\nCURRENTLY UNAVAILABLE")

if not unavailable:
    print("None")

for number, result in enumerate(unavailable, start=1):
    print(
        f"{number}. {result['title']} "
        f"[Release ID: {result['release_id']}]"
    )
