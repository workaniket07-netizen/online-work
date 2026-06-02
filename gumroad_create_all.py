#!/usr/bin/env python3
"""
Gumroad Auto-Creator — Creates all 50 products via API
Run: python3 ~/Desktop/online-work-site/gumroad_create_all.py
"""
import os
import re
import json
import time
import urllib.request
import urllib.parse

GUMROAD_TOKEN = "VqPxTEOv-PzfRIwTjTxxyhdl3wanXE54T7iQvnjSA1Q"
PRODUCTS_DIR = "/Users/aniket/Desktop/online-work-site/products"
RESULTS_FILE = "/Users/aniket/Desktop/online-work-site/CREATED_PRODUCTS.json"

# Products already created (skip these)
ALREADY_CREATED = {
    "01-ai-business-vault": "njqbe"  # created via browser
}

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

def read_listing(folder):
    """Read gumroad-listing.txt and extract title + description"""
    path = os.path.join(PRODUCTS_DIR, folder, "gumroad-listing.txt")
    if not os.path.exists(path):
        print(f"  WARNING: No listing file for {folder}")
        return None, None

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'PRODUCT TITLE:\s*\n(.+)', content)
    title = title_match.group(1).strip() if title_match else folder

    # Extract long description (everything between LONG DESC and TAGS or end)
    desc_match = re.search(r'LONG DESCRIPTION:\s*\n(.*?)(?:TAGS:|━+\s*TAGS|$)', content, re.DOTALL)
    if not desc_match:
        # Try SHORT DESCRIPTION as fallback
        desc_match = re.search(r'SHORT DESCRIPTION.*?:\s*\n(.+)', content)

    description = desc_match.group(1).strip() if desc_match else f"Premium digital product: {title}"

    # Clean up description
    description = description[:3000]  # Gumroad limit

    return title, description

def create_product(name, description, price_cents):
    """Create a product via Gumroad API"""
    url = "https://api.gumroad.com/v2/products"

    data = urllib.parse.urlencode({
        "access_token": GUMROAD_TOKEN,
        "name": name,
        "description": description,
        "price": str(price_cents),
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8', errors='replace'))
            return result
    except Exception as e:
        return {"success": False, "message": str(e)}

def main():
    print("=" * 60)
    print("GUMROAD AUTO-CREATOR")
    print("=" * 60)
    print()

    results = {}

    # Load existing results
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            results = json.load(f)
        print(f"Loaded {len(results)} existing results")

    # Add already-created products
    for folder, permalink in ALREADY_CREATED.items():
        if folder not in results:
            results[folder] = {"permalink": permalink, "status": "created_browser"}

    created = 0
    skipped = 0
    errors = 0

    for folder, price_cents in PRODUCTS:
        if folder in results and results[folder].get("permalink"):
            print(f"SKIP (already exists): {folder}")
            skipped += 1
            continue

        print(f"Creating: {folder}...", end=" ", flush=True)

        title, description = read_listing(folder)
        if not title:
            print(f"ERROR - No listing file")
            errors += 1
            continue

        result = create_product(title, description, price_cents)

        if result.get("success"):
            product = result.get("product", {})
            permalink = product.get("short_url", "").split("/")[-1] or product.get("id", "")
            product_id = product.get("id", "")

            results[folder] = {
                "title": title,
                "price_cents": price_cents,
                "permalink": permalink,
                "product_id": product_id,
                "status": "created_api"
            }

            # Save after each product
            with open(RESULTS_FILE, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"✅ Created | URL: gumroad.com/l/{permalink}")
            created += 1
            time.sleep(0.5)  # Rate limiting
        else:
            print(f"❌ Error: {result.get('message', 'Unknown')}")
            errors += 1
            time.sleep(1)

    print()
    print("=" * 60)
    print(f"DONE: {created} created | {skipped} skipped | {errors} errors")
    print(f"Results saved to: {RESULTS_FILE}")
    print()
    print("NEXT STEPS:")
    print("1. Add files to each product (drag-drop prompts.txt)")
    print("2. Run: python3 gumroad_publish_all.py  (to publish all)")
    print("=" * 60)

if __name__ == "__main__":
    main()
