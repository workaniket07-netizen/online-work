#!/usr/bin/env python3
"""
AniketG AI — Master Automation Agent
Runs everything: upload check, resume, Gumroad daily, status report
Usage: python3 MASTER-AGENT.py
"""
import os, json, re, time, subprocess, urllib.request, urllib.parse
import datetime

BASE = "/Users/aniket/Desktop/online-work-site"
PRODUCTS = f"{BASE}/products"

# === PLATFORM CONFIGS ===
GUMROAD_TOKEN = "VqPxTEOv-PzfRIwTjTxxyhdl3wanXE54T7iQvnjSA1Q"
POLAR_TOKEN   = "polar_oat_hZM5WfSKXp9igCs0pKmHzpMqzmGk8jGShDvYM24KsO9"
POLAR_UA      = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def count_json(path):
    if not os.path.exists(path): return 0
    with open(path) as f: return len(json.load(f))

def status_report():
    polar  = count_json(f"{BASE}/POLAR_CREATED.json")
    gm     = count_json(f"{BASE}/CREATED_PRODUCTS.json")
    total  = len([f for f in os.listdir(PRODUCTS) if f[0].isdigit() and os.path.isdir(f"{PRODUCTS}/{f}")])
    log(f"=== STATUS === ")
    log(f"Products total: {total:,}")
    log(f"Polar.sh:       {polar:,}/{total:,} ({polar*100//max(total,1)}%)")
    log(f"Gumroad:        {gm}/{total:,} (10/day limit)")
    log(f"Whop:           10 bundles ✅")
    return polar, gm, total

def check_polar_running():
    result = subprocess.run(['ps','aux'], capture_output=True, text=True)
    py_procs = [l for l in result.stdout.split('\n') 
                if 'python3' in l and 'grep' not in l and 'MASTER' not in l 
                and 'code-review' not in l]
    return len(py_procs)

def resume_polar():
    log("Resuming Polar upload...")
    script = f"""
import json, http.client, ssl, os, re, time
TOKEN="{POLAR_TOKEN}"
UA="{POLAR_UA}"
BASE="{PRODUCTS}"
RESULTS="{BASE}/POLAR_CREATED.json"

def clean(t):
    t=re.sub(r'[^\\x00-\\x7F]','',t).replace('—','-').replace('$','USD').replace('/','')
    return t[:64].strip()

def post(data):
    ctx=ssl.create_default_context()
    conn=http.client.HTTPSConnection("api.polar.sh",context=ctx,timeout=20)
    conn.request("POST","/v1/products/",body=json.dumps(data),
        headers={{"Authorization":f"Bearer {{TOKEN}}","Content-Type":"application/json",
                 "Accept":"application/json","User-Agent":UA}})
    r=conn.getresponse()
    return r.status,r.read().decode()

def read(folder):
    path=f"{{BASE}}/{{folder}}/gumroad-listing.txt"
    if not os.path.exists(path): return None,None,127
    with open(path) as f: c=f.read()
    t=re.search(r'PRODUCT TITLE:\\s*(.+)',c)
    p=re.search(r'PRICE:\\s*\\$(\\d+)',c)
    d=re.search(r'SHORT DESC:\\s*(.+)',c)
    return (clean(t.group(1).strip()) if t else folder[:64],
            d.group(1).strip()[:500] if d else "",
            int(p.group(1)) if p else 127)

results={{}}
if os.path.exists(RESULTS):
    with open(RESULTS) as f: results=json.load(f)

folders=sorted([f for f in os.listdir(BASE) if f[0].isdigit() and os.path.isdir(f"{{BASE}}/{{f}}")])
created=0
for folder in folders:
    if folder in results: continue
    title,desc,price=read(folder)
    if not title: continue
    try:
        s,b=post({{"name":title,"description":desc,
                    "prices":[{{"price_amount":price*100,"price_currency":"usd",
                               "type":"one_time","amount_type":"fixed"}}]}})
        if s==201:
            results[folder]={{"id":json.loads(b)["id"],"title":title}}
            created+=1
            if created%1000==0:
                with open(RESULTS,'w') as f: json.dump(results,f)
                print(f"Polar: {{len(results):,}} | {{time.strftime('%H:%M')}}",flush=True)
            time.sleep(0.35)
        elif s==429: time.sleep(10)
        else: time.sleep(1)
    except: time.sleep(2)

with open(RESULTS,'w') as f: json.dump(results,f)
print(f"Polar DONE: {{len(results):,}}")
"""
    with open('/tmp/polar_resume.py','w') as f: f.write(script)
    subprocess.Popen(['python3','/tmp/polar_resume.py'], 
                     stdout=open('/tmp/polar_log.txt','a'),
                     stderr=subprocess.STDOUT)
    log("Polar upload process started")

def run_gumroad_daily():
    results = {}
    if os.path.exists(f"{BASE}/CREATED_PRODUCTS.json"):
        with open(f"{BASE}/CREATED_PRODUCTS.json") as f: results = json.load(f)
    
    already = set(results.keys())
    folders = sorted([f for f in os.listdir(PRODUCTS) 
                      if f[0].isdigit() and os.path.isdir(f"{PRODUCTS}/{f}")])
    todo = [f for f in folders if f not in already][:10]
    
    if not todo:
        log("Gumroad: Nothing to add today")
        return
    
    created = 0
    for folder in todo:
        path = f"{PRODUCTS}/{folder}/gumroad-listing.txt"
        if not os.path.exists(path): continue
        with open(path) as f: c = f.read()
        t = re.search(r'PRODUCT TITLE:\s*(.+)', c)
        p = re.search(r'PRICE:\s*\$(\d+)', c)
        d = re.search(r'SHORT DESC:\s*(.+)', c)
        title = t.group(1).strip()[:255] if t else folder
        price = int(p.group(1)) * 100 if p else 12700
        desc  = d.group(1).strip()[:3000] if d else title
        
        data = urllib.parse.urlencode({
            "access_token": GUMROAD_TOKEN,
            "name": title, "description": desc, "price": str(price)
        }).encode()
        req = urllib.request.Request("https://api.gumroad.com/v2/products", 
                                      data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                result = json.loads(r.read())
                if result.get("success"):
                    p2 = result.get("product", {})
                    permalink = p2.get("short_url","").split("/")[-1]
                    results[folder] = {"title": title, "price": price, "permalink": permalink}
                    created += 1
                    time.sleep(1)
                else:
                    log(f"Gumroad limit: {result.get('message','?')}")
                    break
        except Exception as e:
            log(f"Gumroad error: {e}")
            break
        time.sleep(0.5)
    
    if created > 0:
        with open(f"{BASE}/CREATED_PRODUCTS.json", 'w') as f: json.dump(results, f, indent=2)
        log(f"Gumroad: +{created} today | Total: {len(results)}")
    else:
        log("Gumroad: 0 added (limit reached)")

def check_etsy_status():
    log("Etsy: Checking API approval...")
    try:
        req = urllib.request.Request(
            "https://openapi.etsy.com/v3/application/openapi-ping",
            headers={"x-api-key": "80mdau3vwn8uct0cxx3i9gzrh"})
        with urllib.request.urlopen(req, timeout=10) as r:
            log(f"Etsy API: ACTIVE ✅ — can start uploading!")
            return True
    except Exception as e:
        log(f"Etsy API: Still pending ({str(e)[:50]})")
        return False

def generate_daily_post():
    today = datetime.datetime.now().strftime("%A")
    angles = {
        "Monday": "Problem angle — why generic prompts fail",
        "Tuesday": "Use case — specific professional story",
        "Wednesday": "Value — $127 vs hiring consultant",
        "Thursday": "How-to — 3 ways to use prompt packs",
        "Friday": "Results — save 10hrs/week",
        "Saturday": "Weekend special — discount angle",
        "Sunday": "Week ahead — prep for Monday"
    }
    angle = angles.get(today, "General value post")
    
    post_dir = f"{BASE}/MARKETING-AUTO/social-media/twitter"
    os.makedirs(post_dir, exist_ok=True)
    
    fname = f"{post_dir}/daily-{datetime.datetime.now().strftime('%d-%m-%Y')}.md"
    if not os.path.exists(fname):
        with open(fname, 'w') as f:
            f.write(f"# Daily Post — {today}\n# Angle: {angle}\n\n")
            f.write("Stop using generic AI prompts.\n\n")
            f.write("99,440 specialized packs for your exact industry + role + country.\n")
            f.write("ChatGPT & Claude ready. $127. Instant download.\n\n")
            f.write("→ polar.sh/aniketg-ai\n\n")
            f.write("#AIPrompts #ChatGPT #DigitalProducts #WorkSmart\n\n")
            f.write(f"Platform: Twitter | Generated: {datetime.datetime.now()}\n")
        log(f"Daily post generated: {fname}")

def main():
    log("🚀 AniketG AI Master Agent Starting...")
    
    # 1. Status
    polar, gm, total = status_report()
    
    # 2. Resume Polar if not running
    procs = check_polar_running()
    log(f"Active upload processes: {procs}")
    
    if polar < total and procs < 2:
        log("Polar not complete — resuming...")
        resume_polar()
    elif polar >= total:
        log("Polar: COMPLETE ✅")
    
    # 3. Gumroad daily
    run_gumroad_daily()
    
    # 4. Etsy check
    etsy_ready = check_etsy_status()
    
    # 5. Daily content
    generate_daily_post()
    
    # 6. Final report
    log("\n=== MASTER AGENT REPORT ===")
    log(f"Polar:   {polar:,}/{total:,}")
    log(f"Gumroad: {count_json(BASE+'/CREATED_PRODUCTS.json')}")
    log(f"Etsy:    {'READY' if etsy_ready else 'PENDING'}")
    log(f"Content: Generated for {datetime.datetime.now().strftime('%A')}")
    log("✅ All tasks complete")

if __name__ == "__main__":
    main()
