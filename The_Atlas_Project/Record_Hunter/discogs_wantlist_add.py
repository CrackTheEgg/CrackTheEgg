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
        "User-Agent": "RecordHunter/0.1",
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


def get_all_pages(url, result_key):
    results = []
    page = 1

    while True:
        data = get_json(
            url,
            params={
                "page": page,
                "per_page": 100,
            },
        )

        results.extend(data.get(result_key, []))

        pagination = data.get("pagination", {})
        total_pages = pagination.get("pages", 1)

        if page >= total_pages:
            break

        page += 1

    return results


# Identify the authenticated Discogs account.
identity = get_json(
    "https://api.discogs.com/oauth/identity"
)
username = identity["username"]

# Retrieve the selected private list.
discogs_list = get_json(
    f"https://api.discogs.com/lists/{list_id}"
)

list_releases = [
    item
    for item in discogs_list.get("items", [])
    if item.get("type", "").lower() == "release"
]

# Retrieve the complete collection.
collection_releases = get_all_pages(
    (
        f"https://api.discogs.com/users/{username}"
        "/collection/folders/0/releases"
    ),
    "releases",
)

collection_ids = {
    release["id"] for release in collection_releases
}

# Retrieve the complete wantlist.
wantlist_releases = get_all_pages(
    f"https://api.discogs.com/users/{username}/wants",
    "wants",
)

wantlist_ids = {
    release["id"] for release in wantlist_releases
}

# Classify releases from the selected list.
owned = [
    item
    for item in list_releases
    if item["id"] in collection_ids
]

wanted = [
    item
    for item in list_releases
    if (
        item["id"] not in collection_ids
        and item["id"] in wantlist_ids
    )
]

neither = [
    item
    for item in list_releases
    if (
        item["id"] not in collection_ids
        and item["id"] not in wantlist_ids
    )
]

owned_and_wanted = [
    item
    for item in list_releases
    if (
        item["id"] in collection_ids
        and item["id"] in wantlist_ids
    )
]


def print_releases(heading, releases):
    print(f"\n{heading}")

    if not releases:
        print("None")
        return

    for number, item in enumerate(releases, start=1):
        print(
            f"{number}. {item['display_title']} "
            f"[Release ID: {item['id']}]"
        )


print(f"\nLIST ANALYSIS: {discogs_list['name']}")
print(f"Total releases in list: {len(list_releases)}")
print(f"Already owned: {len(owned)}")
print(f"Not owned but already wanted: {len(wanted)}")
print(f"Neither owned nor wanted: {len(neither)}")

print_releases(
    "ALREADY OWNED — EXCLUDED",
    owned,
)

print_releases(
    "NOT OWNED BUT ALREADY IN WANTLIST",
    wanted,
)

print_releases(
    "NEITHER OWNED NOR WANTED — CANDIDATES TO ADD",
    neither,
)

if owned_and_wanted:
    print_releases(
        "NOTICE — OWNED BUT STILL IN WANTLIST",
        owned_and_wanted,
    )

if not neither:
    print("\nNo releases need adding to the wantlist.")
    raise SystemExit(0)

print(
    f"\nRecord Hunter found {len(neither)} "
    "release(s) that are neither owned nor wanted."
)

required_confirmation = f"ADD {len(neither)}"

confirmation = input(
    f"Type {required_confirmation} to add them "
    "to your Discogs wantlist: "
)

if confirmation.strip().upper() != required_confirmation:
    print("\nCancelled. No Discogs data was changed.")
    raise SystemExit(0)

print("\nADDING RELEASES TO WANTLIST")

added = []
failed = []

for item in neither:
    try:
        response = session.put(
            (
                f"https://api.discogs.com/users/{username}"
                f"/wants/{item['id']}"
            ),
            timeout=10,
        )
        response.raise_for_status()

        added.append(item)

        print(
            f"Added: {item['display_title']} "
            f"[Release ID: {item['id']}]"
        )

    except requests.RequestException as error:
        failed.append(item)

        print(
            f"FAILED: {item['display_title']} "
            f"[Release ID: {item['id']}] — {error}"
        )

# Reload the wantlist and verify the changes.
updated_wantlist = get_all_pages(
    f"https://api.discogs.com/users/{username}/wants",
    "wants",
)

updated_wantlist_ids = {
    release["id"] for release in updated_wantlist
}

verified = [
    item
    for item in added
    if item["id"] in updated_wantlist_ids
]

print("\nWANTLIST UPDATE SUMMARY")
print(f"Requested: {len(neither)}")
print(f"Added successfully: {len(added)}")
print(f"Verified in wantlist: {len(verified)}")
print(f"Failed: {len(failed)}")
