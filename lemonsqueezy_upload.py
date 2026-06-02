#!/usr/bin/env python3
"""
Lemon Squeezy Auto-Uploader
Usage: python3 lemonsqueezy_upload.py --api-key YOUR_KEY --store-id YOUR_STORE_ID
Gets both from: LemonSqueezy Dashboard → Settings → API
"""
import os, json, time, argparse
import urllib.request, urllib.parse

PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/LS_CREATED.json"
BASE_URL = "https://api.lemonsqueezy.com/v1"

def ls_request(method, endpoint, data=None, api_key=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def create_product(title, description, price_cents, store_id, api_key):
    data = {
        "data": {
            "type": "products",
            "attributes": {
                "name": title,
                "description": description,
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": str(store_id)}}
            }
        }
    }
    return ls_request("POST", "/products", data, api_key)

def read_listing(folder):
    path = os.path.join(PRODUCTS_DIR, folder, "gumroad-listing.txt")
    if not os.path.exists(path): return None, None, 127
    with open(path) as f: content = f.read()
    import re
    title = re.search(r'PRODUCT TITLE:\s*(.+)', content)
    price = re.search(r'PRICE:\s*\$(\d+)', content)
    desc = re.search(r'SHORT DESC:\s*(.+)', content)
    t = title.group(1).strip() if title else folder
    p = int(price.group(1)) * 100 if price else 12700
    d = desc.group(1).strip() if desc else t
    return t, d, p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--store-id", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f: results = json.load(f)

    folders = sorted([f for f in os.listdir(PRODUCTS_DIR)
                      if f[0].isdigit() and os.path.isdir(f"{PRODUCTS_DIR}/{f}")])

    created = skipped = errors = 0
    for folder in folders:
        if created >= args.limit: break
        if folder in results:
            skipped += 1
            continue

        title, desc, price = read_listing(folder)
        if not title: continue

        result = create_product(title, desc, price, args.store_id, args.api_key)

        if "data" in result:
            pid = result["data"]["id"]
            results[folder] = {"id": pid, "title": title, "price": price}
            with open(RESULTS_FILE, 'w') as f: json.dump(results, f, indent=2)
            print(f"✅ {folder[:50]} → ID:{pid}")
            created += 1
            time.sleep(0.3)
        else:
            print(f"❌ {folder[:40]}: {result.get('error','unknown')}")
            errors += 1
            time.sleep(1)

    print(f"\nDone: {created} created | {skipped} skipped | {errors} errors")

if __name__ == "__main__":
    main()
