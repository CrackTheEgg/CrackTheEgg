import os

import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv("DISCOGS_TOKEN")
release_id = 67239

headers = {
    "Authorization": f"Discogs token={token}",
    "User-Agent": "DiscogsAgentTest/0.1",
}

try:
    response = requests.get(
        f"https://api.discogs.com/marketplace/stats/{release_id}",
        headers=headers,
        params={"curr_abbr": "GBP"},
        timeout=10,
    )
    response.raise_for_status()

except requests.RequestException as error:
    raise SystemExit(f"Marketplace request failed: {error}")

statistics = response.json()
lowest_price = statistics.get("lowest_price")
number_for_sale = statistics.get("num_for_sale", 0)

print("\nNoise Factory - Generation X")
print(f"Copies for sale: {number_for_sale}")

if lowest_price:
    print(
        f"Lowest advertised price: "
        f"{lowest_price['currency']} {lowest_price['value']:.2f}"
    )
else:
    print("No copies are currently listed for sale.")
