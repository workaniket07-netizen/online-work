#!/usr/bin/env python3
"""
Etsy Auto-Uploader
Steps to get keys:
1. etsy.com/developers → Create App
2. Get: keystring + shared_secret
3. OAuth token (me guide karito when you have keystring)
"""
import os, json, time, argparse, re
import urllib.request, urllib.parse

PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/ETSY_CREATED.json"
BASE_URL = "https://openapi.etsy.com/v3"

def etsy_request(endpoint, data, api_key, access_token):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
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
    if not os.path.exists(path): return None, None, None, 127
    with open(path) as f: content = f.read()
    title = re.search(r'PRODUCT TITLE:\s*(.+)', content)
    price = re.search(r'PRICE:\s*\$(\d+)', content)
    tags = re.search(r'TAGS:\s*(.+)', content)
    t = title.group(1).strip() if title else folder
    p = int(price.group(1)) if price else 127
    tg = tags.group(1).strip() if tags else "AI prompts, digital download"
    return t, tg, None, p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True, help="Etsy API keystring")
    parser.add_argument("--access-token", required=True, help="OAuth access token")
    parser.add_argument("--shop-id", required=True)
    parser.add_argument("--limit", type=int, default=10, help="Etsy: start slow, 10/day")
    args = parser.parse_args()

    results = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f: results = json.load(f)

    folders = sorted([f for f in os.listdir(PRODUCTS_DIR)
                      if f[0].isdigit() and os.path.isdir(f"{PRODUCTS_DIR}/{f}")])

    created = 0
    for folder in folders:
        if created >= args.limit: break
        if folder in results: continue

        title, tags_str, _, price = read_listing(folder)
        if not title: continue

        # Etsy needs: title, description, price, tags, quantity, taxonomy_id
        tags_list = [t.strip()[:20] for t in tags_str.split(',')][:13]

        data = {
            "title": title[:140],
            "description": f"AI-powered prompt system. Commercial license. {title}",
            "price": str(price),
            "quantity": "999",
            "tags": tags_list,
            "who_made": "i_did",
            "when_made": "made_to_order",
            "taxonomy_id": "2078",  # Digital → Templates & Downloads
            "type": "digital",
            "state": "draft",
            "shipping_profile_id": "0",
        }

        result = etsy_request(f"/application/shops/{args.shop_id}/listings", data,
                               args.api_key, args.access_token)

        if "listing_id" in result:
            lid = result["listing_id"]
            results[folder] = {"listing_id": lid, "title": title}
            with open(RESULTS_FILE, 'w') as f: json.dump(results, f, indent=2)
            print(f"✅ {folder[:50]} → listing:{lid}")
            created += 1
            time.sleep(1)  # Etsy rate limit: slow down
        else:
            print(f"❌ {folder[:40]}: {result.get('error','?')}")
            time.sleep(2)

    print(f"\nDone: {created} Etsy listings created")

if __name__ == "__main__":
    main()
