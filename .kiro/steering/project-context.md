# Amazon India Seller Handbook 2026 — project context

## What this repo is

A print-quality PDF handbook for Amazon India sellers, built from hand-written HTML
parts, plus the research pipeline that extracts Amazon's live fee data to back it up.

All fee data was captured from `sell.amazon.in/fees-and-pricing` on **4 August 2026**.
Amazon changes these numbers without notice — always re-verify against the live page
before republishing, and update the capture date in the source notes.

## Layout

```
handbook/            The deliverable
  build.py           Assembles part1-7 -> handbook_full.html -> PDF (weasyprint)
  part1..part7.html  The chapters, hand-written
  style.css          Print stylesheet, linked RELATIVELY by part1 + handbook_full
  handbook_full.html Generated - do not edit by hand
  Amazon_India_Seller_Handbook_2026.pdf   Generated

research/            Fee-data pipeline
  fees.html          Saved copy of Amazon's live fees page (the source of truth)
  step.html          Saved copy of another Amazon seller page
  product.html       Saved product page
  extract_fees.py    fees.html   -> referral_fees_live.json   (219 categories)
  extract_groups.py  fees.html   -> closing_groups_live.json  (closing-fee groups)
  build_appendixA.py referral_fees_live.json  -> appendixA_body.html
  build_appendixB.py closing_groups_live.json -> appendixB_body.html
  parse_product.py   product.html -> prints product attributes to stdout
  ratecards/         Amazon's own rate-card screenshots (JPG)
```

## Critical: how to run the scripts

Every script in `research/` reads its inputs with bare relative paths
(`pathlib.Path("fees.html")`), which resolve against the **current working
directory**, not the script location. You must `cd` into the folder first:

```bash
cd research && python3 extract_fees.py     # correct
python3 research/extract_fees.py           # WRONG - crashes, file not found
```

`handbook/build.py` is the exception - it resolves paths via `__file__`, so it works
from anywhere, but the parts and `style.css` must stay in the same folder as it.

Outputs are deterministic: re-running the four data scripts reproduces the committed
JSON and appendix HTML byte-for-byte. Use that as a regression check after any edit.

## Known open issues

1. **`extract_groups.py` finds 0 categories for Group ##, Group C and Group D.**
   Only Group # (153), Group A (58) and Group B (20) populate. These three empty
   groups are the ₹301-500 price band. Appendix B currently presents the ₹301-500
   rates (₹22 / ₹18 / ₹14) as if their category membership mirrors the ₹0-300 groups,
   but that mirroring was never actually extracted or verified - while the output is
   still labelled `VERIFIED`. Either extract the real ₹301-500 membership from
   `fees.html`, or downgrade that label and state the assumption in the text.

2. **`parse_product.py` extracts nothing** from the current `product.html` - title,
   price, byline, seller and all details return `-- not found --`. The saved page is
   likely a bot-block/interstitial rather than a real product page, or Amazon's markup
   changed. Re-save the product page before relying on this script.

## Conventions

- The rate-card JPGs are cited in prose only (`<em>FC_Closing_fee2026.jpg</em>`), never
  as `<img src>`. Renaming them will not break rendering, but it will orphan citations.
- Generated files (`handbook_full.html`, the PDF, the JSONs, appendix bodies) are
  committed deliberately so the handbook is reproducible without re-scraping. Edit the
  generator, never the generated file.
- Currency is INR throughout, written as `₹`. Keep the `·` separator style in fee
  tables for consistency with existing parts.
