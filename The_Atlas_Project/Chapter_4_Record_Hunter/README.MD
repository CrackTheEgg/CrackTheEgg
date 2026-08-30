# Record Hunter

**Chapter 4 of The Atlas Project**

Record Hunter is a Python-based Discogs assistant designed to help record collectors identify missing releases from a set list, assess marketplace availability, validate listings against purchasing rules, and recommend efficient seller combinations.

## Project status

**Alpha prototype — active development**

## Architecture

The current, target and future AWS architectures are documented in  
[docs/architecture.md](docs/architecture.md).

The core Discogs integration and listing-validation functions are working. The next development stage is the purchasing optimiser.

## The problem

Completing a DJ set or curated record list manually can involve:

1. Comparing every release against a Discogs collection.
2. Checking whether missing releases are already in the wantlist.
3. Searching through multiple marketplace listings.
4. Rejecting unsuitable media conditions or sellers.
5. Comparing individual prices against combined purchases from fewer sellers.
6. Accounting for shipping costs and seller reputation.

Record Hunter is intended to automate as much of this process as the supported Discogs API allows.

## Current capabilities

The working prototype can:

* Authenticate securely with the Discogs API.
* Retrieve private Discogs lists.
* Retrieve every release from a selected list.
* Compare list releases against a user’s collection using exact Release IDs.
* Separate owned and missing releases.
* Compare missing releases against the user’s wantlist.
* Add releases to the wantlist after explicit confirmation.
* Retrieve marketplace availability statistics.
* Inspect individual marketplace listings.
* Process candidate listing URLs in bulk from a text file.
* Remove duplicated listing IDs from a test batch.
* Validate listings against defined purchasing rules.
* Group eligible listings by seller.
* Calculate seller-level item subtotals.
* Report rejected listings with specific reasons.

## Current purchasing rules

A marketplace listing is currently eligible when:

| Rule                | Requirement         |
| ------------------- | ------------------- |
| Media condition     | VG+ or better       |
| Seller location     | United Kingdom      |
| Seller rating       | At least 99%        |
| Seller rating count | At least 50         |
| Listing status      | For Sale            |
| Currency            | GBP where supported |

Sleeve condition is reported but is not currently used as a rejection rule.

## Installation

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

Create a local `.env` file:

```text
DISCOGS_TOKEN=your_discogs_personal_access_token
```

The `.env` file is excluded from Git and must never be committed.

## Basic connection test

Run:

```bash
python discogs_test.py
```

A successful connection displays the authenticated Discogs username.

## Batch candidate testing

Add individual Discogs marketplace listing URLs to:

```text
candidate_links.txt
```

Use one URL per line:

```text
https://www.discogs.com/shop/item/1234567890
```

Run the batch validator:

```bash
python discogs_batch_candidates.py < candidate_links.txt
```

To retain the output locally:

```bash
python discogs_batch_candidates.py < candidate_links.txt | tee seller_test_results.txt
```

Generated results files are excluded from Git.

## Prototype workflow

1. Select a private Discogs list.
2. Retrieve the releases in that list.
3. Exclude exact Release IDs already present in the collection.
4. Check the remaining releases against the wantlist.
5. Add approved missing releases to the wantlist.
6. Collect candidate marketplace listing URLs.
7. Validate every candidate against the purchasing rules.
8. Group eligible candidates by seller.
9. Compare purchasing combinations.
10. Hand the selected listings back to Discogs for cart and payment confirmation.

## Known limitations

* The public Discogs API does not provide a supported general buyer-side marketplace search endpoint equivalent to the website filters.
* Candidate marketplace listing URLs are currently supplied manually.
* Shipping prices are not reliably returned through the listing API.
* Shipping must therefore be confirmed in the Discogs cart.
* The prototype cannot currently add listings directly to a buyer’s cart.
* Discogs API rate limits can temporarily return HTTP `429` responses.
* Listings can be sold or changed between analysis and purchase.
* Collection comparisons currently use exact Discogs Release IDs.

Record Hunter does not scrape Discogs webpages or bypass supported Discogs functionality.

## Development roadmap

### Phase 1 — Core Discogs integration

* Authentication
* Private-list retrieval
* Collection comparison
* Wantlist comparison and controlled updates
* Marketplace statistics
* Listing validation
* Batch candidate processing
* Seller grouping

**Status: working prototype**

### Phase 2 — Purchasing optimiser

* Select no more than one listing per release.
* Identify releases with no eligible candidates.
* Compare lowest individual item prices.
* Minimise the number of sellers.
* Calculate seller-level item subtotals.
* Show where shipping costs could change the recommendation.
* Produce a recommended purchasing plan.

**Status: next development stage**

### Phase 3 — Application refactoring

* Replace duplicated prototype code with reusable Python modules.
* Remove hard-coded List IDs.
* Introduce selectable lists and configuration.
* Add structured error and rate-limit handling.
* Add automated tests and reusable test fixtures.
* Export results in a structured format.

### Phase 4 — Web application

* Python backend API.
* Responsive HTML, CSS and JavaScript interface.
* iPhone-friendly Progressive Web App.
* User-controlled purchasing rules.
* Search and optimisation results presented through the interface.

### Phase 5 — AWS architecture

Potential AWS services include:

* Amazon Cognito for user authentication.
* AWS Lambda or container-based backend services.
* Amazon API Gateway.
* Amazon DynamoDB.
* AWS Secrets Manager and AWS KMS.
* Amazon S3 and Amazon CloudFront.
* Amazon CloudWatch.

Discogs access tokens will remain encrypted and accessible only to authorised backend services.

### Phase 6 — Discogs-supported purchasing hand-off

Subject to supported Discogs functionality or future permission:

* Prepare selected listings for purchase.
* Redirect the user to the Discogs cart.
* Allow the user to confirm shipping and payment through Discogs.
* Retain explicit user approval before any purchase.

## Security principles

* Discogs tokens are never stored in source code.
* `.env` and `.venv/` are excluded from Git.
* Destructive account changes require explicit confirmation.
* Wantlist updates are verified after submission.
* Future multi-user tokens will be encrypted and isolated by user.
* Payment will remain within the supported Discogs and payment-provider flow.

## Portfolio objectives

Record Hunter demonstrates:

* Python application development.
* REST API integration.
* Authentication and secrets management.
* Data retrieval and pagination.
* Input validation and filtering.
* Marketplace data processing.
* Cost-optimisation logic.
* Secure cloud architecture planning.
* Incremental development and controlled testing.

## Disclaimer

Record Hunter is an independent portfolio project and is not affiliated with or endorsed by Discogs. Marketplace data remains subject to Discogs availability, terms and supported API functionality.
