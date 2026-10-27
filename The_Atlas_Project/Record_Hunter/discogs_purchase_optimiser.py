import os
import re
import json
from itertools import product
from pathlib import Path

import requests
from dotenv import load_dotenv
from datetime import datetime

PROJECT_DIRECTORY = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIRECTORY / ".env"
CANDIDATE_FILE = PROJECT_DIRECTORY / "candidate_links.txt"
REPORT_DIRECTORY = PROJECT_DIRECTORY / "reports"
SHIPPING_FILE = PROJECT_DIRECTORY / "shipping_costs.json"

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

def write_purchase_report(
    plan,
    cheapest_subtotal,
    unresolved_releases,
):
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now().astimezone()
    report_name = (
        "purchase_report_"
        f"{generated_at.strftime('%Y-%m-%d_%H-%M-%S')}.md"
    )
    report_path = REPORT_DIRECTORY / report_name

    seller_groups = group_plan_by_seller(plan)
    plan_subtotal = calculate_plan_subtotal(plan)
    plan_premium = plan_subtotal - cheapest_subtotal

    lines = [
        "# Record Hunter Purchase Report",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        "## Summary",
        "",
        f"- Records covered: {len(plan)}",
        f"- Sellers required: {len(seller_groups)}",
        f"- Item subtotal: GBP {plan_subtotal:.2f}",
        f"- Premium over cheapest-item plan: GBP {plan_premium:.2f}",
        "- Shipping must be confirmed in the Discogs cart.",
        "",
        "## Selected Listings by Seller",
        "",
    ]

    for seller_name in sorted(seller_groups, key=str.lower):
        seller_listings = seller_groups[seller_name]
        seller_subtotal = calculate_plan_subtotal(seller_listings)

        lines.extend(
            [
                f"### {seller_name}",
                "",
                f"Seller subtotal: **GBP {seller_subtotal:.2f}**",
                "",
            ]
        )

        for listing in seller_listings:
            release = listing.get("release", {})
            price = float(
                listing.get("price", {}).get("value") or 0
            )
            listing_id = listing.get("id")
            description = release.get(
                "description",
                "Unknown release",
            )
            url = (
                "https://www.discogs.com/shop/item/"
                f"{listing_id}"
            )

            lines.append(
                f"- [{description}]({url}) — GBP {price:.2f}"
            )

        lines.extend(
            [
                "",
                "Shipping: confirm in the Discogs cart.",
                "",
            ]
        )

    lines.extend(
        [
            "## Unresolved Releases",
            "",
        ]
    )

    if unresolved_releases:
        for description in unresolved_releases:
            lines.append(f"- {description}")
    else:
        lines.append("- None")

    lines.append("")

    report_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return report_path

def load_shipping_costs():
    if not SHIPPING_FILE.exists():
        raise SystemExit(
            f"Shipping-cost file was not found: {SHIPPING_FILE}"
        )

    try:
        shipping_costs = json.loads(
            SHIPPING_FILE.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"Invalid JSON in {SHIPPING_FILE.name}: {error}"
        )

    if not isinstance(shipping_costs, dict):
        raise SystemExit(
            "Shipping-cost data must be a JSON object."
        )

    return shipping_costs


def get_shipping_cost(
    shipping_costs,
    seller_name,
    record_count,
):
    seller_rates = shipping_costs.get(seller_name, {})
    shipping_value = seller_rates.get(str(record_count))

    if shipping_value is None:
        return None

    try:
        shipping_cost = float(shipping_value)
    except (TypeError, ValueError):
        return None

    if shipping_cost < 0:
        return None

    return shipping_cost

def get_api_shipping_price(listing):
    shipping_price = listing.get("shipping_price")

    if not isinstance(shipping_price, dict):
        return None

    currency = shipping_price.get("currency")
    value = shipping_price.get("value")

    if currency != "GBP" or value is None:
        return None

    try:
        shipping_value = float(value)
    except (TypeError, ValueError):
        return None

    if shipping_value < 0:
        return None

    return shipping_value

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

    unresolved_releases = [
        description
        for release_id, description in all_releases.items()
        if not eligible_by_release.get(release_id)
    ]

    report_path = write_purchase_report(
        fewest_seller_plan,
        cheapest_subtotal,
        unresolved_releases,
    )

    print("\nAPI SHIPPING PRICE CHECK")

    api_shipping_available = 0
    api_shipping_unavailable = 0

    for listing in eligible_listings:
        seller_name = listing.get("seller", {}).get(
            "username",
            "Unknown seller",
        )
        listing_id = listing.get("id")
        api_shipping_price = get_api_shipping_price(listing)

        if api_shipping_price is None:
            api_shipping_unavailable += 1
            print(
                f"UNAVAILABLE — Listing {listing_id} — "
                f"{seller_name}"
            )
        else:
            api_shipping_available += 1
            print(
                f"AVAILABLE — Listing {listing_id} — "
                f"{seller_name} — GBP {api_shipping_price:.2f}"
            )

    print("\nAPI SHIPPING SUMMARY")
    print(f"Available: {api_shipping_available}")
    print(f"Unavailable: {api_shipping_unavailable}")

    shipping_costs = load_shipping_costs()
    shipping_requirements = set()

    for plan in (cheapest_plan, fewest_seller_plan):
        plan_groups = group_plan_by_seller(plan)

        for seller_name, seller_listings in plan_groups.items():
            shipping_requirements.add(
                (seller_name, len(seller_listings))
            )

    print("\nSHIPPING COST REQUIREMENTS")

    missing_shipping_costs = []

    for seller_name, record_count in sorted(
        shipping_requirements,
        key=lambda requirement: requirement[0].lower(),
    ):
        shipping_cost = get_shipping_cost(
            shipping_costs,
            seller_name,
            record_count,
        )

        if shipping_cost is None:
            missing_shipping_costs.append(
                (seller_name, record_count)
            )
            print(
                f"MISSING — {seller_name} — "
                f"{record_count} record(s)"
            )
        else:
            print(
                f"LOADED — {seller_name} — "
                f"{record_count} record(s) — "
                f"GBP {shipping_cost:.2f}"
            )

    print(
        f"Missing shipping prices: "
        f"{len(missing_shipping_costs)}"
    )

    print(f"\nMarkdown report saved to: {report_path}")

if __name__ == "__main__":
    main()