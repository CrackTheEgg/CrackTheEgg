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

release = listing.get("release", {})
seller = listing.get("seller", {})
price = listing.get("price", {})

media_condition = listing.get(
    "condition",
    "Condition unavailable",
)

sleeve_condition = listing.get(
    "sleeve_condition",
    "Sleeve condition unavailable",
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

if price:
    print(
        f"Item price: "
        f"{price.get('currency')} "
        f"{float(price.get('value', 0)):.2f}"
    )

print("\nMEDIA CONDITION RESULT")

if media_condition in accepted_conditions:
    print("ELIGIBLE — media condition is VG+ or better.")
else:
    print("REJECTED — media condition is below VG+.")
