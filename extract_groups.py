#!/usr/bin/env python3
"""Extract the closing-fee group -> category assignments from the live page."""
import re, html, json, pathlib

raw = pathlib.Path("fees.html").read_text(encoding="utf-8", errors="ignore")
t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n') if l.strip()]

MARK = re.compile(r'^\((Group (?:#{1,2}|[A-D]))\)$')
STOP = re.compile(r'(closing fee applies|item price|^✕$|^\*|Weight Handling|Other Fees|'
                  r'Fulfillment Channels|Calculating Profitability|^Note|^NOTE)', re.I)

groups, cur = {}, None
for l in lines:
    m = MARK.match(l)
    if m:
        cur = m.group(1)
        groups.setdefault(cur, [])
        continue
    if cur is None:
        continue
    if STOP.search(l):
        cur = None
        continue
    # plausible category name
    if 2 < len(l) < 160 and not l.endswith('%'):
        groups[cur].append(l)

# de-dupe within each group, keep order
out = {}
for g, items in groups.items():
    seen, keep = set(), []
    for c in items:
        k = c.lower()
        if k not in seen:
            seen.add(k); keep.append(c)
    if keep:
        out[g] = keep

pathlib.Path("closing_groups_live.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

RATES = {'Group #': '₹26 · ₹0–300', 'Group ##': '₹22 · ₹301–500',
         'Group A': '₹20 · ₹0–300',  'Group B': '₹13 · ₹0–300',
         'Group C': '₹18 · ₹301–500', 'Group D': '₹14 · ₹301–500'}
for g in ['Group #', 'Group ##', 'Group A', 'Group B', 'Group C', 'Group D']:
    items = out.get(g, [])
    print(f"{g:9} {RATES[g]:16} {len(items):3} categories")
    if items:
        print(f"          e.g. {', '.join(items[:4])[:110]}")
