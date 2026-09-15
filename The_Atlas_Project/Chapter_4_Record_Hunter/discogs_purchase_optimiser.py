import os
import re
from itertools import product
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_DIRECTORY = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIRECTORY / ".env"
CANDIDATE_FILE = PROJECT_DIRECTORY / "candidate_links.txt"

load_dotenv(ENV_FILE)

DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")

if not DISCOGS_TOKEN:
    raise SystemExit("DISCOGS_TOKEN was not found in the .env file.")


HEADERS = {
    "Authorization": f"Discogs token={DISCOGS_TOKEN}",
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

def fetch_listing(listing_id):
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
    return response.json()


def evaluate_listing(listing):
    rejection_reasons = []

    seller = listing.get("seller", {})
    seller_stats = seller.get("stats", {})
    price = listing.get("price", {})

    seller_rating = float(seller_stats.get("rating") or 0)
    rating_count = int(seller_stats.get("total") or 0)
    price_value = float(price.get("value") or 0)

    if listing.get("status") != "For Sale":
        rejection_reasons.append("listing is not for sale")

    if listing.get("condition") not in ACCEPTED_CONDITIONS:
        rejection_reasons.append("media condition is below VG+")

    if listing.get("ships_from") != REQUIRED_COUNTRY:
        rejection_reasons.append(
            f"ships from {listing.get('ships_from', 'Unknown')}, not the UK"
        )

    if seller_rating < MINIMUM_SELLER_RATING:
        rejection_reasons.append(
            f"seller rating is below {MINIMUM_SELLER_RATING}%"
        )

    if rating_count < MINIMUM_RATING_COUNT:
        rejection_reasons.append(
            f"seller has fewer than {MINIMUM_RATING_COUNT} ratings"
        )

    if price_value <= 0:
        rejection_reasons.append("listing has no valid item price")

    return rejection_reasons

def calculate_plan_subtotal(plan):
    return sum(
        float(listing.get("price", {}).get("value") or 0)
        for listing in plan
    )


def count_plan_sellers(plan):
    return len(
        {
            listing.get("seller", {}).get(
                "username",
                "Unknown seller",
            )
            for listing in plan
        }
    )

def group_plan_by_seller(plan):
    seller_groups = {}

    for listing in plan:
        seller_name = listing.get("seller", {}).get(
            "username",
            "Unknown seller",
        )

        seller_groups.setdefault(seller_name, []).append(listing)

    return seller_groups

def main():
    print("RECORD HUNTER — PURCHASE OPTIMISER")
    print("Configuration loaded successfully.")

    if not CANDIDATE_FILE.exists():
        raise SystemExit(
            f"Candidate file was not found: {CANDIDATE_FILE}"
        )

    candidate_lines = [
        line.strip()
        for line in CANDIDATE_FILE.read_text().splitlines()
        if line.strip()
    ]
    
    listing_ids = []
    seen_ids = set()
    invalid_lines = []

    for line in candidate_lines:
        listing_id = extract_listing_id(line)

        if not listing_id:
            invalid_lines.append(line)
            continue

        if listing_id not in seen_ids:
            seen_ids.add(listing_id)
            listing_ids.append(listing_id)

    print(f"Candidate file: {CANDIDATE_FILE.name}")
    print(f"Candidate lines available: {len(candidate_lines)}")
    print("Discogs token: loaded securely")
    print(f"Unique listing IDs: {len(listing_ids)}")
    print(f"Invalid lines: {len(invalid_lines)}")

    if not listing_ids:
        raise SystemExit("No valid listing IDs were found.")
    
    listings = []
    request_failures = [] 

    print(f"\nRetrieving {len(listing_ids)} listings...")

    for position, listing_id in enumerate(listing_ids, start=1):
        try:
            listing = fetch_listing(listing_id)
        except requests.RequestException as error:
            request_failures.append(
                {
                    "listing_id": listing_id,
                    "error": str(error),
                }
            )
            print(
                f"FAIL {position}/{len(listing_ids)} "
                f"— Listing {listing_id}"
            )
            continue

        listings.append(listing)

        release = listing.get("release", {})
        description = release.get("description", "Unknown release")

        print(
            f"FETCHED {position}/{len(listing_ids)} "
            f"— {listing_id} — {description}"
        )

    print("\nRETRIEVAL SUMMARY")
    print(f"Listings requested: {len(listing_ids)}")
    print(f"Listings retrieved: {len(listings)}")
    print(f"Request failures: {len(request_failures)}")
    
    if request_failures:
        print("\nREQUEST FAILURE DETAILS")

        for failure in request_failures:
            print(
                f"Listing {failure['listing_id']}: "
                f"{failure['error']}"
            )

    eligible_listings = []
    rejected_listings = []

    for listing in listings:
        rejection_reasons = evaluate_listing(listing)

        if rejection_reasons:
            rejected_listings.append(
                {
                    "listing": listing,
                    "reasons": rejection_reasons,
                }
            )
        else:
            eligible_listings.append(listing)

    print("\nELIGIBILITY SUMMARY")
    print(f"Eligible listings: {len(eligible_listings)}")
    print(f"Rejected listings: {len(rejected_listings)}")
    print(f"Inaccessible listings: {len(request_failures)}")

    all_releases = {}
    eligible_by_release = {}

    for listing in listings:
        release = listing.get("release", {})
        release_id = release.get("id")

        if release_id:
            all_releases[release_id] = release.get(
                "description",
                "Unknown release",
            )

    for listing in eligible_listings:
        release = listing.get("release", {})
        release_id = release.get("id")

        if not release_id:
            continue

        eligible_by_release.setdefault(release_id, []).append(listing)

    print("\nELIGIBLE OPTIONS BY RELEASE")

    for release_id, description in all_releases.items():
        candidates = eligible_by_release.get(release_id, [])

        print(f"\n{description}")
        print(f"Release ID: {release_id}")
        print(f"Eligible options: {len(candidates)}")

        if not candidates:
            print("NO ELIGIBLE LISTING")
            continue

        for candidate in candidates:
            seller = candidate.get("seller", {})
            price = candidate.get("price", {})

            print(
                f"  Listing {candidate.get('id')} — "
                f"{seller.get('username', 'Unknown seller')} — "
                f"{price.get('currency', 'GBP')} "
                f"{float(price.get('value') or 0):.2f}"
            )

    cheapest_plan = []

    for release_id, candidates in eligible_by_release.items():
        cheapest_listing = min(
            candidates,
            key=lambda item: float(
                item.get("price", {}).get("value") or 0
            ),
        )

        cheapest_plan.append(cheapest_listing)

    cheapest_subtotal = sum(
        float(listing.get("price", {}).get("value") or 0)
        for listing in cheapest_plan
    )

    cheapest_sellers = {
        listing.get("seller", {}).get("username", "Unknown seller")
        for listing in cheapest_plan
    }

    print("\nCHEAPEST ITEM PLAN")

    for listing in cheapest_plan:
        release = listing.get("release", {})
        seller = listing.get("seller", {})
        price = listing.get("price", {})

        print(f"\n{release.get('description', 'Unknown release')}")
        print(f"  Listing: {listing.get('id')}")
        print(f"  Seller: {seller.get('username', 'Unknown seller')}")
        print(f"  Price: GBP {float(price.get('value') or 0):.2f}")

    print(f"\nItem subtotal: GBP {cheapest_subtotal:.2f}")
    print(f"Number of sellers: {len(cheapest_sellers)}")
    print("Shipping: confirm separately in the Discogs cart")

    candidate_groups = list(eligible_by_release.values())

    fewest_seller_plan = min(
        product(*candidate_groups),
        key=lambda plan: (
            count_plan_sellers(plan),
            calculate_plan_subtotal(plan),
        ),
    )

    consolidated_subtotal = calculate_plan_subtotal(
        fewest_seller_plan
    )
    consolidated_seller_count = count_plan_sellers(
        fewest_seller_plan
    )
    consolidation_premium = (
        consolidated_subtotal - cheapest_subtotal
    )

    print("\nFEWEST SELLER PLAN")

    for listing in fewest_seller_plan:
        release = listing.get("release", {})
        seller = listing.get("seller", {})
        price = listing.get("price", {})

        print(f"\n{release.get('description', 'Unknown release')}")
        print(f"  Listing: {listing.get('id')}")
        print(f"  Seller: {seller.get('username', 'Unknown seller')}")
        print(f"  Price: GBP {float(price.get('value') or 0):.2f}")

    print(f"\nItem subtotal: GBP {consolidated_subtotal:.2f}")
    print(f"Number of sellers: {consolidated_seller_count}")
    print(
        f"Premium over cheapest-item plan: "
        f"GBP {consolidation_premium:.2f}"
    )
    print("Shipping: confirm separately in the Discogs cart")

    seller_groups = group_plan_by_seller(fewest_seller_plan)

    print("\nPURCHASE REPORT GROUPED BY SELLER")

    for seller_name in sorted(seller_groups, key=str.lower):
        seller_listings = seller_groups[seller_name]
        seller_subtotal = calculate_plan_subtotal(seller_listings)

        print(f"\nSELLER: {seller_name}")
        print(f"Records: {len(seller_listings)}")

        for listing in seller_listings:
            release = listing.get("release", {})
            price = listing.get("price", {})
            listing_id = listing.get("id")

            print(
                f"  {release.get('description', 'Unknown release')}"
            )
            print(f"  Price: GBP {float(price.get('value') or 0):.2f}")
            print(
                f"  URL: https://www.discogs.com/shop/item/"
                f"{listing_id}"
            )

        print(f"Seller subtotal: GBP {seller_subtotal:.2f}")
        print("Shipping: confirm in the Discogs cart")

    print("\nPURCHASE REPORT TOTAL")
    print(f"Records covered: {len(fewest_seller_plan)}")
    print(f"Sellers required: {len(seller_groups)}")
    print(f"Item subtotal: GBP {consolidated_subtotal:.2f}")

if __name__ == "__main__":
    main()