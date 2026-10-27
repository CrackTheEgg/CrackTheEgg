import os
import re

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")

if not token:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")

listing_reference = input(
    "Paste a Discogs listing URL or listing ID: "
).strip()

numbers = re.findall(r"\d+", listing_reference)

if not numbers:
    raise SystemExit("No listing ID was found.")

listing_id = numbers[-1]

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Discogs token={token}",
        "User-Agent": "RecordHunter/0.1",
    }
)


def get_json(url):
    try:
        response = session.get(
            url,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        raise SystemExit(f"Discogs request failed: {error}")


def is_confirmed_uk_location(location):
    normalized = location.casefold()

    uk_markers = (
        "united kingdom",
        "england",
        "scotland",
        "wales",
        "northern ireland",
        "great britain",
    )

    if any(marker in normalized for marker in uk_markers):
        return True

    return bool(re.search(r"\buk\b", normalized))


listing = get_json(
    (
        "https://api.discogs.com/marketplace/listings/"
        f"{listing_id}"
    )
)

seller = listing.get("seller", {})
print("\nAVAILABLE LISTING FIELDS")
print(sorted(listing.keys()))

print("\nAVAILABLE SELLER FIELDS")
print(sorted(seller.keys()))

print("\nPOSSIBLE SHIPPING LOCATION VALUES")
print(f"Listing ships_from: {listing.get('ships_from')}")
print(f"Listing country: {listing.get('country')}")
print(f"Listing location: {listing.get('location')}")
print(f"Seller ships_from: {seller.get('ships_from')}")
print(f"Seller country: {seller.get('country')}")
print(f"Seller location: {seller.get('location')}")
seller_username = seller.get("username")

if not seller_username:
    raise SystemExit("No seller username was found.")

seller_profile = get_json(
    f"https://api.discogs.com/users/{seller_username}"
)

print("\nSELLER RATING DATA")
print(
    f"Listing seller stats: "
    f"{seller.get('stats')}"
)
print(
    f"Profile seller rating: "
    f"{seller_profile.get('seller_rating')}"
)
print(
    f"Profile seller rating count: "
    f"{seller_profile.get('seller_num_ratings')}"
)

accepted_conditions = {
    "Mint (M)",
    "Near Mint (NM or M-)",
    "Very Good Plus (VG+)",
}

release = listing.get("release", {})
price = listing.get("price", {})

media_condition = listing.get(
    "condition",
    "Condition unavailable",
)

sleeve_condition = listing.get(
    "sleeve_condition",
    "Sleeve condition unavailable",
)

ships_from = (
    listing.get("ships_from") or ""
).strip()

media_pass = media_condition in accepted_conditions
uk_location_pass = (
    ships_from.casefold() == "united kingdom"
)

print("\nLISTING AND SELLER INSPECTION")
print(f"Listing ID: {listing_id}")
print(
    f"Release: "
    f"{release.get('description', 'Description unavailable')}"
)
print(f"Seller: {seller_username}")
print(f"Media condition: {media_condition}")
print(f"Sleeve condition: {sleeve_condition}")
print(
    f"Ships from: "
    f"{ships_from or 'Not supplied'}"
)
 

if price:
    print(
        f"Item price: "
        f"{price.get('currency')} "
        f"{float(price.get('value', 0)):.2f}"
    )

print("\nFILTER RESULTS")

if media_pass:
    print("PASS — media condition is VG+ or better.")
else:
    print("FAIL — media condition is below VG+.")

if uk_location_pass:
    print("PASS — seller profile confirms a UK location.")
else:
    print("FAIL — a UK seller location was not confirmed.")

print("\nOVERALL RESULT")

if media_pass and uk_location_pass:
    print("ELIGIBLE — passes media and UK-location rules.")
else:
    print("REJECTED — does not pass all current rules.")
