# Amazon India Seller Handbook 2026

A print-quality PDF guide to selling on Amazon India, with every fee figure traced back
to Amazon's own live fee page and rate-card images.

Fee data captured from [sell.amazon.in/fees-and-pricing](https://sell.amazon.in/fees-and-pricing)
on **4 August 2026**. Amazon revises these figures without notice — re-verify before republishing.

## Repository layout

| Path | What it holds |
| --- | --- |
| `handbook/` | The deliverable: 8 hand-written HTML chapters (part1–part8), print stylesheet, and `build.py` which assembles them into the PDF |
| `research/` | The fee-data pipeline: saved Amazon pages, extraction scripts, and the JSON they produce |
| `research/ratecards/` | Amazon's own rate-card screenshots, cited as sources in the handbook |
| `research/fc/` | FC Capabilities PDF (10 pages) — source for all FC codes and weight/height thresholds |
| `.kiro/steering/` | Project context loaded automatically by Kiro |

## Building the PDF

Requires [WeasyPrint](https://weasyprint.org/).

```bash
cd handbook
python3 build.py
```

This concatenates `part1.html` … `part8.html` into `handbook_full.html`, asserts the
result has exactly one `<html>` element, then renders `Amazon_India_Seller_Handbook_2026.pdf`.

**Part 8** (added August 2026) covers operational chapters 26–32: Seller Central Dashboard,
Revenue Checking, Fee Reconciliation, Reports, Advertising Management, Account Rules &
Compliance, and Growth Strategies.

## Regenerating the fee data

Each script reads its input from the **current working directory**, so `cd` in first:

```bash
cd research
python3 extract_fees.py      # fees.html -> referral_fees_live.json  (219 categories)
python3 extract_groups.py    # fees.html -> closing_groups_live.json (6 group lists)
python3 build_appendixA.py   # referral_fees_live.json  -> appendixA_body.html
python3 build_appendixB.py   # closing_groups_live.json -> appendixB_body.html
```

`extract_groups.py` self-validates and exits non-zero if any group list is empty, if
Amazon's own worked examples fail to reproduce, or if a category appears in two groups
of the same price band.

Running `python3 research/extract_fees.py` from the repo root will fail — the paths are
relative to the working directory, not the script.

These four scripts are deterministic: re-running them reproduces the committed JSON and
appendix HTML byte-for-byte, which makes them a useful regression check.

## Closing fees: six lists, not three tiers

Amazon publishes six independent category lists — three per price band — and **the
bands do not mirror each other**:

| Price band | | | |
| --- | --- | --- | --- |
| ₹0–300 | Group # — ₹26 (153) | Group A — ₹20 (59) | Group B — ₹13 (20) |
| ₹301–500 | Group ## — ₹22 (146) | Group C — ₹18 (55) | Group D — ₹14 (32) |

Never pair Group A with C, or B with D. Amazon's own example on the fee page settles
it: *Apparel - Shorts* is Group A below ₹300 but **Group D** at ₹450 — ₹14, not the ₹18
an A→C pairing implies. 16 categories break any simple pairing; Appendix B tabulates
them.

Above ₹1,000 all categories pay ₹52 except four, which pay ₹72: Chimneys,
Refrigerators, Major Appliances – Other Products, Home Entertainment – Other products.

## What is verified, and what is not

Reproducible from `fees.html` by re-running the scripts: all six closing-fee lists, the
₹72 exception list, all 219 referral rates, pick & pack ₹17, storage ₹50/cu ft, and the
500 g minimum chargeable weight.

**Read by eye from the rate-card JPGs and not machine-verifiable:** the ₹27 (₹501–1,000)
and ₹52 (above ₹1,000) closing fees, the ₹101 Self-Ship rate, and all weight-handling
figures (₹39 / ₹65 / ₹54 / ₹85). These strings do not appear in the saved page text, so
no script can confirm them — re-check against `research/ratecards/*.jpg` before
republishing.

## Known issues

- `product.html` is **not a product page** — it holds Amazon's "Continue shopping"
  anti-automation interstitial (3,793 bytes, zero product markup). Re-save it from a
  browser session already signed in to Amazon.in, as *Webpage, HTML Only*.
  `python3 parse_product.py --selftest` confirms the extraction patterns still work
  independently of that bad input.

## Resolved issues (August 2026)

- **Chapter 3's advertising figures** — now based on **actual** July Seller Central
  transaction export (₹15,554 total ad spend, not a 7-day projection). The loss figure
  (₹103.15/unit) is computed from real settlement data.
- **Try FBA Promotion terms** — confirmed by Amazon Support (case 13137163892):
  progressive, no clawback, ends 11 Aug 2026, covers pick/pack + weight handling +
  closing only (not referral).
- **FBA reimbursement window** — confirmed at 60 days for inbound/warehouse claims,
  45–105 days for customer returns (Jan 2025 Seller Central update).
- **EPR plastic (Ch 17.5)** — Rule 4A (2024 amendment) confirmed to have *created* the
  micro/small exemption, not undermined it.
- **SAFE-T 30-day window** — downgraded from VERIFIED to UNCONFIRMED FOR INDIA; all
  sources describe US seller-fulfilled orders only.

See `.kiro/steering/project-context.md` for detail.
