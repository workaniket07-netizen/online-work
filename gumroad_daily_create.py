#!/usr/bin/env python3
"""
Run daily: python3 ~/Desktop/online-work-site/gumroad_daily_create.py
Creates next 10 products. Run each morning until all 50 are created.
"""
import os, re, json, time, urllib.request, urllib.parse

GUMROAD_TOKEN = "VqPxTEOv-PzfRIwTjTxxyhdl3wanXE54T7iQvnjSA1Q"
PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/CREATED_PRODUCTS.json"

PRODUCTS = [
    ("01-ai-business-vault", 4700),
    ("02-midjourney-cinematic", 2700),
    ("03-instagram-content-machine", 1900),
    ("04-photography-prompts", 2200),
    ("05-chatgpt-copywriting", 3700),
    ("06-freelancer-client-vault", 4700),
    ("07-youtube-script-machine", 3700),
    ("08-linkedin-domination-vault", 3700),
    ("09-seo-content-machine", 3700),
    ("10-email-marketing-funnel-kit", 4700),
    ("11-creator-monetization-pack", 3700),
    ("12-notion-productivity-os", 3700),
    ("13-profession-ai-prompts", 4700),
    ("14-business-sop-templates", 4700),
    ("15-resume-career-kit", 2700),
    ("16-ecommerce-launch-kit", 3700),
    ("17-ai-side-hustle-vault", 4700),
    ("18-tiktok-viral-vault", 3700),
    ("19-student-ai-vault", 2700),
    ("20-personal-finance-playbook", 3700),
    ("21-pinterest-marketing-machine", 2700),
    ("22-wedding-planning-kit", 3700),
    ("23-mindset-journal-system", 1900),
    ("24-podcast-launch-kit", 3700),
    ("25-airbnb-superhost-kit", 3700),
    ("26-amazon-kdp-kit", 3700),
    ("27-fitness-coaching-templates", 3700),
    ("28-canva-creator-kit", 2700),
    ("29-real-estate-investor", 4700),
    ("30-social-media-agency", 4700),
    ("31-prompt-engineering-masterclass", 4700),
    ("32-teacher-classroom-pack", 1900),
    ("33-dating-profile-kit", 1900),
    ("34-parenting-templates", 1900),
    ("35-mental-health-workbook", 2700),
    ("36-startup-founder-toolkit", 4700),
    ("37-etsy-business-kit", 3700),
    ("38-dropshipping-kit", 3700),
    ("39-photography-business", 3700),
    ("40-virtual-assistant-kit", 4700),
    ("41-nutrition-coaching", 3700),
    ("42-language-learning-ai", 2700),
    ("43-home-organization", 1900),
    ("44-consulting-sow-kit", 4700),
    ("45-grant-writing-vault", 4700),
    ("46-youtube-channel-growth", 3700),
    ("47-investment-tracking", 3700),
    ("48-adulting-life-skills", 1900),
    ("49-book-writing-kit", 3700),
    ("50-nonprofit-fundraising", 4700),
]

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def read_listing(folder):
    path = os.path.join(PRODUCTS_DIR, folder, "gumroad-listing.txt")
    with open(path, 'r', errors='replace') as f:
        content = f.read()
    title_m = re.search(r'PRODUCT TITLE:\s*\n(.+)', content)
    title = title_m.group(1).strip() if title_m else folder
    desc_m = re.search(r'LONG DESCRIPTION:.*?\n(.*?)(?:━{5,}|\ZTAGS:)', content, re.DOTALL)
    if not desc_m:
        desc_m = re.search(r'SHORT DESCRIPTION.*?:\n(.+)', content)
    desc = desc_m.group(1).strip()[:3000] if desc_m else title
    return title, desc

def create_product(name, description, price):
    data = urllib.parse.urlencode({
        "access_token": GUMROAD_TOKEN,
        "name": name,
        "description": description,
        "price": str(price),
    }).encode('utf-8')
    req = urllib.request.Request("https://api.gumroad.com/v2/products", data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode('utf-8', errors='replace')
            raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
            return json.loads(raw)
    except Exception as e:
        return {"success": False, "message": str(e)}

results = load_results()
created_today = 0
MAX_PER_DAY = 10

print("=" * 55)
print("GUMROAD DAILY CREATOR")
print(f"Already created: {len(results)}/{len(PRODUCTS)}")
print("=" * 55)

for folder, price in PRODUCTS:
    if folder in results and results[folder].get("permalink"):
        continue

    if created_today >= MAX_PER_DAY:
        print(f"\n⚠️  Daily limit ({MAX_PER_DAY}) reached. Run again tomorrow.")
        break

    print(f"Creating {folder}...", end=" ", flush=True)
    title, desc = read_listing(folder)
    result = create_product(title, desc, price)

    if result.get("success"):
        p = result.get("product", {})
        permalink = p.get("short_url", "").split("/")[-1]
        results[folder] = {
            "title": title,
            "price": price,
            "permalink": permalink,
            "product_id": p.get("id", "")
        }
        save_results(results)
        print(f"✅ gumroad.com/l/{permalink}")
        created_today += 1
        time.sleep(0.8)
    else:
        msg = result.get("message", "Unknown error")
        print(f"❌ {msg}")
        if "10 products" in msg or "429" in str(result):
            print("Daily limit reached. Run again tomorrow.")
            break
        time.sleep(2)

print(f"\nTotal created: {len(results)}/{len(PRODUCTS)}")
remaining = len(PRODUCTS) - len(results)
if remaining > 0:
    days_left = (remaining + MAX_PER_DAY - 1) // MAX_PER_DAY
    print(f"Remaining: {remaining} products | ~{days_left} more day(s)")
else:
    print("ALL 50 PRODUCTS CREATED! ✅")
    print("\nNEXT: Add files to each product, then publish.")
