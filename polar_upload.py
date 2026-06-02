#!/usr/bin/env python3
"""
Polar.sh Auto-Uploader
API key from: polar.sh → Settings → Developers → New Token
"""
import os, json, time, argparse, re
import urllib.request

PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/POLAR_CREATED.json"
BASE_URL = "https://api.polar.sh/v1"

def polar_request(method, endpoint, data=None, api_key=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def read_listing(folder):
    path = os.path.join(PRODUCTS_DIR, folder, "gumroad-listing.txt")
    if not os.path.exists(path): return None, None, 127
    with open(path) as f: content = f.read()
    title = re.search(r'PRODUCT TITLE:\s*(.+)', content)
    price = re.search(r'PRICE:\s*\$(\d+)', content)
    desc = re.search(r'SHORT DESC:\s*(.+)', content)
    t = title.group(1).strip() if title else folder
    p = int(price.group(1)) if price else 127
    d = desc.group(1).strip() if desc else t
    return t, d, p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--org-id", required=True, help="Organization ID from polar.sh settings")
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
        if folder in results: skipped += 1; continue

        title, desc, price_usd = read_listing(folder)
        if not title: continue

        data = {
            "organization_id": args.org_id,
            "name": title[:255],
            "description": desc[:1000],
            "prices": [{"price_amount": price_usd * 100, "price_currency": "usd", "type": "one_time"}],
            "is_archived": False
        }

        result = polar_request("POST", "/products", data, args.api_key)

        if "id" in result:
            results[folder] = {"id": result["id"], "title": title}
            with open(RESULTS_FILE, 'w') as f: json.dump(results, f, indent=2)
            print(f"✅ {folder[:50]} → {result['id']}")
            created += 1
            time.sleep(0.3)
        else:
            print(f"❌ {folder[:40]}: {result.get('error','?')}")
            errors += 1
            time.sleep(1)

    print(f"\nDone: {created} created | {skipped} skipped | {errors} errors")

if __name__ == "__main__":
    main()
