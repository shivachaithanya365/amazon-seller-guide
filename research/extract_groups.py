#!/usr/bin/env python3
"""Extract closing-fee group -> category assignments from the live page.

The page publishes SIX independent lists, not three. Two price bands:

    INR 0-300    Group #  (Rs 26)   Group A  (Rs 20)   Group B  (Rs 13)
    INR 301-500  Group ## (Rs 22)   Group C  (Rs 18)   Group D  (Rs 14)

The 301-500 lists have genuinely DIFFERENT membership from the 0-300 lists -
they are not a relabelling of them. Amazon's own example on the page proves it:
"Apparel - Shorts" sits in Group A (0-300) but in Group D (301-500), not Group C.
Never assume a mapping between bands; always read all six lists.

Markup shapes differ between groups, which is what defeated the previous version
of this script: '(Group #)' sits alone on a line, while Group C/D put the marker
at the END of the description line, and Group ## has no marker on its list header
at all and must be identified by its rate.
"""
import re, html, json, pathlib, sys

SRC = pathlib.Path("fees.html")
if not SRC.exists():
    sys.exit("fees.html not found - run this script from inside research/ "
             "(paths are relative to the working directory)")

raw = SRC.read_text(encoding="utf-8", errors="ignore")
t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
lines = [l.strip() for l in t.split('\n') if l.strip()]

# --- locate section headers -------------------------------------------------
# A list header is a line describing a closing fee for a price band. It may
# carry an explicit (Group X) marker before or after the text, or none at all.
HEADER = re.compile(
    r'For items priced between INR\s*(?P<lo>[\d,]+)\s*[-\u2013\u2014]\s*(?P<hi>[\d,]+)\s*,\s*'
    r'a?\s*\u20b9\s*(?P<rate>\d+)\s*closing fee', re.I)
MARKER = re.compile(r'\(Group (?P<g>#{1,2}|[A-D])\)')
BARE_MARKER = re.compile(r'^\(Group (?P<g>#{1,2}|[A-D])\)$')
# rate+band -> group, used when the header carries no marker
BY_RATE = {('0', '300', '26'): 'Group #',  ('301', '500', '22'): 'Group ##',
           ('0', '300', '20'): 'Group A',  ('301', '500', '18'): 'Group C',
           ('0', '300', '13'): 'Group B',  ('301', '500', '14'): 'Group D'}
# lines that terminate a category list
TERMINATOR = re.compile(
    r'^\u2715$|^\*|closing fee applies|Weight Handling|Other Fees|'
    r'Fulfillment Channels|Calculating Profitability|^Note|^NOTE|'
    r'^Seller flex$|^Easy Ship$|^Self Ship$', re.I)

# The legend block near the top lists all six groups back to back with no
# categories between them. Skip any header immediately followed by another
# header - those are legend entries, not list headers.
starts = []            # (index_of_first_category, group_name)
for i, l in enumerate(lines):
    m = HEADER.search(l)
    if not m:
        continue
    g = None
    mk = MARKER.search(l)
    if mk:
        g = f"Group {mk.group('g')}"
    else:
        key = (m.group('lo').replace(',', ''), m.group('hi').replace(',', ''),
               m.group('rate'))
        g = BY_RATE.get(key)
    if g is None:
        continue
    # step past any immediately following bare marker line, e.g. '(Group #)'
    j = i + 1
    if j < len(lines):
        bm = BARE_MARKER.match(lines[j])
        if bm:
            g = f"Group {bm.group('g')}"       # bare marker wins - most explicit
            j += 1
    # legend entry: next line is another header, so there are no categories here
    if j < len(lines) and HEADER.search(lines[j]):
        continue
    starts.append((j, g))

# --- slice each section -----------------------------------------------------
groups = {}
boundaries = [s for s, _ in starts]
for n, (start, g) in enumerate(starts):
    stop = boundaries[n + 1] if n + 1 < len(starts) else len(lines)
    items, seen = [], set()
    for l in lines[start:stop]:
        if TERMINATOR.search(l):
            break
        if not (2 < len(l) < 200) or l.endswith('%'):
            continue
        k = l.lower()
        if k not in seen:
            seen.add(k)
            items.append(l)
    # a group can be described more than once; keep the richest capture
    if len(items) > len(groups.get(g, [])):
        groups[g] = items

# --- the Rs 72 above-1,000 list --------------------------------------------
# Published separately, as a footnote rather than a numbered group.
for i, l in enumerate(lines):
    if re.search(r'^\*?\s*For items priced above INR\s*1,000\s*,\s*\u20b9\s*72\s*closing fee', l, re.I):
        items = []
        for nxt in lines[i + 1:]:
            if TERMINATOR.search(nxt) or HEADER.search(nxt):
                break
            if 2 < len(nxt) < 200:
                items.append(nxt)
        if len(items) > len(groups.get('Above 1000 (Rs 72)', [])):
            groups['Above 1000 (Rs 72)'] = items

ORDER = ['Group #', 'Group ##', 'Group A', 'Group B', 'Group C', 'Group D',
         'Above 1000 (Rs 72)']
out = {g: groups[g] for g in ORDER if groups.get(g)}

# --- validation -------------------------------------------------------------
# Fail loudly rather than silently emitting an empty or half-parsed group.
problems = []
for g in ORDER[:6]:
    if not out.get(g):
        problems.append(f"{g} is empty - the page markup has probably changed")

# Amazon's own worked examples on the page, used as ground truth.
CHECKS = [
    ('Group #', 'Grocery and Gourmet - Beverages',
     'Example 1: Beverages at Rs 249 -> Rs 26'),
    ('Group A', 'Apparel - Shorts',
     'Shorts must be in Group A for the 0-300 band'),
    ('Group D', 'Apparel - Shorts',
     'Example 2: Shorts at Rs 450 -> Rs 14, i.e. Group D not Group C'),
]
for g, cat, why in CHECKS:
    if cat not in out.get(g, []):
        problems.append(f"{g} is missing {cat!r} ({why})")
if 'Apparel - Shorts' in out.get('Group C', []):
    problems.append("'Apparel - Shorts' found in Group C, but Amazon's example "
                    "puts it in Group D - band lists may have been mis-sliced")

# no category may appear twice within the same price band
for band, gs in (('0-300', ['Group #', 'Group A', 'Group B']),
                 ('301-500', ['Group ##', 'Group C', 'Group D'])):
    seen = {}
    for g in gs:
        for c in out.get(g, []):
            if c in seen:
                problems.append(f"{c!r} is in both {seen[c]} and {g} "
                                f"(same {band} band - cannot be both)")
            seen[c] = g

pathlib.Path("closing_groups_live.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

RATES = {'Group #': 'Rs 26 - 0-300',   'Group ##': 'Rs 22 - 301-500',
         'Group A': 'Rs 20 - 0-300',   'Group C':  'Rs 18 - 301-500',
         'Group B': 'Rs 13 - 0-300',   'Group D':  'Rs 14 - 301-500',
         'Above 1000 (Rs 72)': 'Rs 72 - above 1,000'}
for g in ORDER:
    items = out.get(g, [])
    print(f"{g:20} {RATES[g]:22} {len(items):4} categories")
    if items:
        print(f"    e.g. {', '.join(items[:3])[:100]}")

print()
if problems:
    print("VALIDATION FAILED:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("Validation passed: all six groups populated, Amazon's own worked "
      "examples reproduced, no category duplicated within a price band.")
