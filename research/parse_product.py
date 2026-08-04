#!/usr/bin/env python3
"""Extract product attributes from a saved Amazon product page.

    python3 parse_product.py [path/to/page.html]   # default: product.html
    python3 parse_product.py --selftest            # check the patterns still fire

Why this script previously appeared broken: it was handed Amazon's "Continue
shopping" bot-interstitial rather than a product page, and reported that as
fifteen '-- not found --' lines while exiting 0. That is indistinguishable from
Amazon having changed their markup. It now classifies the input first and exits
non-zero with a specific diagnosis, so the two failure modes cannot be confused.
"""
import re, html, pathlib, sys

# --- field patterns, most specific first ------------------------------------
FIELDS = [
    ("TITLE", [r'<span id="productTitle"[^>]*>(.*?)</span>',
               r'<h1[^>]*id="title"[^>]*>(.*?)</h1>',
               r'<meta name="title" content="([^"]+)"']),
    ("IMAGE ALT", [r'id="landingImage"[^>]*alt="([^"]+)"',
                   r'<img[^>]*data-old-hires[^>]*alt="([^"]+)"']),
    ("PRICE", [r'<span class="a-price-whole">(.*?)</span>',
               r'"displayPrice"\s*:\s*"([^"]+)"',
               r'id="priceblock_ourprice"[^>]*>(.*?)</span>',
               r'class="a-offscreen">\s*(\u20b9[\d,.]+)\s*</span>',
               r'"priceAmount"\s*:\s*([\d.]+)']),
    ("BYLINE / BRAND", [r'<a id="bylineInfo"[^>]*>(.*?)</a>',
                        r'id="brand"[^>]*>(.*?)<',
                        r'<tr[^>]*>\s*<t[dh][^>]*>\s*Brand\s*</t[dh]>\s*<t[dh][^>]*>(.*?)</t[dh]>']),
    ("SOLD BY", [r'id="sellerProfileTriggerId"[^>]*>(.*?)</a>',
                 r'Sold by</span>.{0,300}?<span[^>]*>(.*?)</span>',
                 r'"merchantName"\s*:\s*"([^"]+)"']),
    ("FULFILLED BY", [r'Fulfilled by\s*</span>\s*<span[^>]*>(.*?)</span>',
                      r'Ships from</span>.{0,300}?<span[^>]*>(.*?)</span>']),
]
DETAIL_KEYS = ('dimension', 'weight', 'brand', 'manufacturer', 'asin', 'material',
               'item length', 'net quantity', 'country of origin', 'importer',
               'packer', 'best sellers rank', 'date first available', 'colour', 'size')
# markers that indicate a genuine product page, whatever else changed
PRODUCT_MARKERS = ('productTitle', 'a-price-whole', 'bylineInfo', 'landingImage',
                   'merchant-info', 'feature-bullets', 'averageCustomerReviews',
                   'wayfinding-breadcrumbs', 'sellerProfileTriggerId',
                   'dp-container', 'centerCol')


def txt(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def classify(raw):
    """Return (verdict, explanation). verdict is 'product' or a failure kind."""
    low = raw.lower()
    visible = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', raw, flags=re.S | re.I)
    visible = html.unescape(re.sub(r'<[^>]+>', '\n', visible))
    n_lines = len([l for l in visible.split('\n') if l.strip()])

    if 'click the button below to continue shopping' in low or \
       ('continue shopping' in low and n_lines < 25):
        return 'bot_wall', ("Amazon's \u201cContinue shopping\u201d interstitial \u2014 "
                            "the anti-automation wall, not a product page")
    if 'enter the characters you see below' in low or 'api-services-support@amazon' in low \
            or 'type the characters you see in this image' in low:
        return 'captcha', "Amazon's CAPTCHA / \u201cSorry, we just need to make sure\u201d page"
    if 'page not found' in low or "we couldn't find that page" in low:
        return 'not_found', "Amazon's 404 page"
    if 'sign in' in low and n_lines < 40:
        return 'signin', 'a sign-in page'

    hits = [m for m in PRODUCT_MARKERS if m.lower() in low]
    if not hits:
        return 'not_product', (f"no product-page markers at all (looked for "
                               f"{len(PRODUCT_MARKERS)}); only {n_lines} lines of "
                               f"visible text, {len(raw):,} bytes")
    return 'product', f"{len(hits)} of {len(PRODUCT_MARKERS)} product markers present"


HOWTO = """
How to save a usable page:
  1. Open the product page in a browser where you are already signed in to
     Amazon.in and have clicked through any 'Continue shopping' prompt.
  2. Confirm you can see the title, price and 'Sold by' on screen.
  3. Save with Ctrl+S / Cmd+S as "Webpage, HTML Only" (not "Complete").
     Saving the rendered page from a logged-in session is what avoids the wall;
     fetching the URL with curl or a fresh incognito window will hit it again.
  4. Replace research/product.html and re-run this script.
"""

SAMPLE = '''<html><head><meta name="title" content="Sample"></head><body>
<div id="dp-container"><span id="productTitle">  Test Clothesline Wire 20m  </span>
<img id="landingImage" alt="Test Clothesline Wire, PVC coated" src="x.jpg">
<span class="a-price-whole">333</span>
<a id="bylineInfo" href="/x">Visit the ExampleBrand Store</a>
<div id="merchant-info">Sold by</span> <span>ExampleSeller</span>
Fulfilled by </span> <span>Amazon</span></div>
<div id="wayfinding-breadcrumbs_feature_div"><ul>
<a href="/a">Home &amp; Kitchen</a><a href="/b">Laundry Organization</a>
<a href="/c">Clotheslines</a></ul></div></div>
<table><tr><td>Item Weight</td><td>460 g</td></tr>
<tr><td>Brand</td><td>ExampleBrand</td></tr>
<tr><td>Country of Origin</td><td>India</td></tr></table>
<span>4.2 out of 5 stars</span><span>1,204 ratings</span>
</body></html>'''


def parse(raw, quiet=False):
    """Extract everything. Returns dict of found values."""
    out = {}

    def emit(label, value):
        if not quiet:
            print(f"{label:22} {value[:150] if value else '-- not found --'}")

    print("=" * 78) if not quiet else None
    for label, pats in FIELDS:
        val = None
        for p in pats:
            m = re.search(p, raw, re.S | re.I)
            if m and txt(m.group(1)):
                val = txt(m.group(1))
                break
        if val:
            out[label] = val
        emit(label, val)

    if not quiet:
        print("-" * 78)
    bc = re.search(r'id="wayfinding-breadcrumbs_feature_div"(.*?)(?:</ul>|</div>\s*</div>)',
                   raw, re.S)
    if bc:
        parts = [txt(a) for a in re.findall(r'<a[^>]*>(.*?)</a>', bc.group(1), re.S)]
        parts = [p for p in parts if p]
        if parts:
            out['BREADCRUMB'] = " > ".join(parts)
            if not quiet:
                print("BREADCRUMB            " + out['BREADCRUMB'][:150])

    details = {}
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', raw, re.S):
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', m.group(1), re.S)
        if len(cells) >= 2:
            k, v = txt(cells[0]).rstrip(':').strip(), txt(cells[1])
            if k and v and any(x in k.lower() for x in DETAIL_KEYS):
                details.setdefault(k, v)
    for m in re.finditer(r'<li[^>]*>\s*<span class="a-list-item">\s*'
                         r'<span class="a-text-bold">(.*?)</span>\s*<span>(.*?)</span>', raw, re.S):
        k = txt(m.group(1)).rstrip(':').replace('\u200f', '').replace('\u200e', '').strip()
        v = txt(m.group(2))
        if k and v and any(x in k.lower() for x in DETAIL_KEYS):
            details.setdefault(k, v)
    if details:
        out['DETAILS'] = details
    if not quiet:
        print("-" * 78)
        print(f"PRODUCT DETAILS ({len(details)} rows)")
        for k, v in details.items():
            print(f"   {k[:34]:36} {v[:90]}")
        print("-" * 78)

    for label, pat in [("other sellers", r'(\d+)\s+(?:other |)(?:new |)offers?'),
                       ("ratings count", r'([\d,]+)\s*ratings'),
                       ("stars", r'([\d.]+)\s*out of 5 stars'),
                       ("returns policy", r'(\d+\s*Days?\s*Return[^<]{0,30})'),
                       ("A+ / brand store", r'(Visit the [^<]{1,40} Store)')]:
        m = re.search(pat, raw, re.I)
        if m:
            out[label] = txt(m.group(1))
        emit(label, txt(m.group(1)) if m else None)
    if not quiet:
        print("=" * 78)
    return out


def selftest():
    """Prove the patterns still fire, without needing a real Amazon page."""
    verdict, why = classify(SAMPLE)
    got = parse(SAMPLE, quiet=True)
    expect = {
        'TITLE': 'Test Clothesline Wire 20m',
        'IMAGE ALT': 'Test Clothesline Wire, PVC coated',
        'PRICE': '333',
        'BYLINE / BRAND': 'Visit the ExampleBrand Store',
        'SOLD BY': 'ExampleSeller',
        'FULFILLED BY': 'Amazon',
        'BREADCRUMB': 'Home & Kitchen > Laundry Organization > Clotheslines',
        'stars': '4.2',
        'ratings count': '1,204',
    }
    fails = [f"classify() said {verdict!r}, expected 'product'"] if verdict != 'product' else []
    for k, want in expect.items():
        if got.get(k) != want:
            fails.append(f"{k}: got {got.get(k)!r}, expected {want!r}")
    for k in ('Item Weight', 'Brand', 'Country of Origin'):
        if k not in got.get('DETAILS', {}):
            fails.append(f"DETAILS missing {k!r}")

    for k, want in expect.items():
        mark = "ok  " if got.get(k) == want else "FAIL"
        print(f"  [{mark}] {k:16} {str(got.get(k))[:52]}")
    print(f"  [{'ok  ' if len(got.get('DETAILS', {})) >= 3 else 'FAIL'}] "
          f"{'DETAILS':16} {len(got.get('DETAILS', {}))} rows")
    if fails:
        print("\nSELFTEST FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print("\nSelftest passed: all field patterns fire on a known-good sample.")
    return 0


def main():
    args = [a for a in sys.argv[1:]]
    if '--selftest' in args:
        return selftest()
    path = pathlib.Path(args[0] if args else "product.html")
    if not path.exists():
        sys.exit(f"{path} not found - run this script from inside research/ "
                 "(paths are relative to the working directory)")

    raw = path.read_text(encoding="utf-8", errors="ignore")
    verdict, why = classify(raw)
    print(f"INPUT   {path}  ({len(raw):,} bytes)")
    print(f"VERDICT {verdict}: {why}\n")

    if verdict != 'product':
        print(f"Cannot parse: this file is {why}.")
        print("Nothing was extracted because there is nothing in the file to extract -")
        print("this is NOT a sign that Amazon changed their markup.")
        print(HOWTO)
        return 1

    got = parse(raw)
    core = [k for k in ('TITLE', 'PRICE', 'SOLD BY', 'BYLINE / BRAND') if k in got]
    print(f"\nExtracted {len(got)} fields; {len(core)} of 4 core fields "
          f"({', '.join(core) or 'none'}).")
    if len(core) < 2:
        print("\nThe page looks like a product page but almost nothing parsed - this DOES")
        print("suggest Amazon's markup changed. Run --selftest to confirm the patterns")
        print("themselves still work, then update FIELDS.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
