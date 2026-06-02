#!/usr/bin/env python3
"""
SendOwl Auto-Uploader
API key from: SendOwl Dashboard → Account → Integrations → API
"""
import os, json, time, argparse, re, base64
import urllib.request, urllib.parse

PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/SENDOWL_CREATED.json"
BASE_URL = "https://app.sendowl.com/api/v1_3"

def so_request(endpoint, data, api_key, api_secret):
    url = f"{BASE_URL}{endpoint}.json"
    credentials = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
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
    t = title.group(1).strip() if title else folder
    p = int(price.group(1)) if price else 127
    return t, p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--api-secret", required=True)
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

        title, price = read_listing(folder)
        if not title: continue

        data = {
            "product[name]": title[:200],
            "product[price]": str(price),
            "product[product_type]": "digital",
            "product[currency]": "USD",
        }

        result = so_request("/products", data, args.api_key, args.api_secret)

        if "product" in result:
            pid = result["product"]["id"]
            results[folder] = {"id": pid, "title": title}
            with open(RESULTS_FILE, 'w') as f: json.dump(results, f, indent=2)
            print(f"✅ {folder[:50]} → ID:{pid}")
            created += 1
            time.sleep(0.5)
        else:
            print(f"❌ {folder[:40]}: {result.get('error','?')}")
            errors += 1
            time.sleep(1)

    print(f"\nDone: {created} created | {skipped} skipped | {errors} errors")

if __name__ == "__main__":
    main()
