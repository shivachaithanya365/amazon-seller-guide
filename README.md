# Amazon India Seller Handbook 2026

A print-quality PDF guide to selling on Amazon India, with every fee figure traced back
to Amazon's own live fee page and rate-card images.

Fee data captured from [sell.amazon.in/fees-and-pricing](https://sell.amazon.in/fees-and-pricing)
on **4 August 2026**. Amazon revises these figures without notice — re-verify before republishing.

## Repository layout

| Path | What it holds |
| --- | --- |
| `handbook/` | The deliverable: 7 hand-written HTML chapters, print stylesheet, and `build.py` which assembles them into the PDF |
| `research/` | The fee-data pipeline: saved Amazon pages, extraction scripts, and the JSON they produce |
| `research/ratecards/` | Amazon's own rate-card screenshots, cited as sources in the handbook |
| `.kiro/steering/` | Project context loaded automatically by Kiro |

## Building the PDF

Requires [WeasyPrint](https://weasyprint.org/).

```bash
cd handbook
python3 build.py
```

This concatenates `part1.html` … `part7.html` into `handbook_full.html`, asserts the
result has exactly one `<html>` element, then renders `Amazon_India_Seller_Handbook_2026.pdf`.

## Regenerating the fee data

Each script reads its input from the **current working directory**, so `cd` in first:

```bash
cd research
python3 extract_fees.py      # fees.html -> referral_fees_live.json  (219 categories)
python3 extract_groups.py    # fees.html -> closing_groups_live.json
python3 build_appendixA.py   # referral_fees_live.json  -> appendixA_body.html
python3 build_appendixB.py   # closing_groups_live.json -> appendixB_body.html
```

Running `python3 research/extract_fees.py` from the repo root will fail — the paths are
relative to the working directory, not the script.

These four scripts are deterministic: re-running them reproduces the committed JSON and
appendix HTML byte-for-byte, which makes them a useful regression check.

## Known issues

- `extract_groups.py` returns 0 categories for Group ##, C and D (the ₹301–500 band).
  Appendix B presents those rates as though membership mirrors the ₹0–300 groups, but
  that mirroring is unverified while still labelled `VERIFIED`.
- `parse_product.py` currently extracts nothing from `product.html` — the saved page
  appears to be a bot-block page rather than a product listing.

See `.kiro/steering/project-context.md` for detail.
