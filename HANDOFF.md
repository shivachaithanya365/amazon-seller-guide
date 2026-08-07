# Handoff — read this first

This file exists so the project survives losing the chat history. If you are a new
session, or the seller has come back after a gap, everything you need to resume is here.

Last full verification pass: **7 August 2026**.

## What this project is

A print-quality PDF handbook for **one specific Amazon India seller** — BSNY Enterprises,
Telangana — selling one product, plus the research pipeline that backs every fee figure
with a source. It is not a generic guide; the numbers are that seller's real numbers.

- Deliverable: `handbook/Amazon_India_Seller_Handbook_2026.pdf` (125 pages)
- Built from `handbook/part1.html` … `part8.html` by `handbook/build.py`
- Chapters 1–25 + Appendices A–I, then Chapters 26–32 (operations, added Aug 2026)

## First three commands

```bash
pip install weasyprint pypdf
cd handbook  && python3 build.py
cd ../research && python3 audit_handbook.py     # must print AUDIT PASSED
```

`pypdf` is mandatory. Without it the audit's glyph check skips silently, and that check
is the only thing that catches characters WeasyPrint drops from the PDF without warning.

## The seller's situation, in six lines

| | |
| --- | --- |
| Product | Rope wire clothesline, 22 m, black. SKU `BSNY-WIRE-22M`, ASIN `B0H4WZ8FBR` |
| Price | ₹333 (GST-inclusive, 18%, HSN 72179099) — real revenue is ₹282.20 |
| Channel | FBA only, Standard STEP level, stock at HYD3 and HYD8 (Telangana, Region 3) |
| Fees | ₹120/unit standard (₹85 weight handling + ₹17 pick & pack + ₹18 per-item), ₹0 referral |
| Stock | 140 units, all in the 0–90 day age band as of 7 Aug 2026 |
| The problem | Advertising. ₹15,554 in July against ₹11,988 net revenue, ₹0 attributed ad sales |

**The single most important fact:** the product is profitable and ranks well
(#10 of 663 in its category). The advertising is what makes it lose money. Chapter 3 is
the emergency-brake chapter and everything in it is verified from the seller's own
transaction export in `research/account/transactions_60d.csv`.

## Two numbers still missing, and why they matter

Everything else in the book is settled. These two are not, and they decide whether the
business is viable once the fee promotion ends:

1. **Supplier cost per unit** — the *taxable value* on the purchase invoice divided by
   units received. Not the invoice total.
2. **Packaging cost per unit** — bulk packaging spend divided by units packed.

Feed both into `research/account/unit_economics.py`. Until then it prints a sensitivity
table instead of an answer. At 18% GST the break-even supplier cost is roughly **₹132** —
above that, the unit loses money even with zero advertising.

**Do not invent these numbers.** Ask the seller.

## The fee cliff — check whether it has passed

The Try FBA Promotion zeroed all selling fees. Seller Support confirmed in writing
(case 13137163892) that it ran **60 days from 12 June 2026, ending 11 August 2026**,
applied progressively, and that **nothing already exempted is ever clawed back**.

- **Before 11 Aug 2026:** fees ₹0, net ₹333/unit
- **After 11 Aug 2026:** fees ₹120, net ₹213/unit — advertising ceiling drops from ~44% to ~9% ACOS

If you are reading this after 11 August, treat every "today" figure in Chapter 3 as
historical and confirm the current position in the seller's Fee Preview.

## What is verified, and how

| Source | Backs |
| --- | --- |
| `research/fees.html` + the 4 extract/build scripts | All 219 referral rates, all six closing-fee group lists, the ₹72 exception list. Deterministic — re-running reproduces the committed JSON and appendix HTML byte-for-byte. |
| `research/ratecards/*.jpg` (10 images) | Every closing-fee and weight-handling rate. Read by eye; no script can confirm them. `audit_handbook.py` re-checks them against the book. |
| `research/fc/README.md` | All FC codes, the 22.5 kg standard-size ceiling, Heavy & Bulky limits. Transcribed from Amazon's FC Capabilities sheet. |
| `research/account/*.csv` | Every figure in Chapter 3, the COD/RTO table in Chapter 24, and the returns analysis in Chapter 20. |

Confidence tags used throughout: **VERIFIED** (named source, linked), **UNCONFIRMED**
(probably right, nobody checked), **CHECK LIVE** (only visible inside the seller's
account), **UNSETTLED** (credible sources disagree). The audit prints the current counts.

## Known limits — do not "fix" these by guessing

1. **`research/product.html` is not a product page.** It contains Amazon's
   "Continue shopping" bot wall, 3,793 bytes, zero product markup. `parse_product.py`
   diagnoses this correctly and exits non-zero. To fix it the seller must re-save the
   page from a signed-in browser as *Webpage, HTML Only*.
2. **Two claims remain genuinely unverified:** the 13-day refund processing time in
   Chapter 20 (no public source states it) and the "16 Heavy & Bulky centres" count.
3. **The SAFE-T 30-day filing window is US-sourced.** Every source describing the
   60→30 day change refers to Amazon.com. India may still be 60 days. Tagged accordingly.
4. **Storage: the published rate and the actual bill disagree.** Amazon publishes
   ₹50/cubic foot/month; the seller was charged ₹23.02 for July, roughly a tenth of a
   naive estimate. Likely average-daily-volume billing plus a new-seller concession.
   Budget from the settlement report, not the headline rate. Flagged in Chapter 9.

## House rules for editing

- **Never use Unicode arrows.** Write `-&gt;` and `&lt;-`. `→` `←` `≥` are dropped from
  the PDF silently. This shipped as a live bug once already.
- Edit the `partN.html` sources, never `handbook_full.html` or the PDF — both are generated.
- `research/` scripts read relative paths, so `cd research` first. `handbook/build.py`
  resolves via `__file__` and works from anywhere.
- Rate-card JPGs are cited in prose only, never as `<img src>`. Renaming them orphans citations.
- Run the audit before committing. It exits non-zero on failure.
- Currency is INR, written `₹`. Fee tables use the `·` separator.

## Where the open items live

`research/account/open-questions.md` is the live worklist: the resolved Seller Support
case, the inbound shortage claim still to file, the STEP and mission status, and the
account-level to-dos. Read it after this file.
