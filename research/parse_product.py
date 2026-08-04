#!/usr/bin/env python3
import re, html, pathlib

raw = pathlib.Path("product.html").read_text(encoding="utf-8", errors="ignore")

def txt(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def first(pats, label):
    for p in pats:
        m = re.search(p, raw, re.S | re.I)
        if m:
            v = txt(m.group(1))
            if v:
                print(f"{label:22} {v[:150]}")
                return v
    print(f"{label:22} -- not found --")
    return None

print("=" * 78)
first([r'<span id="productTitle"[^>]*>(.*?)</span>'], "TITLE")
first([r'id="landingImage"[^>]*alt="([^"]+)"'], "IMAGE ALT")
first([r'<span class="a-price-whole">(.*?)</span>',
       r'"displayPrice"\s*:\s*"([^"]+)"',
       r'id="priceblock_ourprice"[^>]*>(.*?)</span>'], "PRICE")
first([r'<a id="bylineInfo"[^>]*>(.*?)</a>',
       r'id="brand"[^>]*>(.*?)<'], "BYLINE / BRAND")
first([r'Sold by</span>.{0,300}?<span[^>]*>(.*?)</span>',
       r'id="sellerProfileTriggerId"[^>]*>(.*?)</a>'], "SOLD BY")
first([r'Fulfilled by\s*</span>\s*<span[^>]*>(.*?)</span>'], "FULFILLED BY")

print("-" * 78)
# breadcrumb / category
bc = re.search(r'id="wayfinding-breadcrumbs_feature_div"(.*?)</div>\s*</div>', raw, re.S)
if bc:
    parts = [txt(a) for a in re.findall(r'<a[^>]*>(.*?)</a>', bc.group(1), re.S)]
    print("BREADCRUMB          ", " > ".join(p for p in parts if p))

print("-" * 78)
# product details table (dimensions, weight, brand, manufacturer)
KEYS = ('dimension', 'weight', 'brand', 'manufacturer', 'asin', 'material',
        'item length', 'net quantity', 'country of origin', 'importer', 'packer',
        'best sellers rank', 'date first available', 'colour', 'size')
found = {}
for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', raw, re.S):
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', m.group(1), re.S)
    if len(cells) >= 2:
        k, v = txt(cells[0]).rstrip(':').strip(), txt(cells[1])
        if k and v and any(x in k.lower() for x in KEYS):
            found.setdefault(k, v)
for m in re.finditer(r'<li[^>]*>\s*<span class="a-list-item">\s*<span class="a-text-bold">(.*?)</span>\s*<span>(.*?)</span>', raw, re.S):
    k, v = txt(m.group(1)).rstrip(':').replace('\u200f','').replace('\u200e','').strip(), txt(m.group(2))
    if k and v and any(x in k.lower() for x in KEYS):
        found.setdefault(k, v)

print("PRODUCT DETAILS")
for k, v in found.items():
    print(f"   {k[:34]:36} {v[:90]}")

print("-" * 78)
for label, pat in [("other sellers", r'(\d+)\s+(?:other |)(?:new |)offers?'),
                   ("ratings count", r'([\d,]+)\s*ratings'),
                   ("stars", r'([\d.]+)\s*out of 5 stars'),
                   ("returns policy", r'(\d+\s*Days?\s*Return[^<]{0,30})'),
                   ("A+ / brand store", r'(Visit the [^<]{1,40} Store)')]:
    m = re.search(pat, raw, re.I)
    print(f"{label:22} {txt(m.group(1)) if m else '-- not found --'}")
print("=" * 78)
