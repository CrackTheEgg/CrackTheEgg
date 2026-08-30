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

headers = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "RecordHunter/0.1",
}

try:
    response = requests.get(
        (
            "https://api.discogs.com/marketplace/listings/"
            f"{listing_id}"
        ),
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    listing = response.json()

except requests.RequestException as error:
    raise SystemExit(f"Discogs request failed: {error}")

accepted_conditions = {
    "Mint (M)",
    "Near Mint (NM or M-)",
    "Very Good Plus (VG+)",
}

minimum_seller_rating = 99.0
minimum_rating_count = 50
required_shipping_country = "United Kingdom"

release = listing.get("release", {})
seller = listing.get("seller", {})
seller_stats = seller.get("stats", {})
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

seller_rating = float(
    seller_stats.get("rating") or 0
)

seller_rating_count = int(
    seller_stats.get("total") or 0
)

media_pass = media_condition in accepted_conditions

country_pass = (
    ships_from.casefold()
    == required_shipping_country.casefold()
)

rating_pass = (
    seller_rating >= minimum_seller_rating
)

rating_count_pass = (
    seller_rating_count >= minimum_rating_count
)

print("\nLISTING INSPECTION")
print(f"Listing ID: {listing_id}")
print(
    f"Release: "
    f"{release.get('description', 'Description unavailable')}"
)
print(f"Seller: {seller.get('username', 'Unknown')}")
print(f"Status: {listing.get('status', 'Unknown')}")
print(f"Media condition: {media_condition}")
print(f"Sleeve condition: {sleeve_condition}")
print(f"Ships from: {ships_from or 'Not supplied'}")
print(f"Seller rating: {seller_rating:.1f}%")
print(f"Seller rating count: {seller_rating_count}")

if price:
    print(
        f"Item price: "
        f"{price.get('currency')} "
        f"{float(price.get('value', 0)):.2f}"
    )

print("\nELIGIBILITY RULES")

if media_pass:
    print("PASS — media condition is VG+ or better.")
else:
    print("FAIL — media condition is below VG+.")

if country_pass:
    print("PASS — listing ships from the United Kingdom.")
else:
    print("FAIL — listing does not ship from the United Kingdom.")

if rating_pass:
    print(
        f"PASS — seller rating meets the "
        f"{minimum_seller_rating:.1f}% minimum."
    )
else:
    print(
        f"FAIL — seller rating is below the "
        f"{minimum_seller_rating:.1f}% minimum."
    )

if rating_count_pass:
    print(
        f"PASS — seller has at least "
        f"{minimum_rating_count} ratings."
    )
else:
    print(
        f"FAIL — seller has fewer than "
        f"{minimum_rating_count} ratings."
    )

eligible = all(
    (
        media_pass,
        country_pass,
        rating_pass,
        rating_count_pass,
    )
)

print("\nOVERALL RESULT")

if eligible:
    print("ELIGIBLE — listing passes every current rule.")
else:
    print("REJECTED — listing fails one or more rules.")
