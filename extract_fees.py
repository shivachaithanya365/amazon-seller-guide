#!/usr/bin/env python3
"""Extract the complete referral-fee table and closing-fee group lists from Amazon's live page HTML."""
import re, html, json, pathlib

raw = pathlib.Path("fees.html").read_text(encoding="utf-8", errors="ignore")

def clean(s):
    s = re.sub(r'<br\s*/?>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'\s*\|\s*(\|\s*)+', ' | ', s)
    return re.sub(r'\s+', ' ', s).strip(' |').strip()

# every "text" div, in document order, tagged by alignment
divs = re.findall(
    r'<div class="text align-(start|center)[^"]*">(.*?)</div>',
    raw, flags=re.S)

rows, i = [], 0
while i < len(divs) - 1:
    a_align, a_html = divs[i]
    b_align, b_html = divs[i + 1]
    if a_align == 'start' and b_align == 'center':
        cat, fee = clean(a_html), clean(b_html)
        if cat and fee and '%' in fee and 'item price' in fee:
            rows.append({"category": cat, "fee": fee})
            i += 2
            continue
    i += 1

# de-dupe, preserve order
seen, uniq = set(), []
for r in rows:
    k = r["category"].lower()
    if k not in seen:
        seen.add(k); uniq.append(r)

pathlib.Path("referral_fees_live.json").write_text(
    json.dumps(uniq, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"CATEGORIES EXTRACTED: {len(uniq)}")
print("\n=== first 12 ===")
for r in uniq[:12]:
    print(f"  {r['category'][:58]:60} {r['fee'][:78]}")

# closing-fee group definitions
txt = clean(raw)
print("\n=== closing fee group definitions (verbatim) ===")
for g in ['Group #\\)', 'Group ##\\)', 'Group A\\)', 'Group B\\)', 'Group C\\)', 'Group D\\)']:
    m = re.search(r'For items priced [^(]{0,70}\(' + g, txt)
    if m: print("  ", m.group(0))
m = re.search(r'\* For items priced above INR 1,000[^✕]{0,80}', txt)
if m: print("  ", m.group(0).strip())
