import os
import re
from collections import defaultdict

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")

if not token:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")


HEADERS = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "RecordHunter/0.1",
}

ACCEPTED_CONDITIONS = {
    "Mint (M)",
    "Near Mint (NM or M-)",
    "Very Good Plus (VG+)",
}

REQUIRED_COUNTRY = "United Kingdom"
MINIMUM_SELLER_RATING = 99.0
MINIMUM_RATING_COUNT = 50


def extract_listing_id(value):
    value = value.strip()

    if value.isdigit():
        return value

    match = re.search(r"/item/(\d+)", value)

    if match:
        return match.group(1)

    return None


def inspect_listing(listing_id):
    url = (
        "https://api.discogs.com/marketplace/listings/"
        f"{listing_id}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        params={"curr_abbr": "GBP"},
        timeout=10,
    )

    response.raise_for_status()
    listing = response.json()

    seller = listing.get("seller", {})
    seller_stats = seller.get("stats", {})
    release = listing.get("release", {})
    price = listing.get("price", {})

    seller_rating = float(seller_stats.get("rating") or 0)
    rating_count = int(seller_stats.get("total") or 0)
    price_value = float(price.get("value") or 0)
    price_currency = price.get("currency") or "Unknown"

    result = {
        "listing_id": str(listing.get("id") or listing_id),
        "release_id": release.get("id"),
        "title": release.get("description") or "Unknown release",
        "seller": seller.get("username") or "Unknown seller",
        "condition": listing.get("condition") or "Not supplied",
        "sleeve_condition": (
            listing.get("sleeve_condition") or "Not supplied"
        ),
        "ships_from": listing.get("ships_from") or "Not supplied",
        "seller_rating": seller_rating,
        "rating_count": rating_count,
        "price_value": price_value,
        "price_currency": price_currency,
        "status": listing.get("status") or "Unknown",
        "reasons": [],
    }

    if result["status"] != "For Sale":
        result["reasons"].append("listing is not currently for sale")

    if result["condition"] not in ACCEPTED_CONDITIONS:
        result["reasons"].append(
            f"media condition is below VG+ ({result['condition']})"
        )

    if result["ships_from"] != REQUIRED_COUNTRY:
        result["reasons"].append(
            f"ships from {result['ships_from']}, not the UK"
        )

    if result["seller_rating"] < MINIMUM_SELLER_RATING:
        result["reasons"].append(
            f"seller rating is below {MINIMUM_SELLER_RATING:.1f}%"
        )

    if result["rating_count"] < MINIMUM_RATING_COUNT:
        result["reasons"].append(
            f"seller has fewer than {MINIMUM_RATING_COUNT} ratings"
        )

    if result["price_value"] <= 0:
        result["reasons"].append("item price is unavailable")

    result["eligible"] = not result["reasons"]

    return result


print("RECORD HUNTER — BATCH CANDIDATE CHECK")
print()
print("Paste one Discogs listing URL or listing ID per line.")
print("Press Enter on an empty line when finished.")
print()

listing_ids = []

while True:
    try:
        entered_value = input("Listing: ").strip()
    except EOFError:
        break

    if not entered_value:
        break

    listing_id = extract_listing_id(entered_value)

    if not listing_id:
        print("Could not find a valid listing ID.")
        continue

    if listing_id in listing_ids:
        print(f"Listing {listing_id} has already been entered.")
        continue

    listing_ids.append(listing_id)


if not listing_ids:
    raise SystemExit("No listing IDs were supplied.")


eligible = []
rejected = []
request_failures = []

print(f"\nChecking {len(listing_ids)} listing(s)...")

for listing_id in listing_ids:
    try:
        result = inspect_listing(listing_id)

        if result["eligible"]:
            eligible.append(result)
            print(f"PASS: {listing_id} — {result['title']}")
        else:
            rejected.append(result)
            print(f"FAIL: {listing_id} — {result['title']}")

    except requests.RequestException as error:
        request_failures.append(
            {
                "listing_id": listing_id,
                "error": str(error),
            }
        )
        print(f"ERROR: {listing_id} could not be checked.")


print("\nBATCH SUMMARY")
print(f"Listings submitted: {len(listing_ids)}")
print(f"Eligible listings: {len(eligible)}")
print(f"Rejected listings: {len(rejected)}")
print(f"Request failures: {len(request_failures)}")


print("\nREJECTED LISTINGS")

if not rejected:
    print("None")

for number, result in enumerate(rejected, start=1):
    print(f"\n{number}. {result['title']}")
    print(f"   Listing ID: {result['listing_id']}")
    print(f"   Seller: {result['seller']}")

    for reason in result["reasons"]:
        print(f"   REJECTED: {reason}")


seller_groups = defaultdict(list)

for result in eligible:
    seller_groups[result["seller"]].append(result)


print("\nELIGIBLE LISTINGS GROUPED BY SELLER")

if not seller_groups:
    print("None")

for seller_number, seller in enumerate(
    sorted(seller_groups),
    start=1,
):
    listings = seller_groups[seller]
    subtotal = sum(item["price_value"] for item in listings)

    print(f"\nSELLER {seller_number}: {seller}")
    print(f"Eligible records: {len(listings)}")

    for item_number, item in enumerate(listings, start=1):
        print(f"\n   {item_number}. {item['title']}")
        print(f"      Release ID: {item['release_id']}")
        print(f"      Listing ID: {item['listing_id']}")
        print(f"      Media: {item['condition']}")
        print(f"      Sleeve: {item['sleeve_condition']}")
        print(
            f"      Price: {item['price_currency']} "
            f"{item['price_value']:.2f}"
        )
        print(
            "      URL: "
            f"https://www.discogs.com/shop/item/"
            f"{item['listing_id']}"
        )

    print(f"\n   Item subtotal: GBP {subtotal:.2f}")
    print("   Shipping: Confirm in the Discogs cart")


print("\nREQUEST FAILURES")

if not request_failures:
    print("None")

for failure in request_failures:
    print(
        f"Listing {failure['listing_id']}: "
        f"{failure['error']}"
    )
