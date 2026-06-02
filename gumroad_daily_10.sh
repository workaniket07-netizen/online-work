#!/bin/bash
# Run daily: adds next 10 products to Gumroad
cd /Users/aniket/Desktop/online-work-site
python3 << 'PYEOF'
import os, re, json, time, urllib.request, urllib.parse

TOKEN = "VqPxTEOv-PzfRIwTjTxxyhdl3wanXE54T7iQvnjSA1Q"
BASE = "/Users/aniket/Desktop/online-work-site/products"
RESULTS = "/Users/aniket/Desktop/online-work-site/CREATED_PRODUCTS.json"

results = json.load(open(RESULTS))
already_done = set(results.keys())
folders = sorted([f for f in os.listdir(BASE) if f[0].isdigit() and os.path.isdir(f"{BASE}/{f}")])
todo = [f for f in folders if f not in already_done][:10]

def read_listing(folder):
    path = f"{BASE}/{folder}/gumroad-listing.txt"
    if not os.path.exists(path): return None, None, None
    with open(path) as f: c = f.read()
    t = re.search(r'PRODUCT TITLE:\s*(.+)', c)
    p = re.search(r'PRICE:\s*\$(\d+)', c)
    d = re.search(r'SHORT DESC:\s*(.+)', c)
    return (t.group(1).strip()[:255] if t else folder,
            int(p.group(1)) * 100 if p else 12700,
            d.group(1).strip()[:3000] if d else "")

created = 0
for folder in todo:
    title, price, desc = read_listing(folder)
    if not title: continue
    data = urllib.parse.urlencode({"access_token": TOKEN, "name": title, "description": desc, "price": str(price)}).encode()
    req = urllib.request.Request("https://api.gumroad.com/v2/products", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            result = json.loads(r.read())
            if result.get("success"):
                p = result.get("product", {})
                permalink = p.get("short_url","").split("/")[-1]
                results[folder] = {"title": title, "price": price, "permalink": permalink}
                created += 1
                time.sleep(1)
    except: time.sleep(1)

with open(RESULTS, 'w') as f: json.dump(results, f, indent=2)
print(f"Gumroad: +{created} today | Total: {len(results)}")
PYEOF
