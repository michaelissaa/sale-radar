# Sale Radar

A personal dashboard for Black Friday and clothing sales at gymwear, sportswear and fashion brands. It shows
Australian (AUD, Sydney time) sale status, returns and shipping. It refreshes itself every 6 hours on GitHub
Actions and is hosted free on GitHub Pages. No server and no paid APIs, and your PC can stay off.

## How it works

```
config/brands.json      the brands you track (edit this to add/remove/prioritise)
data/research.json      facts checked by hand: returns, shipping, confirmed sale details, with sources
scanner/scan.py         Python, stdlib only. Fetches each brand's public pages, detects sale wording,
                        merges with research.json, diffs against the previous run
data/dashboard.json     output the website reads (rewritten every scan)
data/changes.json       de-duplicated change log
data/state.json         scanner memory: HTTP cache headers, last success, policy page fingerprints
web/                    React + Vite dashboard (reads data/*.json)
.github/workflows/scan.yml  every 6h: test, scan, commit data, build, deploy to Pages
```

### Sale status rules

| Status | Meaning |
|---|---|
| LIVE | Verified active sale, or sale wording plus a discount detected on the retailer page (labelled *auto-detected*) |
| UPCOMING | Retailer has announced a coming sale ("coming soon", "sign up for early access") |
| EARLY ACCESS | Member or VIP access running now |
| NOT ANNOUNCED | Retailer page was read and has no Black Friday sale wording |
| ENDED | Previously active, confirmed end date passed or wording gone |
| NEEDS CHECKING | Site unreachable/blocked with no prior data, or wording is ambiguous |

Each active or announced sale also has a **sale type**: *Black Friday* (Black Friday / Cyber Monday branded)
or *Regular sale* (a normal promotion). The dashboard has filters for each.

**Store price check:** for Shopify stores (most gymwear brands) the scanner reads the public `/products.json`
once a day and counts products priced below their "compare at" price. This is the store's own price data, so:
a "sale live" banner with under 10% of products discounted becomes NEEDS CHECKING with an explanation;
a "sitewide" claim with under half the products discounted is downgraded to "selected items"; and a store
with at least 40% of products marked down but no Black Friday wording shows as a *Regular sale*.

Dates are only shown when the retailer published them (`dates_confirmed: true` in research.json).
The scanner never derives dates. Past-year patterns go in `expected_note` and display as "Not confirmed".
"Up to 50% off" and "50% off" are stored separately (`discount_kind: up_to | flat`).

**Free returns** = a change-of-mind return costs nothing by at least one method (often in store).
**Free return postage** = the retailer pays for a mailed return. These are tracked as separate fields.
Both are voluntary store policy, separate from Australian Consumer Law rights for faulty goods.

### Failures and staleness

* A blocked or failing site never stops the run. It is logged as a GitHub Actions warning, recorded in the
  brand's `scan.errors`, and shown in the dashboard.
* The last good values are kept and marked **stale** when a brand has had no successful scan for 18 hours.
* The whole page shows a warning banner if no scan has published for 12 hours.
* Policy pages are fetched at most once a day. If their text changes after they were verified, the detail view
  says to re-check.
* The scanner identifies itself honestly (`SaleRadarBot`), obeys robots.txt, waits between requests to the same
  site, uses conditional requests, and never retries a block. It does not bypass CAPTCHAs or bot protection.
  Sites that block it (Nike/Adidas-style bot walls) rely on the hand-checked data in research.json.

## Add, remove or prioritise a brand

Edit `config/brands.json` (in GitHub's web editor is fine):

```json
{"id": "represent", "name": "Represent", "category": "fashion", "priority": 2, "enabled": true,
 "storefront": "UK brand, ships to AU",
 "urls": {"home": "https://representclo.com/", "sale": [], "returns": "https://...", "shipping": "https://..."}}
```

* `priority` 1 sorts first. `enabled: false` hides a brand without deleting its history.
* `sale` can be empty. The scanner finds Black Friday / Cyber / Early Access links on the home page itself.
* Optional: add hand-checked returns/shipping to `data/research.json` under the same `id` (copy an existing entry).
  Values must be `YES | NO | CONDITIONAL | UNKNOWN`, with `source_url` and `evidence`. `python -m unittest discover -s scanner` checks this.

Committing to `main` rebuilds the site. The next scheduled scan picks up the brand.

## Email alerts

People sign up on the dashboard (**Email alerts** button, or **Alert me** on a brand) with their email, the
brands they care about and the alert types: Black Friday news (announced, dates confirmed, live), regular
sales starting or ending, and discount changes. After each scan, `scanner/notify.py` turns that run's changes
into alerts and posts them to a Google Apps Script backend, which emails matching subscribers.
Setup and privacy details: [notify/README.md](notify/README.md). Until it's connected, the sign-up form says
alerts aren't switched on, and the scan log lists the alerts it *would* have sent.

## Run a scan manually

* GitHub: **Actions → Scan retailers and deploy dashboard → Run workflow** (optionally list brand ids).
* Locally: `python scanner/scan.py` (or `--only gymshark,lskd`), then `cd web && npm run dev`.

The dashboard's **Reload data** button fetches the latest published JSON. It does not start a scan.

## Tests

```
python -m unittest discover -s scanner -v   # extraction, Sydney date logic, failures, staleness, de-dup, data quality
cd web && npm test                           # Sydney timezone, countdown, filters, sorting, favourites ordering
```

## Privacy

GitHub Pages on a free account requires a **public** repository, so the code, the brand list and the scraped
sale data are public. There are no secrets, credentials or personal data in the repo. Favourites stay in your
browser (localStorage) and are never uploaded. The page sets `noindex` so search engines are asked not to list it,
but anyone with the URL can open it.
