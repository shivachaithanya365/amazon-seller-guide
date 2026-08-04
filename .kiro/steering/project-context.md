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

## Closing fees: six lists, not three tiers

This is the single most important fact about the fee data, and it was previously
modelled wrongly.

Amazon publishes **six independent category lists**, three per price band:

```
INR 0-300    Group #  Rs 26 (153)   Group A  Rs 20 (59)   Group B  Rs 13 (20)
INR 301-500  Group ## Rs 22 (146)   Group C  Rs 18 (55)   Group D  Rs 14 (32)
```

The bands do **not** mirror each other. Do not pair Group A with C, or B with D.
Amazon's own worked example on the page settles it: *Apparel - Shorts* is Group A
below Rs 300 but Group D at Rs 450, so Rs 14 - not the Rs 18 an A->C pairing implies.

**16 categories** are placed in a pairing no simple tier model predicts (11 move
Group # -> D, 4 move A -> D, 1 moves B -> ##). They are tabulated at the end of
Appendix B. A further 18 have no exact string match in the Rs 301-500 band, but that
is mostly Amazon's own inconsistent naming (`Fragrance` vs `Beauty - Fragrance`,
`Jewellery` vs `Jewelry`), not proof of absence - treat those as unknown, not missing.

Above Rs 1,000 every category pays Rs 52 except exactly four, which pay Rs 72:
Chimneys, Refrigerators, Major Appliances - Other Products, Home Entertainment -
Other products. Amazon only ever calls these "select fee categories".

`extract_groups.py` self-validates: it exits non-zero if any group is empty, if
Amazon's worked examples do not reproduce, or if a category appears twice in one
band. If you re-save `fees.html`, run it and trust the exit code.

Two parsing traps that previously broke it, in case the markup shifts again:
`(Group #)` sits alone on a line, but Group C and D put the marker at the **end** of
their description line, and Group ## has **no marker at all** and must be identified
by its rate. A `len(l) < 160` guard also silently dropped a legitimate 170-character
Automotive category; the cap is now 200.

## What is verified, and what cannot be

Verified reproducibly from `fees.html` (re-running the scripts proves it):
all six closing-fee group lists, the Rs 72 exception list, all 219 referral-fee
rates, pick & pack Rs 17, storage Rs 50/cu ft, the 500 g minimum chargeable weight.

**Not machine-verifiable** - these figures exist only inside the rate-card JPGs and
were read by eye: the Rs 27 (Rs 501-1,000) and Rs 52 (above Rs 1,000) closing fees,
the Rs 101 Self-Ship rate, and every weight-handling number (Rs 39 / 65 / 54 / 85).
Searching the saved page text for "501", "Rs 27" or "Rs 52" returns nothing. They may
well be right, but no script can confirm them - re-check by eye against
`research/ratecards/*.jpg` before republishing, and do not assume a passing script
run has validated them.

## Known open issues

1. **`product.html` is not a product page.** Diagnosed: it is 3,793 bytes containing
   only Amazon's "Continue shopping" anti-automation interstitial - six lines of
   visible text, and zero occurrences of `productTitle`, `a-price-whole`,
   `bylineInfo`, `landingImage` or `merchant-info`. `parse_product.py` was never the
   problem; it had nothing to parse.

   The script now classifies its input first and exits non-zero with a specific
   diagnosis (bot wall / CAPTCHA / 404 / sign-in / no markers / stale markup) instead
   of printing fifteen `-- not found --` lines and exiting 0. Run
   `python3 parse_product.py --selftest` to confirm the extraction patterns still fire
   against a known-good synthetic sample - that separates "bad input" from "Amazon
   changed their markup", which the old script conflated.

   To fix the data: open the listing in a browser already signed in to Amazon.in,
   click through any "Continue shopping" prompt, confirm title/price/"Sold by" are
   visible, then save as **Webpage, HTML Only**. Fetching the URL with curl or from a
   fresh incognito window hits the wall again. The parser's happy path is verified
   only against the synthetic sample - it has never seen a real saved page.

2. **Chapter 3's ad-spend figures rest on a projection, not measurement.** The
   Rs 1,858 last-7-days Sponsored Ads spend is stated as fact but the underlying
   Seller Central export is not in this repo, so nothing here can verify it. The
   Rs 248.84 per-unit ad cost mixes windows: it projects that 7-day figure to 30 days
   (Rs 7,963) and divides by *July's* 32 units. That is only valid if spend ran flat
   through July. The headline "Rs 39.94 loss per unit" depends entirely on it. All the
   arithmetic reconciles exactly - the assumption, not the maths, is the weak point.
   Commit the transaction CSVs and recompute from actual July spend.

3. **Chapter 9's profit box excludes advertising.** It shows Rs 95 net and ~29% margin
   at Rs 120 COGS, while Chapter 3 says ads make the same unit a loss. Both are
   arithmetically right; they just answer different questions. Worth an explicit
   cross-reference so the two chapters are not read as contradicting each other.

## Conventions

- The rate-card JPGs are cited in prose only (`<em>FC_Closing_fee2026.jpg</em>`), never
  as `<img src>`. Renaming them will not break rendering, but it will orphan citations.
- Generated files (`handbook_full.html`, the PDF, the JSONs, appendix bodies) are
  committed deliberately so the handbook is reproducible without re-scraping. Edit the
  generator, never the generated file.
- Currency is INR throughout, written as `₹`. Keep the `·` separator style in fee
  tables for consistency with existing parts.
