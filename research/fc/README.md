# Fulfilment Centre Capabilities — source data

The FC code table in **Appendix F** of the handbook is transcribed from Amazon's
*Fulfilment Centre Capabilities* sheet, supplied by the seller on **7 August 2026**
(10 pages, PDF).

The PDF itself is not committed here — it was shared in a chat session, not downloaded
from a stable public URL. What follows is the transcription that Appendix F is built
from, so the handbook remains reproducible even without the original file.

## What the sheet confirms

| Field | Value |
| --- | --- |
| Max weight per unit, standard FC | **22.5 kg** |
| Max height per unit, standard FC | **1.66 m** (some FCs 1.83 m) |
| Max height per unit, Heavy & Bulky FC | **3 m** |
| Truck loading, floor level (Level 1) | **85 kg** per box |
| Truck loading, stacked (Level 2) | **44 kg** per box |

These four figures are what upgraded the Heavy & Bulky thresholds in Chapter 8.4 from
UNCONFIRMED to VERIFIED.

## FC codes by region, as printed in the sheet

Amazon groups these by **shipping region** (North / West / East / South / Central),
which is *not* the same as state. Appendix F regroups them by **state**, because that
is what matters for GST registration.

**North** — Gurgaon: DEL2, DEL4, DEL5 · New Delhi: DEX3, DEX8 · Delhi City: PNQ2
· Ludhiana: ATX1, SATF (H&B) · Jaipur: JPX1 · Bagru: JPX2 · Lucknow: LKO1, SLKY (H&B),
SLKF (H&B) · Gurugram: DED4, SHDZ, HDX1, HDO3, SDEU (H&B), SDEG (H&B), XNAB (MPS)
· Rajpura: LDX1

**West** — Mumbai: BOM4 · Bhiwandi: BOM5, BOM7, SBOW, SBOB (H&B), XWUA (MPS)
· Pune: PNQ3, SPUN (H&B) · Ahmedabad: AMD2 · Kheda: SAME (H&B) · Nagpur: NAX1
· Chennai: SMAK

**East** — Howrah: CCX1, SCUY (H&B) · Kolkata: CCX2, SCCX · Serampore: CCX4
· Guwahati: GAX1 · Changsari: SGAC (H&B) · Patna: PAX, SPAB (H&B)
· Bhubaneswar: BBX1 · Islampur: SCCE (H&B), XECP (MPS)

**South** — Bangalore: BLR5, BLR7, BLR8, SBLU, BLX1 (H&B), XSAJ (MPS)
· Hubballi: SBLL · Chennai: MAA4, SMAB (H&B) · Tiruvallur: SMAH (H&B)
· Coimbatore: CJB1, SCJY (H&B) · Karumathampatti: SCJF (H&B)
· Krishnagiri: SBLI, SCJB (H&B) · Hyderabad: HYD3, HYD8, SHYL, SHTX (H&B),
SHYH (H&B), SHTI (H&B), XSAD (MPS), XSIP (MPS) · Ernakulam: COX1
· Visakhapatnam: RJX1 · Anakapalli: SVTZ (H&B)

**Central** — Indore: IDX2 · Bhopal: SBHF (H&B)

Suffix key, from the sheet's own footnote: **(H&B)** = Heavy and Bulky.
**(MPS)** = Multi-Package Shipment site. Codes with no suffix are standard FCs.

## Two oddities in the sheet, left as-is

1. **PNQ2 is listed under "Delhi City"** in the North region, even though the PNQ
   prefix belongs to Pune. PNQ3 is separately listed under Pune in the West region.
   Appendix F omits PNQ2 rather than guess which is right. If your Inventory Ledger
   ever shows PNQ2, open the full address before assuming a state.
2. **SMAK is listed under the West region with city "Chennai."** Chennai is in Tamil
   Nadu, which is South. Region here means Amazon's shipping zone, not geography.
   Appendix F files it under Tamil Nadu, because GST follows the state.

## Codes independently confirmed by Amazon announcements

These 12 are corroborated by a public Amazon source as well as the sheet, and carry the
strongest confidence in Appendix F:

| Code | State | Announcement |
| --- | --- | --- |
| LDEB | Haryana (Jhajjar) | Heavy & Bulky FC, opened 1 Apr 2026 — full address published |
| BBX1 | Odisha | Opened 7 Apr 2025 |
| LDX1 | Punjab (Rajpura) | One of 5 FCs opened before Prime Day 2025 |
| IDX2 | Madhya Pradesh (Indore) | Same 5-FC announcement |
| COX1 | Kerala (Kochi) | Same 5-FC announcement |
| DED1 | Delhi NCR | Same 5-FC announcement |
| SIXR | Jharkhand | Transshipment centre, 20 May 2026 |
| SRPI | Chhattisgarh | Transshipment centre, 25 May 2026 |
| BLR8 | Karnataka | Covered in an aboutamazon.in feature |
| BLR5, BLR7 | Karnataka | Address published in FC documentation |
| HYD3, HYD8 | Telangana | Multiple Telangana FC announcements |

**LDEB is not in this sheet** — it opened after the sheet was produced. Appendix F adds
it from Amazon's own announcement. Expect the same gap for any FC opened later: the
sheet is a snapshot, not a live feed.
