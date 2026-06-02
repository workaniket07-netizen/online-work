#!/usr/bin/env python3
"""
Higgsfield Unlimited Automation
- Uses real Chrome browser (separate profile)
- Unlimited toggle respected = 0 credits
- Login once, then fully automatic
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

# ── Config ──────────────────────────────────────────────────────────────────
PROJECTS_DIR  = Path.home() / "Desktop/online-work-site/projects"
LOGO_PATH     = Path.home() / "Desktop/online-work-site/AniketG_Ai_logo.png"
PROFILE_DIR   = Path.home() / "higgsfield-chrome-profile"
SESSION_FILE  = Path.home() / "higgsfield-session.json"
DONE_FILE     = Path.home() / "Desktop/online-work-site/.hf_done.json"
LOGO_RATIO    = 0.09
MARGIN        = 22

# ── Model + quality ──────────────────────────────────────────────────────────
HIGGSFIELD_MODEL  = "nano-banana-pro"
HIGGSFIELD_URL    = f"https://higgsfield.ai/ai/image?model={HIGGSFIELD_MODEL}"
IMAGE_RESOLUTION  = "4k"   # 1k | 2k | 4k — forced in every API request

# Appended to every prompt — forces cinematic, premium-ad quality output
QUALITY_SUFFIX = (
    ", shot on Phase One IQ4 150MP camera, 85mm f/1.4 lens, "
    "professional commercial advertising photography, "
    "cinematic dramatic lighting, award-winning editorial, "
    "ultra-sharp, photorealistic, 8K resolution, "
    "published in Vogue/Harper's Bazaar/Forbes luxury magazine"
)

# ── Topics + Prompts ─────────────────────────────────────────────────────────
TOPICS = [
    {
        "slug": "ice-cream-brands-ad",
        "name": "Ice Cream Brands",
        "posts": [
            "Award-winning artisan ice cream brand full-page magazine ad. Haagen-Dazs aesthetic. Vibrant colorful gelato scoops in luxury waffle cone on white marble, golden spoon, floral accents. Headline 'TASTE THE BLISS' in elegant serif above product. NATURAL FLAVORS · HANDCRAFTED DAILY · PREMIUM DAIRY. Pastel tones, premium editorial. Text never touches product.",
            "Premium ice cream brand ad. Ben and Jerry aesthetic. Three artisan scoops of gelato on marble surface, dramatic soft diffused light from above, mint leaves garnish. 'CRAFTED FOR JOY' serif headline in clear negative space above. Pastel pink and cream palette. Luxurious lifestyle photography.",
            "Luxury gelato shop ad. Soft serve swirl in premium waffle cone against creamy beige gradient, delicate gold leaf flakes. 'EVERY SCOOP A MOMENT' headline in refined typography above product scene. Minimalist editorial. Text never touches product.",
            "Ice cream brand social ad. Overhead flatlay of assorted gelato scoops on marble with berries, pistachios, waffle pieces. 'FLAVORS WORTH LIVING FOR' headline in clear space above scene. Warm pastel tones, editorial magazine quality."
        ],
        "thumb": "Luxury ice cream brand landscape thumbnail. Colorful gelato scoops on marble, golden accents. 'TASTE THE BLISS' headline in clear space above product. Pastel premium editorial."
    },
    {
        "slug": "cafe-advertisement",
        "name": "Cafe Advertisement",
        "posts": [
            "Award-winning specialty cafe full-page magazine ad. Blue Bottle Coffee aesthetic. Perfect latte art in handcrafted ceramic cup on oak table, soft morning window light, croissant beside. 'YOUR PERFECT CUP' in warm serif headline in negative space above cup. SINGLE ORIGIN · EXPERT BARISTAS · FRESH PASTRIES. Warm amber tones.",
            "Premium cafe ad. Third-wave coffee aesthetic. Close-up espresso pour into glass, crema swirling, dramatic top-down angle. 'BREWED TO PERFECTION' serif headline in clear space beside scene. Dark moody tones, editorial.",
            "Artisan cafe lifestyle ad. Barista crafting latte art with focus on skilled hands, bokeh warm cafe background. 'WHERE COFFEE BECOMES ART' headline in upper negative space. Warm golden hour tones.",
            "Specialty coffee shop ad. Flat lay of coffee cups, beans, croissant on marble. 'START YOUR DAY RIGHT' headline in clear space above scene. Clean lifestyle editorial."
        ],
        "thumb": "Specialty cafe landscape thumbnail. Latte art ceramic cup, warm cafe ambiance. 'YOUR PERFECT CUP' headline in clear space above. Warm amber editorial."
    },
    {
        "slug": "watch-brands-advertisement",
        "name": "Watch Brands",
        "posts": [
            "Luxury watch brand full-page magazine ad. Rolex aesthetic. Swiss chronograph on dark wet black marble, dramatic chiaroscuro side lighting, smoke wisps. 'MASTER OF TIME' in gold serif in clear space above watch. SWISS MOVEMENT · SAPPHIRE CRYSTAL · WATER RESISTANT. Text never touches watch.",
            "Premium watch brand ad. Patek Philippe aesthetic. Skeleton watch movement visible, placed on dark glass, dramatic spotlight from above. 'CRAFTED FOR ETERNITY' elegant headline in negative space beside watch. Dark luxury editorial.",
            "Luxury timepiece lifestyle ad. Watch flat on slate surface, single dramatic side light revealing dial detail. 'PRECISION ELEVATED' headline in upper clear space. Deep charcoal tones, understated luxury.",
            "Premium watch ad. Close-up of watch crown and case detail on brushed metal surface, macro photography. 'ENGINEERED TO PERFECTION' headline in clear space above. Monochrome editorial quality."
        ],
        "thumb": "Luxury watch brand landscape thumbnail. Chronograph on dark marble, dramatic lighting. 'MASTER OF TIME' in gold serif above. Premium editorial."
    },
    {
        "slug": "luxury-hotel-advertisement",
        "name": "Luxury Hotel",
        "posts": [
            "Five-star luxury hotel full-page ad. Four Seasons aesthetic. Infinity pool overlooking ocean at golden sunset, cabana chairs, tropical palms. 'YOUR ESCAPE AWAITS' serif headline in clear sky above scene. PRIVATE VILLAS · WORLD-CLASS SPA · MICHELIN DINING. Warm luxury tones.",
            "Luxury resort hotel ad. Aman aesthetic. Elegant suite interior, floor-to-ceiling windows, mountain view, fresh orchids on nightstand. 'LIVE WITHOUT LIMITS' headline in clear space above window. Soft cream and gold palette.",
            "Premium hotel lifestyle ad. Butler presenting champagne on private terrace with city skyline at dusk. 'REDEFINE LUXURY' headline in upper clear zone. Rich evening tones, aspirational editorial.",
            "Luxury hotel spa ad. Serene treatment room with candles, orchids, stone bath, soft natural light. 'RESTORE YOUR SOUL' headline in clear space above scene. Soft neutral tones, wellness editorial."
        ],
        "thumb": "Luxury hotel landscape thumbnail. Infinity pool at golden sunset, tropical setting. 'YOUR ESCAPE AWAITS' headline in clear sky. Warm premium editorial."
    },
    {
        "slug": "perfume-fragrance-ad",
        "name": "Perfume Fragrance",
        "posts": [
            "Luxury perfume brand full-page magazine ad. Chanel No.5 aesthetic. Crystal perfume bottle on black marble, dramatic single spotlight, smoke tendrils. 'THE SCENT OF DESIRE' serif headline in clear dark space above bottle. EXCLUSIVE · HANDCRAFTED · TIMELESS. Gold and black palette.",
            "Premium fragrance ad. Dior Sauvage aesthetic. Glass perfume flacon on rock in misty forest scene, blue hour light. 'WILD. UNTAMED. YOURS.' headline in clear space above. Moody masculine editorial.",
            "Niche perfume brand ad. Minimalist glass bottle on white marble, single rose petal beside, soft diffused light. 'PURE ESSENCE' headline in clear space above. All-white editorial, ultra-luxury aesthetic.",
            "Luxury fragrance lifestyle ad. Perfume bottle on vanity table, blurred woman applying fragrance in background. 'YOUR SIGNATURE SCENT' headline in clear upper space. Warm boudoir lighting, feminine editorial."
        ],
        "thumb": "Luxury perfume landscape thumbnail. Crystal bottle on marble, dramatic spotlight. 'THE SCENT OF DESIRE' headline in clear dark space. Gold editorial."
    },
    {
        "slug": "sneakers-sports-shoes-ad",
        "name": "Sneakers Sports Shoes",
        "posts": [
            "Premium sneaker brand full-page ad. Nike Air aesthetic. Single sneaker floating mid-air on pure white background, dramatic under-lighting, motion blur laces. 'BORN TO RUN' bold sans-serif headline in clear space above shoe. PERFORMANCE · STYLE · COMFORT. Clean white editorial.",
            "Luxury sports shoe ad. Adidas Ultraboost aesthetic. Sneaker on wet urban concrete at night, neon reflections, rain drops. 'OWN THE NIGHT' headline in clear upper space. Dark urban editorial.",
            "Premium sneaker lifestyle ad. Feet in clean white sneakers walking on marble floor, low angle shot. 'EVERY STEP MATTERS' headline in clear space above feet. Minimal white tones.",
            "Sneaker brand editorial ad. Side profile of sneaker on black surface, dramatic spotlight revealing texture and sole detail. 'CRAFTED FOR CHAMPIONS' headline in clear space above. Monochrome luxury."
        ],
        "thumb": "Premium sneaker landscape thumbnail. Floating shoe on white background, dramatic lighting. 'BORN TO RUN' headline in clear space above. Clean editorial."
    },
    {
        "slug": "luxury-car-advertisement",
        "name": "Luxury Car",
        "posts": [
            "Luxury car brand full-page magazine ad. Rolls-Royce aesthetic. Silver sedan on empty wet coastal road at golden hour, dramatic clouds behind. 'BEYOND EXTRAORDINARY' serif headline in clear sky above car. HANDCRAFTED · BESPOKE · ICONIC. Rich warm tones. Text never on car.",
            "Premium sports car ad. Porsche aesthetic. Red sports car on mountain road curve, motion blur background. 'PURE PERFORMANCE' headline in clear sky zone. Dynamic editorial photography.",
            "Luxury electric car ad. Tesla aesthetic. Black EV on rooftop parking at city twilight, city lights below. 'THE FUTURE IS NOW' headline in clear dark sky. Modern premium editorial.",
            "Premium car interior ad. Steering wheel and dashboard detail, hand-stitched leather, ambient lighting. 'CRAFTED FOR YOU' headline in clear dark space. Intimate luxury editorial."
        ],
        "thumb": "Luxury car landscape thumbnail. Silver sedan on coastal road at golden hour. 'BEYOND EXTRAORDINARY' headline in clear sky. Premium editorial."
    },
    {
        "slug": "jewelry-diamond-advertisement",
        "name": "Jewelry Diamond",
        "posts": [
            "Luxury jewelry brand full-page ad. Cartier aesthetic. Diamond ring on black velvet, single spot from above, sparkles. 'FOREVER YOURS' elegant serif headline in clear dark space above ring. CONFLICT-FREE · CERTIFIED · HANDSET. Gold and black. Text never touches jewelry.",
            "Premium diamond brand ad. Tiffany aesthetic. Solitaire ring in blue box on white marble, soft window light. 'THE PERFECT MOMENT' headline in clear space above. Clean white and blue editorial.",
            "Luxury necklace ad. Diamond pendant on woman's neck, soft focus shoulders, dramatic studio light. 'WEAR YOUR STORY' headline in clear upper zone. Elegant portrait editorial.",
            "Premium jewelry lifestyle ad. Diamond bracelet flat on white satin cloth, scattered rose petals. 'BRILLIANCE DEFINED' headline in clear space above. Soft white editorial."
        ],
        "thumb": "Luxury jewelry landscape thumbnail. Diamond ring on black velvet, sparkles. 'FOREVER YOURS' headline in clear dark space. Cartier-level editorial."
    },
    {
        "slug": "smartphone-tech-advertisement",
        "name": "Smartphone Tech",
        "posts": [
            "Premium smartphone brand full-page ad. Apple iPhone aesthetic. Sleek phone on black glass surface, dramatic edge lighting revealing thin profile. 'THE FUTURE IN YOUR HAND' headline in clear dark space above. TITANIUM · PRO CAMERA · ALL-DAY BATTERY. Ultra-minimal editorial.",
            "Flagship smartphone ad. Samsung aesthetic. Phone floating on gradient purple-blue background, screen showing vibrant wallpaper. 'SEE MORE. DO MORE.' headline in clear space above. Premium tech editorial.",
            "Smartphone lifestyle ad. Phone on marble desk beside coffee cup, glasses, editorial magazine. 'DESIGNED FOR LIFE' headline in clear space above scene. Warm lifestyle tones.",
            "Premium smartphone camera ad. Close-up of phone camera system on dark background, lens glass refracting light. 'CAPTURE EVERYTHING' headline in clear dark space above. Macro product editorial."
        ],
        "thumb": "Premium smartphone landscape thumbnail. Sleek phone on dark surface, edge lighting. 'THE FUTURE IN YOUR HAND' headline in clear space. Tech editorial."
    },
    {
        "slug": "skincare-beauty-advertisement",
        "name": "Skincare Beauty",
        "posts": [
            "Luxury skincare brand full-page ad. La Mer aesthetic. Elegant cream jar on white marble, single orchid beside, soft diffused light. 'TRANSFORM YOUR SKIN' serif headline in clear space above jar. CLINICALLY PROVEN · NATURAL EXTRACTS · DERMATOLOGIST TESTED. Cream white tones.",
            "Premium serum brand ad. SK-II aesthetic. Glass dropper bottle on pale pink background, serum drop mid-fall from dropper. 'PURE RADIANCE' headline in clear space above. Minimal luxury editorial.",
            "Luxury face cream ad. Overhead flatlay of skincare products on marble with jasmine flowers, pearl-like drops. 'YOUR RITUAL BEGINS HERE' headline in clear space above. Soft editorial.",
            "Premium skincare lifestyle ad. Woman's glowing skin close-up, soft studio light. Product bottle in clear lower zone. 'GLOW FROM WITHIN' headline in clear upper space. Beauty editorial."
        ],
        "thumb": "Luxury skincare landscape thumbnail. Cream jar on white marble, orchid. 'TRANSFORM YOUR SKIN' headline in clear space. Premium beauty editorial."
    },
    {
        "slug": "whiskey-spirits-advertisement",
        "name": "Whiskey Spirits",
        "posts": [
            "Luxury whiskey brand full-page ad. Macallan aesthetic. Amber whiskey in crystal glass on dark oak barrel, moody fireplace light, smoke. 'AGED TO PERFECTION' serif headline in clear dark space above. 18 YEAR AGED · SINGLE MALT · HAND BOTTLED. Deep amber tones.",
            "Premium bourbon ad. Woodford Reserve aesthetic. Bottle on distillery barrel, golden sunlight through warehouse slats. 'CRAFTED WITH TIME' headline in clear space above bottle. Warm amber editorial.",
            "Luxury whiskey lifestyle ad. Two crystal glasses on leather lounge table, ice sphere in each, blurred fireplace behind. 'THE FINER THINGS' headline in clear upper zone. Dark masculine editorial.",
            "Premium spirits brand ad. Close-up of pouring whiskey into crystal glass, amber liquid, dramatic backlight. 'PURE CHARACTER' headline in clear dark space. Macro editorial quality."
        ],
        "thumb": "Luxury whiskey landscape thumbnail. Crystal glass on dark oak, fireplace light. 'AGED TO PERFECTION' headline in clear space. Rich amber editorial."
    },
    {
        "slug": "gym-fitness-advertisement",
        "name": "Gym Fitness",
        "posts": [
            "Premium gym brand full-page ad. Equinox aesthetic. State-of-the-art gym floor with equipment at blue dawn light, empty and serene. 'IT'S NOT FITNESS. IT'S LIFE.' bold headline in clear dark space above. EXPERT TRAINERS · PREMIUM EQUIPMENT · 24/7. Dark cinematic tones.",
            "Fitness brand lifestyle ad. Athlete doing pull-ups, dramatic backlit silhouette, industrial gym setting. 'PUSH YOUR LIMITS' headline in clear upper zone. High contrast black and white editorial.",
            "Premium supplement brand ad. Protein powder container on black marble, shaker bottle beside. 'FUEL YOUR GREATNESS' headline in clear dark space above. Dark premium editorial.",
            "Fitness lifestyle ad. Running shoes, protein bar, headphones flat lay on gym floor. 'EVERY REP COUNTS' headline in clear space above. Clean editorial layout."
        ],
        "thumb": "Premium gym landscape thumbnail. Empty gym at dawn, dramatic equipment rows. 'IT'S NOT FITNESS. IT'S LIFE.' headline in clear space. Dark editorial."
    },
    {
        "slug": "real-estate-luxury-homes-ad",
        "name": "Real Estate Luxury Homes",
        "posts": [
            "Luxury real estate full-page ad. Modern glass mansion at twilight, infinity pool in foreground, city valley below. 'LIVE ABOVE IT ALL' serif headline in clear sky above. PRIVATE · SECURE · ICONIC. Deep blue hour tones. Text never touches building.",
            "Premium property ad. Grand colonial villa exterior, sweeping driveway, manicured gardens, golden hour sun. 'YOUR LEGACY BEGINS HERE' headline in clear sky zone above. Warm prestigious editorial.",
            "Luxury penthouse ad. Interior shot through floor-to-ceiling windows, city skyline at dusk visible, elegant furniture. 'ELEVATED LIVING' headline in clear sky outside window. Premium editorial.",
            "Luxury home lifestyle ad. Architect-designed kitchen, Italian marble island, chef's range, pendant lighting. 'DESIGNED FOR THE EXCEPTIONAL' headline in clear space above. Interior editorial."
        ],
        "thumb": "Luxury real estate landscape thumbnail. Glass mansion at twilight, infinity pool. 'LIVE ABOVE IT ALL' headline in clear sky. Blue hour editorial."
    },
    {
        "slug": "chocolate-brand-advertisement",
        "name": "Chocolate Brand",
        "posts": [
            "Luxury chocolate brand full-page ad. Godiva aesthetic. Dark chocolate pralines in gold box on black velvet, dramatic spot lighting, cocoa dust. 'PURE INDULGENCE' serif headline in clear dark space above. SINGLE ORIGIN · HANDCRAFTED · AWARD-WINNING. Dark gold palette.",
            "Premium chocolate bar ad. Lindt aesthetic. Broken chocolate bar revealing glossy interior, on white marble, cocoa bean beside. 'CRAFTED FOR PLEASURE' headline in clear space above. Clean editorial.",
            "Luxury hot chocolate ad. Ceramic mug of rich hot chocolate with cream rosette, marshmallows, on rustic oak table, soft window light. 'WARMTH IN EVERY SIP' headline in clear space above. Cozy premium tones.",
            "Artisan chocolate lifestyle ad. Chocolatier hands with dark chocolate truffle, bokeh kitchen behind. 'MADE WITH PASSION' headline in clear upper zone. Warm artisan editorial."
        ],
        "thumb": "Luxury chocolate landscape thumbnail. Gold praline box on black velvet, spotlit. 'PURE INDULGENCE' headline in clear space. Gold editorial."
    },
    {
        "slug": "energy-drink-advertisement",
        "name": "Energy Drink",
        "posts": [
            "Premium energy drink full-page ad. Red Bull aesthetic. Sleek can in mid-air on electric blue background, lightning bolts radiating. 'UNLEASH YOUR ENERGY' bold headline in clear space above. ZERO SUGAR · NATURAL CAFFEINE · ELECTROLYTES. Electric blue tones.",
            "Premium energy drink lifestyle ad. Athlete opening can post-workout, stadium lights behind, sweat, dramatic backlight. 'POWER YOUR PERFORMANCE' headline in clear upper sky zone. Cinematic sports editorial.",
            "Energy drink product ad. Can on black reflective surface, ice condensation, neon color splash. 'FEEL ALIVE' headline in clear dark space above. Vibrant nightlife editorial.",
            "Energy drink brand ad. Flat lay of can, pre-workout gear, earphones on dark gym floor. 'FUEL THE GRIND' headline in clear space above. Dark athletic editorial."
        ],
        "thumb": "Energy drink landscape thumbnail. Sleek can on electric blue, lightning bolts. 'UNLEASH YOUR ENERGY' headline in clear space. Dynamic editorial."
    },
    {
        "slug": "hair-care-advertisement",
        "name": "Hair Care",
        "posts": [
            "Luxury hair care brand full-page ad. Kerastase aesthetic. Elegant shampoo and conditioner bottles on white marble, fresh jasmine sprigs. 'HAIR TRANSFORMED' serif headline in clear space above. SALON-GRADE · NATURAL EXTRACTS · CLINICALLY TESTED. Cream editorial.",
            "Premium hair serum ad. Gold glass dropper bottle on black background, serum drop mid-fall. 'LIQUID GOLD FOR YOUR HAIR' headline in clear space above. Dark luxury editorial.",
            "Hair care lifestyle ad. Woman with flowing shiny hair, soft studio wind, white background. Product in lower clear zone. 'YOUR CROWNING GLORY' headline in clear upper space. Beauty editorial.",
            "Premium hair mask product ad. Jar and brush on bathroom vanity with eucalyptus branches. 'RESTORE. REPAIR. REVIVE.' headline in clear space above. Spa-like editorial tones."
        ],
        "thumb": "Luxury hair care landscape thumbnail. Elegant bottles on white marble, jasmine. 'HAIR TRANSFORMED' headline in clear space. Premium editorial."
    },
    {
        "slug": "burger-restaurant-advertisement",
        "name": "Burger Restaurant",
        "posts": [
            "Premium burger restaurant full-page ad. Shake Shack aesthetic. Gourmet burger stacked tall on wooden board, dramatic top-light, lettuce and sauce visible. 'BUILT FOR LEGENDS' bold serif headline in clear dark space above burger. FRESH BEEF · BRIOCHE BUN · HOUSE SAUCE. Dark moody tones.",
            "Artisan burger brand ad. Smash burger on butcher paper, dramatic overhead lighting, sesame bun, melted cheese cascade. 'CRAVE THE CRAFT' headline in clear space above. Dark editorial.",
            "Premium burger lifestyle ad. Burger and fries in paper bag on diner table, retro vinyl record poster on wall behind. 'OLD SCHOOL FLAVOR' headline in clear upper zone. Warm vintage tones.",
            "Gourmet burger brand ad. Cross-section of perfect burger showing layers, macro shot, dramatic backlight. 'EVERY LAYER TELLS A STORY' headline in clear space above. Editorial food photography."
        ],
        "thumb": "Premium burger restaurant landscape thumbnail. Gourmet burger on wooden board, dramatic light. 'BUILT FOR LEGENDS' headline in clear space. Dark editorial."
    },
    {
        "slug": "pizza-advertisement",
        "name": "Pizza Brand",
        "posts": [
            "Premium pizza brand full-page ad. Neapolitan aesthetic. Wood-fired pizza in brick oven, flame visible, bubbling mozzarella, charred crust. 'BORN IN NAPLES' italic serif headline in clear space above. 100% ITALIAN · WOOD FIRED · FRESH DAILY. Warm dark rustic tones.",
            "Artisan pizza brand ad. Perfect Margherita flatlay on dark slate, basil leaves, buffalo mozzarella, tomato sauce drizzle. 'SIMPLY PERFECT' headline in clear space above. Editorial food photography.",
            "Pizza lifestyle ad. Pizza being sliced at rustic wooden table, cheese pull mid-slice, candlelight evening. 'SHARE THE MOMENT' headline in upper clear zone. Warm editorial.",
            "Gourmet pizza brand ad. Aerial view of truffle mushroom pizza in cast iron pan, parmesan shaving landing. 'ELEVATED CLASSICS' headline in clear space above. Premium editorial."
        ],
        "thumb": "Premium pizza landscape thumbnail. Wood-fired pizza in brick oven, flame. 'BORN IN NAPLES' headline in clear space. Warm rustic editorial."
    },
    {
        "slug": "sushi-restaurant-advertisement",
        "name": "Sushi Restaurant",
        "posts": [
            "Premium sushi restaurant full-page ad. Nobu aesthetic. Omakase selection on black slate, each piece perfect, dramatic overhead spot. 'ART ON A PLATE' elegant serif headline in clear dark space above. OMAKASE · SUSTAINABLE · CRAFTED DAILY. Dark editorial.",
            "Luxury sushi brand ad. Chef hands placing nigiri with precision, wooden hinoki counter, bokeh restaurant behind. 'MASTER THE MOMENT' headline in clear upper zone. Editorial restaurant photography.",
            "Sushi restaurant lifestyle ad. Dragon roll platter on dark slate, pickled ginger, wasabi, soy dish beside. 'EXPERIENCE THE CRAFT' headline in clear space above. Moody Japanese editorial.",
            "Premium sushi ad. Close-up of tuna sashimi cut, glistening, on cedar wood, micro herbs garnish. 'PURE. FRESH. PERFECT.' headline in clear dark space above. Macro food editorial."
        ],
        "thumb": "Premium sushi restaurant landscape thumbnail. Omakase selection on black slate, spotlit. 'ART ON A PLATE' headline in clear space. Dark editorial."
    },
    {
        "slug": "restaurant-fine-dining-ad",
        "name": "Fine Dining Restaurant",
        "posts": [
            "Fine dining restaurant full-page ad. Noma aesthetic. Michelin-starred plate with microgreens, foam, single protein, white porcelain on dark table. 'WHERE FOOD BECOMES ART' serif headline in clear dark space above. TWO MICHELIN STARS · SEASONAL MENU · RESERVATIONS REQUIRED.",
            "Premium restaurant brand ad. Le Bernardin aesthetic. Perfectly plated sea bass, beurre blanc sauce, micro herbs, white porcelain. 'CUISINE AT ITS FINEST' headline in clear space above. Elegant editorial.",
            "Fine dining lifestyle ad. Sommelier pouring wine at candlelit table, couple in background blurred, champagne flutes. 'AN EVENING TO REMEMBER' headline in clear upper zone. Warm evening editorial.",
            "Restaurant interior ad. Empty Michelin-starred dining room, dramatic pendant lighting, white tablecloths, tulips. 'YOUR TABLE IS WAITING' headline in clear upper space. Aspirational editorial."
        ],
        "thumb": "Fine dining restaurant landscape thumbnail. Michelin-starred plate, white porcelain, dark table. 'WHERE FOOD BECOMES ART' headline in clear space. Elegant editorial."
    },
    {
        "slug": "fashion-clothing-advertisement",
        "name": "Fashion Clothing",
        "posts": [
            "Luxury fashion brand full-page ad. Prada aesthetic. Elegant structured blazer on white mannequin torso, stark white studio, dramatic single side light. 'DRESSED FOR POWER' serif headline in clear space above. ITALIAN WOOL · BESPOKE FIT · TIMELESS DESIGN. Monochrome editorial.",
            "Premium clothing brand ad. Minimal fashion editorial. Linen trousers and silk shirt flat lay on warm oak floor, editorial arrangement. 'EFFORTLESS ELEGANCE' headline in clear space above. Warm neutral tones.",
            "Luxury outerwear ad. Cashmere overcoat on coat stand against white wall, soft natural light from window. 'WRAP YOURSELF IN LUXURY' headline in clear space above. Minimal editorial.",
            "Premium fashion lifestyle ad. Fashion accessories flat lay: leather gloves, silk scarf, sunglasses on marble. 'THE DETAILS DEFINE YOU' headline in clear space above. Luxury editorial."
        ],
        "thumb": "Luxury fashion landscape thumbnail. Structured blazer on white studio, dramatic light. 'DRESSED FOR POWER' headline in clear space. Monochrome editorial."
    },
    {
        "slug": "wine-advertisement",
        "name": "Wine Brand",
        "posts": [
            "Premium wine brand full-page ad. Opus One aesthetic. Single red wine bottle on stone cellar shelf, dramatic spotlit, aged labels visible. 'BORN FROM THE VINE' serif headline in clear dark space above. ESTATE GROWN · BARREL AGED · VINTAGE RESERVE. Deep burgundy tones.",
            "Luxury wine lifestyle ad. Two crystal wine glasses with red wine catching golden light, vineyard sunset behind. 'POUR THE MOMENT' headline in clear sky above. Warm vineyard editorial.",
            "Premium white wine ad. Chardonnay in crystal glass on marble with fresh grapes and cheese. 'CRISP. ELEGANT. PERFECT.' headline in clear space above. Soft daylight editorial.",
            "Wine brand heritage ad. Vintner hands examining red wine in barrel hall, rows of barrels behind, warm cellar light. 'CRAFTED SINCE 1892' headline in clear upper zone. Heritage editorial."
        ],
        "thumb": "Premium wine landscape thumbnail. Single bottle on stone cellar, spotlit. 'BORN FROM THE VINE' headline in clear dark space. Burgundy editorial."
    },
    {
        "slug": "beer-craft-advertisement",
        "name": "Craft Beer",
        "posts": [
            "Premium craft beer full-page ad. Brooklyn Brewery aesthetic. Pint glass with perfect golden lager, foam head, cold condensation, dark bar counter. 'RAISED WITH CRAFT' bold headline in clear dark space above glass. SMALL BATCH · HOP FORWARD · EST. 1988.",
            "Artisan craft beer brand ad. Four-pack cans with illustrated label, on grass with wildflowers. 'FOR THE FREE-SPIRITED' headline in clear space above. Warm outdoor editorial.",
            "Craft beer lifestyle ad. Two friends clinking pint glasses at rooftop bar, city skyline behind at dusk. 'SHARE WHAT MATTERS' headline in clear sky zone. Warm social editorial.",
            "Craft brewery brand ad. Copper brewing tanks in artisan brewery, steam, golden light. 'WHERE GREAT BEER BEGINS' headline in clear space above. Industrial editorial."
        ],
        "thumb": "Craft beer landscape thumbnail. Perfect pint glass on dark bar, condensation. 'RAISED WITH CRAFT' headline in clear space. Dark editorial."
    },
    {
        "slug": "sunglasses-eyewear-ad",
        "name": "Sunglasses Eyewear",
        "posts": [
            "Luxury eyewear brand full-page ad. Ray-Ban aesthetic. Premium sunglasses on white marble, dramatic side light casting lens shadow. 'SEE THE WORLD DIFFERENTLY' serif headline in clear space above. HANDCRAFTED FRAMES · UV PROTECTION · ITALIAN MADE.",
            "Premium sunglasses lifestyle ad. Sunglasses resting on sun-kissed nose of model on rooftop, city skyline blurred behind. 'MADE FOR MOMENTS' headline in clear sky above. Summer editorial.",
            "Luxury eyewear product ad. Gold aviator sunglasses flat on black velvet, light refracting through lenses. 'PURE STYLE' headline in clear dark space above. Dark luxury editorial.",
            "Premium glasses brand ad. Collection of four frames arranged on marble, clean editorial. 'FIND YOUR FRAME' headline in clear space above. Clean minimal editorial."
        ],
        "thumb": "Luxury sunglasses landscape thumbnail. Premium shades on marble, shadow play. 'SEE THE WORLD DIFFERENTLY' headline in clear space. Clean editorial."
    },
    {
        "slug": "bakery-advertisement",
        "name": "Bakery Brand",
        "posts": [
            "Premium artisan bakery full-page ad. Dominique Ansel aesthetic. Perfect croissant on white linen, flaky layers visible, dramatic morning light, butter gleam. 'BAKED WITH LOVE' serif headline in clear space above. STONE MILLED · SLOW FERMENTED · DAILY FRESH.",
            "Luxury bakery brand ad. Sourdough loaf on dark slate, flour dusting, scored top, rustic bread knife. 'BREAD AS IT SHOULD BE' headline in clear space above. Dark artisan editorial.",
            "Artisan patisserie ad. Showstopper cake with mirror glaze, edible gold, berries, on marble cake stand. 'CRAFTED FOR CELEBRATIONS' headline in clear space above. Premium editorial.",
            "Bakery lifestyle ad. Hands pulling fresh cinnamon roll apart, steam, icing drizzle, warm morning kitchen. 'MORNINGS MADE BETTER' headline in clear upper zone. Warm cozy editorial."
        ],
        "thumb": "Premium bakery landscape thumbnail. Perfect croissant on white linen, morning light. 'BAKED WITH LOVE' headline in clear space. Warm editorial."
    },
    {
        "slug": "tea-brand-advertisement",
        "name": "Tea Brand",
        "posts": [
            "Luxury tea brand full-page ad. Fortnum and Mason aesthetic. Elegant teapot and fine bone china cup on antique table, soft afternoon light. 'THE ART OF TEA' serif headline in clear space above. SINGLE ESTATE · HAND PICKED · BLENDED SINCE 1707.",
            "Premium matcha brand ad. Ceremonial matcha in chawan bowl, bamboo whisk beside, on Japanese stone surface, soft light. 'ZEN IN EVERY SIP' headline in clear space above. Minimal Japanese editorial.",
            "Luxury herbal tea ad. Glass teapot with blooming flower tea submerged, chamomile, on white marble. 'BLOOM IN EVERY CUP' headline in clear space above. Soft botanical editorial.",
            "Premium tea lifestyle ad. Morning tea ritual: cup, saucer, open book, reading glasses on oak beside window. 'YOUR MORNING RITUAL' headline in clear upper space. Warm lifestyle editorial."
        ],
        "thumb": "Luxury tea landscape thumbnail. Elegant teapot and cup, antique table, afternoon light. 'THE ART OF TEA' headline in clear space. Refined editorial."
    },
    {
        "slug": "juice-health-drink-ad",
        "name": "Juice Health Drink",
        "posts": [
            "Premium cold-press juice brand full-page ad. Pressed Juicery aesthetic. Three vivid juice bottles — green, orange, red — on white marble, fresh produce around each. 'NATURE BOTTLED' serif headline in clear space above. 100% COLD-PRESSED · NO ADDED SUGAR · RAW.",
            "Luxury juice brand ad. Single green smoothie in crystal glass, spinach, apple slices, mint arranged beside on marble. 'CLEAN FROM THE INSIDE' headline in clear space above. Bright wellness editorial.",
            "Health drink product ad. Acai bowl in white bowl on marble, fresh berries, granola, honey drizzle from above. 'EAT YOUR COLORS' headline in clear space above. Vibrant food editorial.",
            "Premium juice lifestyle ad. Wicker tray with juice bottles and fresh fruit by pool in daylight. 'START WELL. LIVE WELL.' headline in clear sky above. Summer wellness editorial."
        ],
        "thumb": "Premium juice landscape thumbnail. Three vivid cold-press bottles on marble, fresh produce. 'NATURE BOTTLED' headline in clear space. Bright editorial."
    },
    {
        "slug": "vitamin-supplement-advertisement",
        "name": "Vitamin Supplement",
        "posts": [
            "Premium supplement brand full-page ad. AG1 aesthetic. Elegant container and glass of mixed greens drink on white marble, fresh vegetables arranged. 'ONE SCOOP. INFINITE IMPACT.' sans-serif headline in clear space above. PHYSICIAN FORMULATED · 75 NUTRIENTS · THIRD-PARTY TESTED.",
            "Luxury vitamin brand ad. Glass amber supplement bottles on clean white surface, botanical herbs beside. 'SCIENCE MEETS NATURE' headline in clear space above. Minimal wellness editorial.",
            "Premium protein powder ad. Sleek matte container on dark marble, scoop mid-fall of white powder. 'BUILD MORE THAN MUSCLE' headline in clear dark space above. Athletic editorial.",
            "Wellness supplement lifestyle ad. Morning supplement ritual — vitamins, matcha, journal on wooden tray by window. 'YOUR DAILY FOUNDATION' headline in clear space above. Warm wellness editorial."
        ],
        "thumb": "Premium supplement landscape thumbnail. Container and greens drink on marble, vegetables. 'ONE SCOOP. INFINITE IMPACT.' headline in clear space. Clean editorial."
    },
    {
        "slug": "organic-food-advertisement",
        "name": "Organic Food Brand",
        "posts": [
            "Organic food brand full-page ad. Whole Foods aesthetic. Abundance of fresh colorful organic vegetables and fruits arranged on dark stone, farmers market style. 'GROWN WITH PURPOSE' serif headline in clear space above. CERTIFIED ORGANIC · LOCALLY SOURCED · NON-GMO.",
            "Premium organic brand ad. Olive oil in glass bottle beside olives, herbs on marble. 'LIQUID GOLD FROM THE GROVE' headline in clear space above. Mediterranean editorial.",
            "Organic honey brand ad. Glass jar of raw golden honey, honeycomb beside, wildflowers on rustic wood. 'PURE FROM THE HIVE' headline in clear space above. Warm artisan editorial.",
            "Organic pasta brand ad. Bronze-cut pasta nest on dark slate, fresh tomato, basil, olive oil. 'FROM FIELD TO FORK' headline in clear space above. Italian artisan editorial."
        ],
        "thumb": "Organic food landscape thumbnail. Colorful fresh vegetables on dark stone. 'GROWN WITH PURPOSE' headline in clear space. Natural editorial."
    },
    {
        "slug": "cosmetics-makeup-advertisement",
        "name": "Cosmetics Makeup",
        "posts": [
            "Luxury cosmetics brand full-page ad. Charlotte Tilbury aesthetic. Rose gold lipstick tube on black velvet, dramatic spotlight, glitter dust. 'WEAR YOUR POWER' serif headline in clear dark space above. LONG-LASTING · CRUELTY-FREE · VEGAN.",
            "Premium makeup brand ad. Foundation bottle and beauty sponge on pink marble, fresh rose petals. 'YOUR PERFECT MATCH' headline in clear space above. Rose editorial.",
            "Luxury eyeshadow palette ad. Open palette with vivid colors on black background, makeup brush mid-stroke. 'CREATE YOUR MASTERPIECE' headline in clear dark space above. Dark glamour editorial.",
            "Cosmetics lifestyle ad. Vanity flatlay: lipstick, mascara, highlighter on mirrored surface with soft light. 'BEAUTY REIMAGINED' headline in clear space above. Glamour editorial."
        ],
        "thumb": "Luxury cosmetics landscape thumbnail. Rose gold lipstick on black velvet, spotlight. 'WEAR YOUR POWER' headline in clear dark space. Glamour editorial."
    },
    {
        "slug": "menswear-suit-advertisement",
        "name": "Menswear Suit",
        "posts": [
            "Luxury menswear brand full-page ad. Tom Ford aesthetic. Perfectly tailored charcoal suit on mannequin torso, stark white studio, dramatic single light. 'SUIT YOUR AMBITION' serif headline in clear space above. HAND TAILORED · SUPERFINE WOOL · BESPOKE FIT.",
            "Premium suit brand ad. Suit laid flat editorial: jacket, tie, pocket square, cufflinks arranged on dark floor. 'THE DETAILS MAKE THE MAN' headline in clear space above. Dark premium editorial.",
            "Luxury menswear lifestyle ad. Suited man standing at floor-to-ceiling window, city skyline behind, back to camera. 'DRESSED FOR SUCCESS' headline in clear sky zone above. Aspirational editorial.",
            "Premium shirt and tie ad. White dress shirt with silk tie perfectly knotted, on tailor's dummy, warm studio light. 'PERFECTION IN EVERY STITCH' headline in clear space above. Tailoring editorial."
        ],
        "thumb": "Luxury menswear landscape thumbnail. Tailored charcoal suit, white studio, dramatic light. 'SUIT YOUR AMBITION' headline in clear space. Tom Ford editorial."
    },
    {
        "slug": "womens-fashion-advertisement",
        "name": "Womens Fashion",
        "posts": [
            "Luxury women's fashion full-page ad. Celine aesthetic. Minimal structured silk blouse on white studio, single side light, perfect drape. 'EFFORTLESS. ICONIC.' serif headline in clear space above. PURE SILK · SUSTAINABLE · PARIS ATELIER.",
            "Premium women's brand ad. Dress flat lay on cream linen, architectural fold, editorial arrangement. 'WEAR YOUR STORY' headline in clear space above. Minimal cream editorial.",
            "Luxury handbag advertisement. Structured leather tote on marble table, soft natural light. 'YOUR EVERYDAY ICON' headline in clear space above. Minimal luxury editorial.",
            "Women's fashion lifestyle ad. Silk scarf, gold bracelet, perfume bottle editorial arrangement on marble. 'THE ART OF DRESSING' headline in clear space above. Refined editorial."
        ],
        "thumb": "Luxury women's fashion landscape thumbnail. Silk blouse, white studio, side light. 'EFFORTLESS. ICONIC.' headline in clear space. Celine editorial."
    },
    {
        "slug": "handbag-luxury-advertisement",
        "name": "Luxury Handbag",
        "posts": [
            "Luxury handbag brand full-page ad. Hermès aesthetic. Birkin bag on black velvet, single spotlight, leather sheen visible. 'BEYOND PRICE. BEYOND TIME.' serif headline in clear dark space above. HAND STITCHED · SADDLE LEATHER · MADE IN PARIS.",
            "Premium bag brand ad. Structured tote on white marble, minimalist editorial. 'CARRY CONFIDENCE' headline in clear space above. Clean luxury editorial.",
            "Luxury clutch ad. Evening clutch bag on silk fabric, crystal clasp reflecting light. 'FOR YOUR FINEST MOMENTS' headline in clear space above. Glamour editorial.",
            "Premium handbag lifestyle ad. Bag on passenger seat of luxury convertible, open road behind. 'GO FURTHER IN STYLE' headline in clear sky zone above. Aspirational editorial."
        ],
        "thumb": "Luxury handbag landscape thumbnail. Birkin bag on black velvet, spotlight. 'BEYOND PRICE. BEYOND TIME.' headline in clear dark space. Hermès editorial."
    },
    {
        "slug": "hotel-spa-advertisement",
        "name": "Hotel Spa",
        "posts": [
            "Luxury hotel spa full-page ad. Six Senses aesthetic. Stone hot tub with rose petals, candles, jungle view beyond, golden light. 'SURRENDER TO STILLNESS' serif headline in clear space above. HOLISTIC · AWARD-WINNING · TRANSFORMATIVE.",
            "Premium spa brand ad. Massage table with folded towels, orchid, lit candles, wood and stone interior. 'YOUR SANCTUARY AWAITS' headline in clear space above. Serene editorial.",
            "Luxury wellness retreat ad. Outdoor yoga platform over turquoise ocean, sunrise, single yoga mat. 'FIND YOUR CENTER' headline in clear sky above. Aspirational wellness editorial.",
            "Spa product ad. Essential oils, bamboo, smooth stones, orchids arranged on stone surface. 'PURE RESTORATION' headline in clear space above. Zen editorial."
        ],
        "thumb": "Luxury spa landscape thumbnail. Stone hot tub, rose petals, candles, jungle view. 'SURRENDER TO STILLNESS' headline in clear space. Serene editorial."
    },
    {
        "slug": "travel-airline-advertisement",
        "name": "Travel Airline",
        "posts": [
            "Premium airline full-page ad. Emirates First Class aesthetic. Flat-bed suite with champagne on armrest, window with cloud view, warm ambient lighting. 'ABOVE AND BEYOND' serif headline in clear space above. FLAT BED · GOURMET DINING · PERSONAL SUITE.",
            "Luxury airline product ad. Business class seat detail: champagne flute, amuse-bouche, linen headrest cover. 'FLY BETTER' headline in clear space above. Premium editorial.",
            "Travel brand lifestyle ad. Traveler with premium luggage at empty first-class lounge with city view. 'THE JOURNEY IS THE DESTINATION' headline in clear space above. Aspirational editorial.",
            "Airline brand ad. Aerial view of aircraft wing above sunset cloud layer, orange and pink sky. 'TAKE TO THE SKY' headline in clear sky zone. Cinematic aerial editorial."
        ],
        "thumb": "Premium airline landscape thumbnail. First class suite with champagne, cloud view. 'ABOVE AND BEYOND' headline in clear space. Premium editorial."
    },
    {
        "slug": "luggage-travel-advertisement",
        "name": "Luxury Luggage",
        "posts": [
            "Luxury luggage brand full-page ad. Rimowa aesthetic. Aluminum suitcase on empty airport terminal floor, dramatic dramatic hall lighting. 'ENGINEERED FOR THE JOURNEY' serif headline in clear space above. AEROSPACE ALUMINUM · 100-YEAR GUARANTEE · GERMAN MADE.",
            "Premium luggage brand ad. Four-piece luggage set on hotel room floor, passport, boarding pass styled. 'PACK YOUR WORLD' headline in clear space above. Travel editorial.",
            "Luxury travel bag ad. Leather weekender on train seat, European countryside blurred outside window. 'THE PERFECT COMPANION' headline in clear space above. Editorial travel photography.",
            "Premium luggage lifestyle ad. Suitcase open on hotel bed, curated packing, luxury hotel room. 'TRAVEL WITH INTENTION' headline in clear space above. Hotel editorial."
        ],
        "thumb": "Luxury luggage landscape thumbnail. Aluminum suitcase in empty terminal, dramatic light. 'ENGINEERED FOR THE JOURNEY' headline in clear space. Clean editorial."
    },
    {
        "slug": "stationery-brand-advertisement",
        "name": "Stationery Brand",
        "posts": [
            "Premium stationery brand full-page ad. Smythson aesthetic. Leather notebook with gold monogram on polished walnut desk, fountain pen beside. 'WRITE YOUR LEGACY' serif headline in clear space above. HAND BOUND · FEATHERWEIGHT PAPER · LONDON MADE.",
            "Luxury notebook brand ad. Open Moleskine on marble beside coffee cup, fresh flowers. 'YOUR IDEAS DESERVE THE BEST' headline in clear space above. Warm editorial.",
            "Premium pen brand ad. Gold fountain pen on dark leather desk pad, ink drop visible. 'SIGN WITH INTENTION' headline in clear dark space above. Dark luxury editorial.",
            "Stationery lifestyle ad. Desk flatlay: notebook, pen, washi tape, envelope, candle. 'THE RITUAL OF WRITING' headline in clear space above. Clean editorial."
        ],
        "thumb": "Premium stationery landscape thumbnail. Leather notebook with gold monogram, walnut desk. 'WRITE YOUR LEGACY' headline in clear space. Elegant editorial."
    },
    {
        "slug": "headphones-audio-advertisement",
        "name": "Headphones Audio",
        "posts": [
            "Premium headphones brand full-page ad. Sony WH-1000XM5 aesthetic. Sleek black headphones on dark matte surface, dramatic edge lighting. 'HEAR EVERYTHING' sans-serif headline in clear dark space above. NOISE CANCELLING · 30HR BATTERY · HI-RES AUDIO.",
            "Luxury headphones brand ad. Bose aesthetic. Over-ear headphones floating on gradient navy background. 'THE SILENCE IS YOURS' headline in clear space above. Premium tech editorial.",
            "Premium earbuds ad. Wireless earbuds in charging case on marble, one bud out. 'MUSIC. UNINTERRUPTED.' headline in clear space above. Minimal editorial.",
            "Headphone lifestyle ad. Person with headphones at cafe window, rain outside, eyes closed. 'YOUR WORLD. YOUR SOUNDTRACK.' headline in clear upper zone. Moody editorial."
        ],
        "thumb": "Premium headphones landscape thumbnail. Sleek black headphones on dark matte, edge light. 'HEAR EVERYTHING' headline in clear dark space. Editorial."
    },
    {
        "slug": "laptop-computer-advertisement",
        "name": "Laptop Computer",
        "posts": [
            "Premium laptop brand full-page ad. MacBook aesthetic. Slim silver laptop open on marble desk, glowing screen, coffee cup beside. 'THINK DIFFERENT. CREATE MORE.' sans-serif headline in clear space above. M4 CHIP · ALL-DAY BATTERY · RETINA DISPLAY.",
            "Luxury laptop brand ad. Laptop on minimal wood desk with plant, soft morning light. 'YOUR BEST WORK STARTS HERE' headline in clear space above. Warm lifestyle editorial.",
            "Premium laptop product ad. Closed laptop side profile on black, showing thinness, dramatic side light. 'IMPOSSIBLY THIN. IMPOSSIBLY POWERFUL.' headline in clear space. Minimal editorial.",
            "Laptop lifestyle ad. Coding setup: laptop, mechanical keyboard, monitor, plant, warm desk lamp. 'BUILD THE FUTURE' headline in clear space above. Creator lifestyle editorial."
        ],
        "thumb": "Premium laptop landscape thumbnail. Slim silver laptop on marble desk, glowing. 'THINK DIFFERENT. CREATE MORE.' headline in clear space. Clean editorial."
    },
    {
        "slug": "bank-finance-advertisement",
        "name": "Bank Finance",
        "posts": [
            "Premium bank full-page ad. Private banking aesthetic. Gold credit card on black marble, dramatic spotlight. 'YOUR WEALTH. YOUR LEGACY.' serif headline in clear dark space above. PRIVATE BANKING · WEALTH MANAGEMENT · CONCIERGE SERVICE.",
            "Luxury finance brand ad. Open safety deposit box revealing gold coins, stack of currencies. 'PROTECTING WHAT MATTERS' headline in clear space above. Dark prestige editorial.",
            "Premium investment brand ad. Graph going upward shown on minimalist screen on dark desk. 'GROW YOUR FUTURE' headline in clear space above. Sophisticated editorial.",
            "Private bank lifestyle ad. Banker and client handshake in private boardroom with city view. 'PARTNERSHIP BUILT ON TRUST' headline in clear upper zone. Corporate editorial."
        ],
        "thumb": "Premium bank landscape thumbnail. Gold credit card on black marble, spotlight. 'YOUR WEALTH. YOUR LEGACY.' headline in clear dark space. Prestige editorial."
    },
    {
        "slug": "insurance-advertisement",
        "name": "Insurance Brand",
        "posts": [
            "Premium insurance brand full-page ad. MetLife aesthetic. Family home exterior at golden hour, warm lights inside, safety concept. 'WE PROTECT WHAT YOU LOVE' serif headline in clear sky above. LIFE · HOME · AUTO · HEALTH.",
            "Luxury insurance brand ad. Hands clasped in trust over wooden table. 'THERE WHEN IT MATTERS MOST' headline in clear space above. Warm trust editorial.",
            "Premium car insurance ad. New luxury car keys on marble beside policy document folder. 'COVERED. ALWAYS.' headline in clear space above. Editorial.",
            "Insurance lifestyle ad. Family photo moment: parents with children on beach at sunset, genuine joy. 'PROTECT THE MOMENTS THAT MATTER' headline in clear sky above. Warm editorial."
        ],
        "thumb": "Premium insurance landscape thumbnail. Family home at golden hour, warm inside lights. 'WE PROTECT WHAT YOU LOVE' headline in clear sky. Warm editorial."
    },
    {
        "slug": "yoga-wellness-advertisement",
        "name": "Yoga Wellness",
        "posts": [
            "Premium yoga brand full-page ad. Lululemon aesthetic. Premium yoga mat unfurled in minimal studio with dappled morning light, block and strap beside. 'FIND YOUR FLOW' serif headline in clear space above. GRIP · ALIGNMENT · FLOW.",
            "Luxury yoga brand ad. Aerial view of woman in warrior pose on rooftop studio at sunrise, city below. 'RISE ABOVE' headline in clear sky zone. Aspirational wellness editorial.",
            "Premium yoga lifestyle ad. Rolled yoga mats, essential oils, wooden beads, journal on wooden floor. 'YOUR PRACTICE. YOUR PEACE.' headline in clear space above. Zen editorial.",
            "Yoga retreat ad. Open-air pavilion over ocean, bamboo floor, hanging fabric, single mat. 'WHERE PEACE BEGINS' headline in clear sky above. Tropical wellness editorial."
        ],
        "thumb": "Premium yoga landscape thumbnail. Minimal studio, morning light, mat and props. 'FIND YOUR FLOW' headline in clear space. Clean wellness editorial."
    },
    {
        "slug": "running-sports-advertisement",
        "name": "Running Sports Brand",
        "posts": [
            "Premium running brand full-page ad. Brooks aesthetic. Running shoes mid-stride on misty trail at dawn, motion blur, forest backdrop. 'RUN YOUR WORLD' bold headline in clear mist above. RESPONSIVE CUSHION · BREATHABLE MESH · CARBON PLATE.",
            "Running brand product ad. Single running shoe on white with dynamic paint splash. 'MADE FOR MILES' headline in clear space above. Dynamic white editorial.",
            "Premium athletic brand ad. Runner silhouette at start of empty coastal road at sunrise. 'THE ROAD IS YOURS' headline in clear sky zone. Cinematic sports editorial.",
            "Running lifestyle ad. Runner's gear flatlay: shoes, GPS watch, socks, hydration vest on asphalt. 'GEAR UP. SHOW UP.' headline in clear space above. Athletic editorial."
        ],
        "thumb": "Premium running landscape thumbnail. Shoes mid-stride on misty dawn trail, forest. 'RUN YOUR WORLD' headline in clear mist. Dynamic editorial."
    },
    {
        "slug": "cycling-brand-advertisement",
        "name": "Cycling Brand",
        "posts": [
            "Premium cycling brand full-page ad. Rapha aesthetic. Carbon road bike leaning on stone wall, alpine meadow behind, golden hour. 'RIDE FURTHER' serif headline in clear sky above. CARBON FRAME · AERODYNAMIC · PRO-GRADE.",
            "Luxury cycling brand ad. Close-up of bicycle drivetrain, chain, cassette, ceramic bearings catching light. 'ENGINEERED OBSESSION' headline in clear dark space above. Macro mechanical editorial.",
            "Premium cycling lifestyle ad. Cyclist in kit on mountain switchback descent, dramatic valley below. 'CONQUER EVERY CLIMB' headline in clear sky zone. Adventure editorial.",
            "Cycling brand product ad. Helmet, gloves, jersey, cleats editorial flatlay on marble. 'KIT UP PROPERLY' headline in clear space above. Premium editorial."
        ],
        "thumb": "Premium cycling landscape thumbnail. Carbon bike on stone wall, alpine meadow. 'RIDE FURTHER' headline in clear sky. Golden editorial."
    },
    {
        "slug": "outdoor-adventure-advertisement",
        "name": "Outdoor Adventure Brand",
        "posts": [
            "Premium outdoor brand full-page ad. Patagonia aesthetic. Technical shell jacket on peak of granite mountain, storm clearing, dramatic sky. 'BUILT FOR THE WILD' sans-serif headline in clear stormy sky above. RECYCLED MATERIALS · LIFETIME REPAIR · BLUESIGN.",
            "Outdoor gear brand ad. Backpacker on ridge silhouetted against sunset, perfect composition. 'YOUR PATH AWAITS' headline in clear sky zone. Adventure editorial.",
            "Premium camping brand ad. Perfect campsite at alpine lake: tent, hammock, fire, golden hour. 'LIVE OUTSIDE' headline in clear sky above. Aspirational outdoor editorial.",
            "Outdoor adventure lifestyle ad. Climbing gear flatlay: harness, carabiners, rope, chalk bag on rock. 'REACH NEW HEIGHTS' headline in clear space above. Technical outdoor editorial."
        ],
        "thumb": "Premium outdoor landscape thumbnail. Technical jacket on granite peak, dramatic sky. 'BUILT FOR THE WILD' headline in clear sky. Adventure editorial."
    },
    {
        "slug": "sunscreen-spf-advertisement",
        "name": "Sunscreen SPF",
        "posts": [
            "Premium sunscreen brand full-page ad. Supergoop aesthetic. Elegant SPF tube and mist spray on white marble, fresh jasmine. 'PROTECT YOUR GLOW' serif headline in clear space above. SPF 50 · REEF SAFE · INVISIBLE FINISH.",
            "Luxury sunscreen brand ad. Sunscreen bottle half-submerged in pure white sand, ocean blur behind. 'MADE FOR THE SUN' headline in clear sky zone above. Summer editorial.",
            "Premium SPF product ad. Overhead flatlay of sunscreen, sunglasses, straw hat on linen. 'SUMMER ESSENTIALS' headline in clear space above. Clean summer editorial.",
            "Sunscreen lifestyle ad. Applying sunscreen at beach, close-up of hands on shoulders, ocean behind. 'LOVE YOUR SKIN' headline in clear sky zone. Warm editorial."
        ],
        "thumb": "Premium sunscreen landscape thumbnail. SPF tube on white marble, fresh jasmine. 'PROTECT YOUR GLOW' headline in clear space. Summer editorial."
    },
    {
        "slug": "dental-oral-care-advertisement",
        "name": "Dental Oral Care",
        "posts": [
            "Premium oral care brand full-page ad. Colgate Premium aesthetic. Electric toothbrush and matte tube on white marble, water droplet. 'YOUR BRIGHTEST SMILE' serif headline in clear space above. CLINICALLY PROVEN · ENAMEL CARE · DENTIST RECOMMENDED.",
            "Luxury teeth whitening brand ad. Before-after showing brilliant white teeth, minimal clinical background. 'CONFIDENCE IN EVERY SMILE' headline in clear space above. Clean health editorial.",
            "Premium toothpaste brand ad. Sleek tube on black marble, toothpaste ribbon emerging. 'PURE CLEAN' headline in clear dark space above. Minimal editorial.",
            "Oral care lifestyle ad. Morning bathroom ritual: toothbrush, cup, mirror, morning light. 'START YOUR BEST DAY' headline in clear space above. Fresh morning editorial."
        ],
        "thumb": "Premium oral care landscape thumbnail. Electric toothbrush and tube on white marble. 'YOUR BRIGHTEST SMILE' headline in clear space. Clean editorial."
    },
    {
        "slug": "baby-products-advertisement",
        "name": "Baby Products",
        "posts": [
            "Premium baby brand full-page ad. Ergobaby aesthetic. Soft organic cotton baby clothes folded on white linen, fresh lavender beside. 'GENTLE FROM THE START' serif headline in clear space above. ORGANIC · DERMATOLOGIST TESTED · HYPOALLERGENIC.",
            "Luxury baby care brand ad. Glass baby bottle on marble beside chamomile flowers, soft window light. 'PURE FOR YOURS' headline in clear space above. Soft white editorial.",
            "Premium baby products ad. Overhead flatlay of baby essentials: lotion, shampoo, soft toy on white. 'THE BEST FOR YOUR BEST' headline in clear space above. Pure editorial.",
            "Baby brand lifestyle ad. Baby's feet on white sheet, parent's hands gently holding. 'EVERY MOMENT IS PRECIOUS' headline in clear space above. Warm tender editorial."
        ],
        "thumb": "Premium baby landscape thumbnail. Soft organic baby clothes on white linen, lavender. 'GENTLE FROM THE START' headline in clear space. Soft editorial."
    },
    {
        "slug": "pet-food-advertisement",
        "name": "Pet Food Brand",
        "posts": [
            "Premium pet food brand full-page ad. Royal Canin aesthetic. Shiny happy dog beside premium food bowl filled with kibble on oak floor, warm kitchen. 'NOURISH THEIR BEST LIFE' serif headline in clear space above. VET RECOMMENDED · BREED SPECIFIC · SCIENCE BACKED.",
            "Luxury pet food brand ad. Glass jar of premium raw pet food on marble, fresh meat and vegetables artfully arranged beside. 'REAL FOOD. REAL LOVE.' headline in clear space above. Editorial.",
            "Premium cat food brand ad. Content cat beside elegant feeding bowl, soft natural light, clean home. 'CRAFTED FOR CATS' headline in clear space above. Lifestyle editorial.",
            "Pet food lifestyle ad. Dog food flatlay: bag, fresh bowl, bone treat on rustic floor. 'FEED THE LOVE' headline in clear space above. Warm editorial."
        ],
        "thumb": "Premium pet food landscape thumbnail. Happy dog beside premium bowl on oak floor. 'NOURISH THEIR BEST LIFE' headline in clear space. Warm editorial."
    },
    {
        "slug": "home-decor-advertisement",
        "name": "Home Decor",
        "posts": [
            "Premium home decor brand full-page ad. CB2 aesthetic. Minimal living room: linen sofa, travertine coffee table, dried pampas, warm afternoon light. 'LIVE IN BEAUTY' serif headline in clear upper space. CONTEMPORARY · HANDCRAFTED · SUSTAINABLE.",
            "Luxury interior brand ad. Ceramic vase with dried botanicals on marble ledge, architectural light. 'DESIGNED FOR LIVING' headline in clear space above. Minimal editorial.",
            "Premium home goods ad. Dining table setting: linen napkins, stone plates, hand-blown glasses, candles, fresh greenery. 'GATHER BEAUTIFULLY' headline in clear space above. Editorial.",
            "Home decor lifestyle ad. Cozy reading corner: armchair, throw, lamp, coffee, bookshelf. 'YOUR REFUGE' headline in clear space above. Warm editorial."
        ],
        "thumb": "Premium home decor landscape thumbnail. Minimal living room, linen sofa, travertine, pampas. 'LIVE IN BEAUTY' headline in clear space. Warm editorial."
    },
    {
        "slug": "candle-fragrance-home-ad",
        "name": "Candle Home Fragrance",
        "posts": [
            "Luxury candle brand full-page ad. Diptyque aesthetic. Single pillar candle on dark marble, flame lit, smoke wisps, soft dark background. 'ILLUMINATE YOUR HOME' serif headline in clear dark space above. SOY WAX · COTTON WICK · FRENCH FRAGRANCE.",
            "Premium candle brand ad. Trio of candles in concrete vessels on marble shelf, botanicals beside. 'SCENT YOUR SANCTUARY' headline in clear space above. Minimal editorial.",
            "Luxury home fragrance ad. Reed diffuser on bathroom vanity with fresh eucalyptus and stone. 'BREATHE BEAUTIFULLY' headline in clear space above. Spa editorial.",
            "Candle brand lifestyle ad. Lit candle on coffee table with open book, wine glass, evening ambience. 'EVERY EVENING RITUAL' headline in clear space above. Warm cozy editorial."
        ],
        "thumb": "Luxury candle landscape thumbnail. Lit pillar candle on dark marble, smoke wisps. 'ILLUMINATE YOUR HOME' headline in clear dark space. Diptyque editorial."
    },
    {
        "slug": "kitchen-appliances-advertisement",
        "name": "Kitchen Appliances",
        "posts": [
            "Premium kitchen appliance brand full-page ad. KitchenAid aesthetic. Iconic stand mixer in navy on white marble, flour dusting, recipe card. 'BUILT TO CREATE' serif headline in clear space above. PROFESSIONAL GRADE · HAND CRAFTED · USA MADE.",
            "Luxury coffee machine brand ad. La Marzocco espresso machine on marble kitchen counter, morning light. 'THE HEART OF YOUR KITCHEN' headline in clear space above. Premium editorial.",
            "Premium blender brand ad. Vitamix on marble, fresh smoothie mid-blend, fruits arranged. 'BLEND THE EXTRAORDINARY' headline in clear space above. Clean kitchen editorial.",
            "Kitchen appliance lifestyle ad. Induction range in chef's kitchen, copper pots, marble backsplash. 'WHERE GREAT MEALS BEGIN' headline in clear space above. Kitchen editorial."
        ],
        "thumb": "Premium kitchen appliance landscape thumbnail. KitchenAid stand mixer on marble, flour. 'BUILT TO CREATE' headline in clear space. Clean editorial."
    },
    {
        "slug": "bedding-sleep-advertisement",
        "name": "Bedding Sleep Brand",
        "posts": [
            "Luxury bedding brand full-page ad. Frette aesthetic. Perfectly made bed with 1000-thread Egyptian cotton sheets, morning light through sheer curtains. 'SLEEP LIKE ROYALTY' serif headline in clear space above. EGYPTIAN COTTON · 1000 THREAD COUNT · HOTEL COLLECTION.",
            "Premium pillow brand ad. Four luxurious goose down pillows stacked on white linen, morning sun. 'THE PERFECT NIGHT STARTS HERE' headline in clear space above. Pure white editorial.",
            "Luxury bedding lifestyle ad. Unmade bed morning scene, coffee cup, book, white linen. 'MADE FOR MORNINGS' headline in clear space above. Warm relaxed editorial.",
            "Premium duvet brand ad. Close-up of hand feeling 1000-thread cotton sheet, soft light, texture visible. 'FEEL THE DIFFERENCE' headline in clear space above. Tactile editorial."
        ],
        "thumb": "Luxury bedding landscape thumbnail. Perfectly made bed, Egyptian cotton, morning light. 'SLEEP LIKE ROYALTY' headline in clear space. Pure editorial."
    },
    {
        "slug": "paint-color-brand-advertisement",
        "name": "Paint Color Brand",
        "posts": [
            "Premium paint brand full-page ad. Farrow and Ball aesthetic. Freshly painted deep teal wall with single gold framed artwork, architectural perfection. 'COLOR THAT TRANSFORMS' serif headline in clear space beside wall. MINERAL PIGMENTS · HANDMADE · ARCHIVE COLORS.",
            "Luxury paint brand ad. Paint tin open showing rich sage green, brush resting, chips arranged. 'YOUR WALLS. YOUR CANVAS.' headline in clear space above. Editorial.",
            "Premium color brand ad. Room corner transformed by dusty pink paint, shadow play, minimal decor. 'LIVING WITH COLOR' headline in clear space above. Interior editorial.",
            "Paint brand lifestyle ad. Hands opening paint tin of inky navy, studio setting, swatches visible. 'CHOOSE YOUR STORY' headline in clear space above. Editorial."
        ],
        "thumb": "Premium paint landscape thumbnail. Deep teal painted wall, gold framed art. 'COLOR THAT TRANSFORMS' headline in clear space. Farrow and Ball editorial."
    },
    {
        "slug": "tech-gadget-advertisement",
        "name": "Tech Gadget Brand",
        "posts": [
            "Premium tech brand full-page ad. Apple aesthetic. Minimal smart speaker on white shelf, soft ambient light. 'SOUND REDEFINED' sans-serif headline in clear space above. 360 AUDIO · VOICE CONTROL · SEAMLESS SETUP.",
            "Premium smartwatch brand ad. Sleek smartwatch on black matte surface, edge light revealing screen glow. 'SMARTER ON YOUR WRIST' headline in clear dark space above. Minimal tech editorial.",
            "Luxury tech brand ad. Wireless charging pad with phone and earbuds all wirelessly charging on marble. 'THE FUTURE IS WIRELESS' headline in clear space above. Clean tech editorial.",
            "Premium home tech ad. Smart thermostat on minimal white wall, clean interior. 'LIVE SMARTER' headline in clear space beside device. Minimal editorial."
        ],
        "thumb": "Premium tech landscape thumbnail. Smart speaker on white shelf, ambient light. 'SOUND REDEFINED' headline in clear space. Minimal editorial."
    },
    {
        "slug": "gaming-brand-advertisement",
        "name": "Gaming Brand",
        "posts": [
            "Premium gaming brand full-page ad. Razer aesthetic. Gaming setup: mechanical keyboard, controller, RGB lighting, dark desk. 'PLAY WITHOUT LIMITS' bold sans-serif headline in clear dark space above. PRO-GRADE · RGB · TOURNAMENT READY.",
            "Gaming console brand ad. Controller floating on electric blue gradient, neon accents, dramatic light. 'ENTER THE GAME' headline in clear space above. Dynamic editorial.",
            "Premium gaming headset ad. Headset on dark stand, RGB glow. 'HEAR EVERY DETAIL' headline in clear dark space above. Dark gaming editorial.",
            "Gaming lifestyle brand ad. Pro gamer setup: ultra-wide monitors, perfect desk layout. 'BUILT FOR CHAMPIONS' headline in clear space above. Dark editorial."
        ],
        "thumb": "Premium gaming landscape thumbnail. Gaming setup with RGB, dark desk. 'PLAY WITHOUT LIMITS' headline in clear dark space. Razer editorial."
    },
    {
        "slug": "university-education-advertisement",
        "name": "University Education",
        "posts": [
            "Premium university full-page ad. Harvard aesthetic. Gothic university building facade at golden autumn, red maple leaves. 'SHAPE YOUR FUTURE' serif headline in clear sky above. WORLD-CLASS FACULTY · GLOBAL NETWORK · RESEARCH EXCELLENCE.",
            "Premium education brand ad. Library interior: vaulted ceiling, rows of books, student studying in pool of light. 'KNOWLEDGE IS POWER' headline in clear upper zone. Aspirational editorial.",
            "University lifestyle ad. Students on quad lawn in autumn sun, engaged discussion, campus architecture behind. 'WHERE LEADERS ARE MADE' headline in clear sky zone. Editorial.",
            "Higher education brand ad. Graduation cap and diploma on dark oak desk, sun through window. 'YOUR ACHIEVEMENT. YOUR FUTURE.' headline in clear space above. Heritage editorial."
        ],
        "thumb": "University landscape thumbnail. Gothic building at golden autumn, red maples. 'SHAPE YOUR FUTURE' headline in clear sky. Aspirational editorial."
    },
    {
        "slug": "online-course-advertisement",
        "name": "Online Course Platform",
        "posts": [
            "Premium online learning platform full-page ad. MasterClass aesthetic. Laptop on desk showing course interface, notebook with pen, soft focus. 'LEARN FROM THE BEST' sans-serif headline in clear space above. WORLD EXPERTS · ON DEMAND · LIFETIME ACCESS.",
            "Online course brand ad. Person at laptop by window, golden hour light, learning focused. 'INVEST IN YOURSELF' headline in clear sky zone. Warm lifestyle editorial.",
            "E-learning brand ad. Notebook, certificate, laptop on marble — the tools of learning. 'YOUR NEXT CHAPTER STARTS HERE' headline in clear space above. Clean editorial.",
            "Online education lifestyle ad. Professional reading course notes on tablet at cafe, focused. 'UPGRADE YOUR SKILLS' headline in clear space above. Editorial."
        ],
        "thumb": "Online learning landscape thumbnail. Laptop showing course, notebook, desk. 'LEARN FROM THE BEST' headline in clear space. Editorial."
    },
    {
        "slug": "music-streaming-advertisement",
        "name": "Music Streaming",
        "posts": [
            "Premium music streaming brand full-page ad. Spotify aesthetic. Vinyl record on turntable, glowing warm light, vintage aesthetic. 'MUSIC. EVERYWHERE.' bold sans-serif headline in clear dark space above. 100M SONGS · LOSSLESS · PERSONALIZED.",
            "Music streaming brand ad. Concert crowd silhouette with colorful stage lights, phone screen with app in foreground. 'YOUR SOUNDTRACK TO LIFE' headline in clear upper zone. Vibrant editorial.",
            "Streaming lifestyle ad. Earbuds on vinyl record cover, morning coffee beside. 'START YOUR DAY WITH MUSIC' headline in clear space above. Warm editorial.",
            "Music platform ad. Mix of instruments — guitar, piano keys, drums — arranged in dark studio. 'WHERE MUSIC LIVES' headline in clear dark space above. Cinematic editorial."
        ],
        "thumb": "Music streaming landscape thumbnail. Vinyl on turntable, warm glow. 'MUSIC. EVERYWHERE.' headline in clear dark space. Warm editorial."
    },
    {
        "slug": "food-delivery-advertisement",
        "name": "Food Delivery App",
        "posts": [
            "Premium food delivery brand full-page ad. DoorDash aesthetic. Restaurant meal in kraft takeout box on doorstep, evening home lighting. 'YOUR FAVORITE RESTAURANT. AT HOME.' bold headline in clear space above. 1000+ RESTAURANTS · 30 MIN DELIVERY · LIVE TRACKING.",
            "Food delivery brand ad. Open food delivery bag on kitchen counter with multiple dishes, excited close-up. 'EVERYTHING YOU CRAVE' headline in clear space above. Vibrant editorial.",
            "Food app lifestyle ad. Person on sofa ordering on phone, meal arriving notification. 'DINNER. SORTED.' headline in clear space above. Warm home editorial.",
            "Delivery brand ad. Courier on bike with delivery bag in urban street, golden hour light. 'FAST. FRESH. YOURS.' headline in clear sky zone above. Urban editorial."
        ],
        "thumb": "Food delivery landscape thumbnail. Meal in kraft box at doorstep, evening. 'YOUR FAVORITE RESTAURANT. AT HOME.' headline in clear space. Warm editorial."
    },
    {
        "slug": "pharmacy-health-advertisement",
        "name": "Pharmacy Health",
        "posts": [
            "Premium pharmacy brand full-page ad. Clean medicine cabinet aesthetic. Arranged vitamins, skincare, supplements on white shelf, clinical clean. 'YOUR HEALTH. OUR MISSION.' serif headline in clear space above. LICENSED PHARMACISTS · SAME DAY DELIVERY · TRUSTED BRANDS.",
            "Health brand lifestyle ad. Doctor-patient handshake, warm clinical setting, trust moment. 'CARE YOU CAN COUNT ON' headline in clear upper zone. Professional editorial.",
            "Pharmacy wellness ad. Healthy foods, supplements, measuring tape flatlay on white. 'WELLNESS STARTS HERE' headline in clear space above. Clean health editorial.",
            "Pharmacy brand ad. Prescription bag with care note on pharmacy counter, warm professional setting. 'THERE FOR YOU' headline in clear space above. Warm editorial."
        ],
        "thumb": "Pharmacy health landscape thumbnail. Vitamins and supplements on white shelf, clinical clean. 'YOUR HEALTH. OUR MISSION.' headline in clear space. Clean editorial."
    },
    {
        "slug": "solar-energy-advertisement",
        "name": "Solar Energy Brand",
        "posts": [
            "Premium solar brand full-page ad. Tesla Solar aesthetic. Row of sleek black solar panels on modern roof, clear blue sky, sunrise. 'POWER YOUR FUTURE' sans-serif headline in clear sky above. CLEAN · AFFORDABLE · FOREVER.",
            "Solar energy brand ad. Solar panel field at golden sunset, wind turbines in distance. 'A CLEANER TOMORROW' headline in clear sky zone. Environmental editorial.",
            "Home solar lifestyle ad. Modern family home with rooftop panels, electric car charging below, sunny day. 'ENERGY INDEPENDENCE' headline in clear sky above. Aspirational lifestyle editorial.",
            "Solar brand tech ad. Close-up of solar cell texture, dramatic macro light. 'HARNESSING THE SUN' headline in clear space above. Technical editorial."
        ],
        "thumb": "Solar energy landscape thumbnail. Sleek panels on modern roof, sunrise blue sky. 'POWER YOUR FUTURE' headline in clear sky. Clean editorial."
    },
    {
        "slug": "electric-vehicle-advertisement",
        "name": "Electric Vehicle",
        "posts": [
            "Premium EV brand full-page ad. Rivian aesthetic. Electric SUV on mountain trail, charging at solar station, epic landscape. 'DRIVE FURTHER. LEAVE NO TRACE.' headline in clear sky above. 400MI RANGE · OFF-ROAD · NET ZERO.",
            "Electric car brand ad. EV charging at home garage overnight, family home lit warmly. 'CHARGE WHILE YOU SLEEP' headline in clear space above. Lifestyle editorial.",
            "Premium EV lifestyle ad. Interior of electric SUV, premium materials, digital dashboard glowing. 'THE FUTURE LOOKS THIS GOOD' headline in clear space. Interior editorial.",
            "EV brand ad. Sleek electric sedan on empty coastal highway at dawn, zero emissions concept. 'THE ROAD AHEAD IS ELECTRIC' headline in clear sky zone. Cinematic editorial."
        ],
        "thumb": "EV landscape thumbnail. Electric SUV on mountain trail, solar charging. 'DRIVE FURTHER. LEAVE NO TRACE.' headline in clear sky. Epic editorial."
    },
    {
        "slug": "sport-nutrition-advertisement",
        "name": "Sports Nutrition",
        "posts": [
            "Premium sports nutrition brand full-page ad. Optimum Nutrition aesthetic. Gold standard protein tub on dark gym floor, weight plates beside. 'GOLD STANDARD PERFORMANCE' bold headline in clear dark space above. 24G PROTEIN · 5.5G BCAAs · BANNED SUBSTANCE FREE.",
            "Sports nutrition lifestyle ad. Athlete shaking protein drink post-workout, gym in background. 'RECOVER. REBUILD. REPEAT.' headline in clear upper zone. Athletic editorial.",
            "Premium pre-workout brand ad. Neon-labeled tub on dark surface, energy concept, sparks. 'IGNITE YOUR POTENTIAL' headline in clear dark space above. Dark athletic editorial.",
            "Nutrition brand ad. Clean macros flatlay: chicken, rice, broccoli, supplement beside on meal prep containers. 'EAT FOR PERFORMANCE' headline in clear space above. Clean editorial."
        ],
        "thumb": "Sports nutrition landscape thumbnail. Protein tub on dark gym floor, weight plates. 'GOLD STANDARD PERFORMANCE' headline in clear space. Dark athletic editorial."
    },
    {
        "slug": "meditation-mindfulness-advertisement",
        "name": "Meditation Mindfulness",
        "posts": [
            "Premium meditation brand full-page ad. Headspace aesthetic. Minimal room: cushion on oak floor, candle, incense, morning light from window. 'FIND YOUR CALM' sans-serif headline in clear space above. GUIDED · SLEEP · FOCUS · MOVEMENT.",
            "Mindfulness brand ad. Person meditating on cliff overlooking ocean at sunrise, golden light. 'BE PRESENT' headline in clear sky zone. Aspirational editorial.",
            "Meditation lifestyle ad. Meditation corner setup: zafu cushion, singing bowl, crystals, plant. 'YOUR DAILY RESET' headline in clear space above. Zen editorial.",
            "Mindfulness app ad. Phone screen showing calm app interface beside tea, morning notebook. 'START YOUR MORNING WELL' headline in clear space above. Warm editorial."
        ],
        "thumb": "Meditation landscape thumbnail. Minimal room, cushion on oak floor, candle, morning light. 'FIND YOUR CALM' headline in clear space. Zen editorial."
    },
    {
        "slug": "wedding-brand-advertisement",
        "name": "Wedding Brand",
        "posts": [
            "Premium wedding brand full-page ad. The Knot aesthetic. Bridal bouquet of white peonies and roses on marble, ribbon, ring box beside. 'YOUR PERFECT DAY' serif headline in clear space above. FULL PLANNING · FLORALS · VENUES · CATERING.",
            "Luxury wedding venue ad. Empty grand ballroom set for wedding reception, candlelight, white florals, golden arches. 'WHERE DREAMS COME TRUE' headline in clear upper zone. Opulent editorial.",
            "Wedding brand lifestyle ad. Bride and groom hands clasped showing rings, soft backlighting. 'FOREVER BEGINS HERE' headline in clear space above. Romantic editorial.",
            "Wedding stationery brand ad. Luxury invitation suite flat lay on marble: envelope, card, wax seal, flowers. 'YOUR STORY. YOUR INVITATION.' headline in clear space above. Editorial."
        ],
        "thumb": "Wedding brand landscape thumbnail. Bridal bouquet on marble, ring box. 'YOUR PERFECT DAY' headline in clear space. Romantic editorial."
    },
    {
        "slug": "florist-flowers-advertisement",
        "name": "Florist Flowers",
        "posts": [
            "Premium florist brand full-page ad. Bloom and Wild aesthetic. Enormous garden rose bouquet in kraft paper on marble counter, morning light. 'FLOWERS SPEAK LOUDER' serif headline in clear space above. SAME DAY DELIVERY · SEASONAL · HAND TIED.",
            "Luxury flower brand ad. Single long-stem burgundy rose on black marble, water drops, dramatic light. 'ONE IS ENOUGH' headline in clear dark space above. Minimal editorial.",
            "Florist lifestyle ad. Florist hands arranging wildflower arrangement, apron, studio workshop. 'HANDCRAFTED WITH LOVE' headline in clear upper zone. Artisan editorial.",
            "Flower brand seasonal ad. Overhead of tulips, ranunculus, eucalyptus arranged on white surface. 'NATURE'S FINEST' headline in clear space above. Spring editorial."
        ],
        "thumb": "Florist landscape thumbnail. Garden rose bouquet on marble, morning light. 'FLOWERS SPEAK LOUDER' headline in clear space. Fresh editorial."
    },
    {
        "slug": "bookstore-advertisement",
        "name": "Bookstore Brand",
        "posts": [
            "Premium bookstore brand full-page ad. Powell's Books aesthetic. Floor-to-ceiling dark wood shelves packed with colorful books, warm lamplight, rolling ladder. 'EVERY BOOK A DOOR' serif headline in clear space above. OVER 1 MILLION TITLES · EXPERT STAFF · RARE AND USED.",
            "Luxury bookstore ad. Stack of five hardcovers on marble cafe table beside coffee, reading glasses. 'FEED YOUR MIND' headline in clear space above. Warm editorial.",
            "Bookstore lifestyle ad. Person in deep reading in cozy armchair, floor lamp, bookshelf wall behind, rain on window. 'LOSE YOURSELF' headline in clear upper space. Cozy editorial.",
            "Bookstore brand ad. Books arranged by color spine — rainbow editorial on oak shelf. 'YOUR COLLECTION STARTS HERE' headline in clear space above. Visual editorial."
        ],
        "thumb": "Bookstore landscape thumbnail. Floor-to-ceiling dark shelves, warm lamplight, rolling ladder. 'EVERY BOOK A DOOR' headline in clear space. Warm editorial."
    },
    {
        "slug": "architecture-firm-advertisement",
        "name": "Architecture Firm",
        "posts": [
            "Premium architecture firm full-page ad. Zaha Hadid aesthetic. Dramatic curved concrete building exterior at dusk, interior lights glowing. 'WE BUILD FUTURES' serif headline in clear sky above. AWARD WINNING · SUSTAINABLE · ICONIC DESIGN.",
            "Luxury architecture ad. Architectural model on designer desk, blueprints, soft studio light. 'VISION TO REALITY' headline in clear space above. Professional editorial.",
            "Architecture firm lifestyle ad. Architect reviewing plans at floor-to-ceiling window, city below. 'DESIGNED WITH PURPOSE' headline in clear sky zone. Aspirational editorial.",
            "Architecture brand ad. Dramatic interior of designed atrium space, natural light through glass roof. 'LIGHT. SPACE. LIVING.' headline in clear space above. Architectural editorial."
        ],
        "thumb": "Architecture firm landscape thumbnail. Curved concrete building at dusk, glowing interior. 'WE BUILD FUTURES' headline in clear sky. Dramatic editorial."
    },
    {
        "slug": "interior-design-advertisement",
        "name": "Interior Design",
        "posts": [
            "Luxury interior design brand full-page ad. Kelly Wearstler aesthetic. Styled living room: sculptural lamp, travertine surface, layered textures, warm afternoon light. 'SPACES THAT INSPIRE' serif headline in clear upper space. RESIDENTIAL · COMMERCIAL · HOSPITALITY.",
            "Premium interior brand ad. Before-after concept: empty room vs fully designed space. 'TRANSFORMATION IS AN ART' headline in clear space above. Design editorial.",
            "Interior design lifestyle ad. Interior designer presenting samples to client at studio table. 'YOUR VISION. OUR CRAFT.' headline in clear upper zone. Professional editorial.",
            "Interior brand ad. Detail shots: fabric swatches, tile samples, wood finish on designer table. 'DETAILS MAKE THE DIFFERENCE' headline in clear space above. Texture editorial."
        ],
        "thumb": "Interior design landscape thumbnail. Styled living room, sculptural lamp, travertine. 'SPACES THAT INSPIRE' headline in clear space. Warm editorial."
    },
    {
        "slug": "photography-brand-advertisement",
        "name": "Photography Brand",
        "posts": [
            "Premium camera brand full-page ad. Leica aesthetic. Black rangefinder camera on white marble, dramatic side light. 'CAPTURE THE MOMENT. FOREVER.' serif headline in clear space above. GERMAN ENGINEERING · SUMMILUX LENS · TIMELESS.",
            "Luxury camera brand ad. Professional DSLR with prime lens on photographer's worn leather bag. 'EVERY FRAME A MASTERPIECE' headline in clear space above. Editorial.",
            "Photography lifestyle ad. Photographer at golden hour, silhouette with long lens, ocean behind. 'SEE THE WORLD DIFFERENTLY' headline in clear sky zone. Cinematic editorial.",
            "Camera brand product ad. Lens macro close-up showing glass elements. 'PRECISION OPTICS' headline in clear dark space above. Technical editorial."
        ],
        "thumb": "Camera brand landscape thumbnail. Black Leica on white marble, side light. 'CAPTURE THE MOMENT.' headline in clear space. Minimal editorial."
    },
    {
        "slug": "creative-agency-advertisement",
        "name": "Creative Agency",
        "posts": [
            "Premium creative agency full-page ad. Pentagram aesthetic. Abstract colorful design work spread on light table, hands arranging. 'IDEAS THAT MOVE PEOPLE' sans-serif headline in clear space above. BRAND · DIGITAL · CAMPAIGNS · STRATEGY.",
            "Creative agency brand ad. Agency team at long white table, working, energy, natural light. 'YOUR BRAND. REIMAGINED.' headline in clear upper zone. Dynamic editorial.",
            "Design agency ad. Colorful brand moodboards pinned to wall, art director studying. 'WHERE BRANDS ARE BORN' headline in clear space above. Creative editorial.",
            "Agency portfolio ad. Grid of diverse brand logos, campaigns on dark background. 'WORK THAT WINS.' headline in clear dark space above. Portfolio editorial."
        ],
        "thumb": "Creative agency landscape thumbnail. Design work on light table, colorful. 'IDEAS THAT MOVE PEOPLE' headline in clear space. Editorial."
    },
    {
        "slug": "law-firm-advertisement",
        "name": "Law Firm",
        "posts": [
            "Premium law firm full-page ad. White and Case aesthetic. Law books in dark wood library, dramatic lamplight. 'JUSTICE. INTEGRITY. RESULTS.' serif headline in clear dark space above. CORPORATE · LITIGATION · GLOBAL PRESENCE · 150 YEARS.",
            "Luxury law firm ad. Lawyer with briefcase exiting courthouse, dramatic wide steps. 'YOUR ADVOCATE. YOUR ALLY.' headline in clear sky zone above. Prestigious editorial.",
            "Law firm brand ad. Scales of justice on polished mahogany desk, sunlight. 'BALANCED. POWERFUL.' headline in clear space above. Heritage editorial.",
            "Legal brand lifestyle ad. Attorney and client at conference table, trust, urban office backdrop. 'COUNSEL YOU CAN TRUST' headline in clear upper zone. Professional editorial."
        ],
        "thumb": "Law firm landscape thumbnail. Dark wood law library, dramatic lamplight. 'JUSTICE. INTEGRITY. RESULTS.' headline in clear dark space. Prestigious editorial."
    },
    {
        "slug": "accounting-finance-firm-ad",
        "name": "Accounting Finance Firm",
        "posts": [
            "Premium accounting firm full-page ad. Big Four aesthetic. Clean glass office tower at dusk, city reflected. 'NUMBERS THAT TELL YOUR STORY' serif headline in clear sky above. TAX · AUDIT · ADVISORY · GLOBAL REACH.",
            "Finance firm brand ad. Professional reviewing financial charts on tablet, clean office, natural light. 'PRECISION. EVERY FIGURE.' headline in clear space above. Professional editorial.",
            "Accounting firm lifestyle ad. Handshake in corporate boardroom, city view. 'YOUR FINANCIAL PARTNER' headline in clear space above. Trust editorial.",
            "Finance firm ad. Calculator, annual report, pen on polished desk. 'CLARITY IN EVERY NUMBER' headline in clear space above. Corporate editorial."
        ],
        "thumb": "Accounting firm landscape thumbnail. Glass tower at dusk, city reflected. 'NUMBERS THAT TELL YOUR STORY' headline in clear sky. Corporate editorial."
    },
    {
        "slug": "medical-clinic-advertisement",
        "name": "Medical Clinic",
        "posts": [
            "Premium medical clinic full-page ad. Mayo Clinic aesthetic. Modern clinic interior with natural light, doctor reviewing tablet, clean white. 'YOUR HEALTH IS OUR PRIORITY' serif headline in clear space above. SPECIALIST CARE · ADVANCED TECHNOLOGY · COMPASSION.",
            "Luxury clinic brand ad. Doctor-patient consultation, warm light, trust. 'MEDICINE WITH HEART' headline in clear space above. Professional editorial.",
            "Medical brand ad. Medical technology close-up: MRI details, sterile equipment, precision. 'ADVANCED CARE' headline in clear dark space above. Technical editorial.",
            "Clinic lifestyle ad. Family at pediatric checkup, warm interaction, bright space. 'CARING FOR EVERY AGE' headline in clear upper zone. Warm editorial."
        ],
        "thumb": "Medical clinic landscape thumbnail. Modern clinic, doctor with tablet, natural light. 'YOUR HEALTH IS OUR PRIORITY' headline in clear space. Clean editorial."
    },
    {
        "slug": "gym-equipment-advertisement",
        "name": "Gym Equipment Brand",
        "posts": [
            "Premium gym equipment brand full-page ad. Peloton aesthetic. Sleek exercise bike in minimal bright home studio, woman mid-workout, daylight. 'TRAIN WITHOUT LIMITS' bold headline in clear space above. LIVE CLASSES · AI COACHING · STUDIO GRADE.",
            "Luxury gym equipment ad. Dumbbells on mirror finish rack in home gym, dramatic light. 'YOUR HOME GYM. PERFECTED.' headline in clear space above. Premium editorial.",
            "Gym equipment brand ad. Treadmill on white background, profile view, dramatic side light. 'RUN FURTHER AT HOME' headline in clear space above. Product editorial.",
            "Equipment lifestyle ad. Home gym setup: bench, weights, cable, rubber floor. 'BUILD YOUR BEST SELF' headline in clear space above. Athletic editorial."
        ],
        "thumb": "Gym equipment landscape thumbnail. Sleek exercise bike, minimal home studio, daylight. 'TRAIN WITHOUT LIMITS' headline in clear space. Premium editorial."
    },
    {
        "slug": "spa-beauty-salon-advertisement",
        "name": "Beauty Salon Spa",
        "posts": [
            "Luxury beauty salon full-page ad. Glossier aesthetic. Clean white salon interior, marble stations, fresh florals, natural light. 'YOUR BEAUTY. ELEVATED.' serif headline in clear space above. PREMIUM TREATMENTS · EXPERT STYLISTS · PERSONALIZED.",
            "Premium salon brand ad. Hairstylist finishing model's blowout, studio beauty lights, blurred. 'HAIR TRANSFORMED' headline in clear space above. Beauty editorial.",
            "Spa salon lifestyle ad. Client relaxing in facial chair, cucumber water, white linen, serene. 'INDULGE. REFRESH. GLOW.' headline in clear space above. Spa editorial.",
            "Salon brand ad. Beauty flatlay: brushes, palette, flowers on marble vanity. 'TOOLS OF ARTISTRY' headline in clear space above. Glamour editorial."
        ],
        "thumb": "Beauty salon landscape thumbnail. White salon interior, marble stations, fresh florals. 'YOUR BEAUTY. ELEVATED.' headline in clear space. Glossier editorial."
    },
    {
        "slug": "event-venue-advertisement",
        "name": "Event Venue",
        "posts": [
            "Premium event venue full-page ad. Soho House aesthetic. Grand industrial loft space set for gala: long tables, hanging Edison lights, florals. 'WHERE MOMENTS BECOME MEMORIES' serif headline in clear space above. CORPORATE · WEDDINGS · GALAS · INTIMATE.",
            "Luxury venue brand ad. Rooftop terrace set for evening event, city skyline at dusk, string lights. 'UNFORGETTABLE BY DESIGN' headline in clear sky above. Aspirational editorial.",
            "Event venue lifestyle ad. Guests arriving at grand venue entrance with valet, red carpet. 'ARRIVE. BE IMPRESSED.' headline in clear sky zone above. Prestigious editorial.",
            "Venue brand ad. Empty ballroom before event, perfect symmetry, mirror ball, dramatic light. 'THE STAGE IS YOURS' headline in clear space above. Editorial."
        ],
        "thumb": "Event venue landscape thumbnail. Grand loft set for gala, Edison lights, florals. 'WHERE MOMENTS BECOME MEMORIES' headline in clear space. Premium editorial."
    },
    {
        "slug": "security-brand-advertisement",
        "name": "Security Brand",
        "posts": [
            "Premium home security brand full-page ad. Ring aesthetic. Modern smart doorbell on clean white door, suburb home background, daylight. 'ALWAYS WATCHING. ALWAYS SAFE.' sans-serif headline in clear sky above. LIVE VIEW · NIGHT VISION · TWO-WAY AUDIO.",
            "Luxury security brand ad. Security camera on sleek mount, minimal editorial, night mode glow. 'PROTECT WHAT MATTERS' headline in clear dark space above. Clean editorial.",
            "Security lifestyle ad. Family entering home with phone unlocking smart lock, warm evening. 'HOME. SAFE. ALWAYS.' headline in clear space above. Warm editorial.",
            "Corporate security brand ad. Secure server room with biometric door, dramatic corridor light. 'YOUR DATA IS SACRED' headline in clear space above. Tech editorial."
        ],
        "thumb": "Security brand landscape thumbnail. Smart doorbell on white door, suburb home. 'ALWAYS WATCHING. ALWAYS SAFE.' headline in clear sky. Clean editorial."
    },
    {
        "slug": "courier-logistics-advertisement",
        "name": "Courier Logistics",
        "posts": [
            "Premium courier brand full-page ad. FedEx aesthetic. Delivery van on urban street at golden hour, package ready. 'DELIVERED ON TIME. EVERY TIME.' bold headline in clear space above. OVERNIGHT · TRACKING · GLOBAL · GUARANTEED.",
            "Logistics brand ad. Package on doorstep with notification on phone, satisfied customer. 'YOUR PACKAGE. OUR PROMISE.' headline in clear space above. Lifestyle editorial.",
            "Courier lifestyle ad. Cyclist courier in city, speed motion, package secure on back. 'FAST. RELIABLE. YOURS.' headline in clear space above. Urban editorial.",
            "Logistics brand ad. Warehouse with rows of packages ready for dispatch, organized. 'EFFICIENCY AT SCALE' headline in clear space above. Industrial editorial."
        ],
        "thumb": "Courier landscape thumbnail. Delivery van on urban street, golden hour. 'DELIVERED ON TIME. EVERY TIME.' headline in clear space. Urban editorial."
    },
    {
        "slug": "social-media-marketing-ad",
        "name": "Social Media Marketing",
        "posts": [
            "Premium digital marketing agency full-page ad. Social marketing aesthetic. Phone showing viral post metrics, rising graphs, confetti. 'GROW YOUR BRAND ONLINE' bold headline in clear space above. STRATEGY · CONTENT · ADS · ANALYTICS.",
            "Marketing agency brand ad. Marketing team at content shoot, ring light, flat lay prep. 'WE MAKE YOU SCROLL-STOPPING' headline in clear upper zone. Dynamic creative editorial.",
            "Digital agency lifestyle ad. Laptop with campaign dashboard, rising follower count, bright creative space. 'RESULTS. NOT EXCUSES.' headline in clear space above. Bold editorial.",
            "Social media brand ad. Phone with app icons, colorful content grid visible. 'YOUR AUDIENCE IS WAITING' headline in clear space above. Vibrant editorial."
        ],
        "thumb": "Social media agency landscape thumbnail. Phone with viral metrics, rising graphs. 'GROW YOUR BRAND ONLINE' headline in clear space. Dynamic editorial."
    },
    {
        "slug": "airline-lounge-advertisement",
        "name": "Airline Lounge",
        "posts": [
            "Premium airline lounge full-page ad. Cathay Pacific The Wing aesthetic. Serene lounge interior, floor-to-ceiling glass, city view, single person with champagne. 'THE JOURNEY STARTS HERE' serif headline in clear space above. SHOWER SPA · FINE DINING · QUIET ZONES.",
            "Luxury lounge brand ad. Barista crafting cocktail at lounge bar, ambient lighting. 'SIP BEFORE YOU FLY' headline in clear space above. Premium editorial.",
            "Airline lounge lifestyle ad. Traveler in cashmere sweater reading in deep chair, runway view. 'YOUR PRIVATE OASIS' headline in clear sky zone above. Aspirational editorial.",
            "Lounge brand ad. Full breakfast spread at window table, city view below. 'DINE BEFORE DEPARTURE' headline in clear space above. Premium editorial."
        ],
        "thumb": "Airline lounge landscape thumbnail. Serene lounge, floor-to-ceiling glass, champagne. 'THE JOURNEY STARTS HERE' headline in clear space. Luxe editorial."
    },
    {
        "slug": "vegan-restaurant-advertisement",
        "name": "Vegan Restaurant",
        "posts": [
            "Premium vegan restaurant full-page ad. Eleven Madison Park aesthetic. Beautifully plated plant-based dish, microgreens, colorful vegetables, white porcelain. 'PLANTS. REIMAGINED.' serif headline in clear space above. SEASONAL · ORGANIC · MICHELIN QUALITY.",
            "Vegan brand lifestyle ad. Buddha bowl overhead shot: grains, roasted vegetables, tahini, edible flowers. 'EAT THE RAINBOW' headline in clear space above. Vibrant food editorial.",
            "Vegan restaurant brand ad. Open kitchen: chef plating a stunning vegetable centerpiece dish. 'WHERE PLANTS ARE THE HERO' headline in clear space above. Editorial.",
            "Vegan dining ad. Restaurant interior, exposed brick, hanging plants, warm candles, full tables. 'GOOD FOOD. BETTER WORLD.' headline in clear upper zone. Warm editorial."
        ],
        "thumb": "Vegan restaurant landscape thumbnail. Plated plant-based dish, white porcelain. 'PLANTS. REIMAGINED.' headline in clear space. Editorial."
    },
    {
        "slug": "indian-restaurant-advertisement",
        "name": "Indian Restaurant",
        "posts": [
            "Premium Indian restaurant full-page ad. Dishoom aesthetic. Butter chicken in copper karahi on dark wooden table, garlic naan beside, rose petals. 'TASTE THE SUBCONTINENT' serif headline in clear space above. TRADITIONAL RECIPES · FINEST SPICES · OPEN KITCHEN.",
            "Luxury Indian cuisine ad. Biryani domed presentation being lifted in ornate copper pot, saffron rice visible, steam. 'EVERY GRAIN TELLS A STORY' headline in clear space above. Heritage editorial.",
            "Indian restaurant lifestyle ad. Vibrant masala selection in brass bowls on dark stone. 'SPICED TO PERFECTION' headline in clear space above. Color editorial.",
            "Indian dining brand ad. Candlelit table for two with Indian feast spread, warm restaurant. 'AN EVENING IN INDIA' headline in clear upper zone. Warm editorial."
        ],
        "thumb": "Indian restaurant landscape thumbnail. Butter chicken in copper karahi, rose petals. 'TASTE THE SUBCONTINENT' headline in clear space. Heritage editorial."
    },
    {
        "slug": "chinese-restaurant-advertisement",
        "name": "Chinese Restaurant",
        "posts": [
            "Premium Chinese restaurant full-page ad. Hakkasan aesthetic. Peking duck being carved on dark lacquered table, dramatic overhead light. 'ANCIENT FLAVORS. MODERN CRAFT.' serif headline in clear space above. DIM SUM · PEKING DUCK · PRIVATE DINING.",
            "Luxury dim sum brand ad. Bamboo steamers with har gow and siu mai on dark stone surface, soy sauce dish. 'THE ART OF DIM SUM' headline in clear space above. Dark editorial.",
            "Chinese cuisine lifestyle ad. Family-style feast around lazy Susan, multiple dishes, celebration. 'GATHER AROUND' headline in clear upper zone. Warm editorial.",
            "Chinese restaurant brand ad. Red lanterns hanging above dishes in dark atmospheric dining room. 'TRADITION IN EVERY BITE' headline in clear space above. Atmospheric editorial."
        ],
        "thumb": "Chinese restaurant landscape thumbnail. Peking duck carved on lacquered table, spotlight. 'ANCIENT FLAVORS. MODERN CRAFT.' headline in clear space. Dark editorial."
    },
    {
        "slug": "thai-restaurant-advertisement",
        "name": "Thai Restaurant",
        "posts": [
            "Premium Thai restaurant full-page ad. Gaggan aesthetic. Tom kha gai soup in dark bowl with lemongrass, kaffir lime, chili oil swirl. 'THE SOUL OF THAILAND' serif headline in clear space above. AUTHENTIC RECIPES · THAI HERBS · LIVE KITCHEN.",
            "Thai cuisine brand ad. Pad thai in wok, smoke rising, fresh bean sprouts and lime wedge. 'STREET FOOD PERFECTED' headline in clear space above. Vibrant editorial.",
            "Thai dining lifestyle ad. Thai green curry in coconut bowl, orchid garnish, warm candlelit dinner. 'FLAVORS THAT TRANSPORT' headline in clear space above. Exotic editorial.",
            "Thai restaurant brand ad. Appetizer arrangement: spring rolls, satay, peanut sauce on dark slate. 'THE PERFECT BEGINNING' headline in clear dark space above. Dark editorial."
        ],
        "thumb": "Thai restaurant landscape thumbnail. Tom kha gai in dark bowl, lemongrass, lime. 'THE SOUL OF THAILAND' headline in clear space. Exotic editorial."
    },
    {
        "slug": "mexican-restaurant-advertisement",
        "name": "Mexican Restaurant",
        "posts": [
            "Premium Mexican restaurant full-page ad. Cosme aesthetic. Perfectly plated duck carnitas taco on stone surface, pickled onion, micro herbs. 'MEXICO. REIMAGINED.' serif headline in clear space above. MEZCAL BAR · SEASONAL MENU · MARKET FRESH.",
            "Artisan Mexican cuisine ad. Street taco al pastor on corn tortilla with pineapple, cilantro, on dark surface. 'BORN ON THE STREETS' headline in clear space above. Authentic editorial.",
            "Mexican dining lifestyle ad. Table spread of guacamole, tacos, enchiladas, margaritas. 'FIESTA EVERY NIGHT' headline in clear upper zone. Vibrant editorial.",
            "Mexican restaurant brand ad. Mezcal smoky pour into glass, agave plant beside, dark moody bar setting. 'SMOKE AND SPIRIT' headline in clear dark space above. Dark editorial."
        ],
        "thumb": "Mexican restaurant landscape thumbnail. Duck carnitas taco on stone, pickled onion. 'MEXICO. REIMAGINED.' headline in clear space. Modern editorial."
    },
    {
        "slug": "italian-restaurant-advertisement",
        "name": "Italian Restaurant",
        "posts": [
            "Premium Italian restaurant full-page ad. Osteria Francescana aesthetic. House-made pasta with truffle shaved tableside on white porcelain. 'LA DOLCE VITA' elegant serif headline in clear space above. HANDMADE PASTA · WINE CELLAR · GARDEN TO TABLE.",
            "Italian cuisine brand ad. Tiramisu in glass with espresso poured beside, marble surface. 'DESSERT AS IT SHOULD BE' headline in clear space above. Classic editorial.",
            "Italian dining lifestyle ad. Candlelit trattoria table with wine, breadbasket, couple in soft focus. 'EVENINGS MADE IN ITALY' headline in clear upper zone. Warm romantic editorial.",
            "Italian restaurant brand ad. Wood-fired oven with glowing fire, pizzaiolo in white, artisan craft. 'FIRED WITH PASSION' headline in clear space above. Rustic editorial."
        ],
        "thumb": "Italian restaurant landscape thumbnail. Truffle pasta on white porcelain, elegant plating. 'LA DOLCE VITA' headline in clear space. Refined editorial."
    },
    {
        "slug": "mediterranean-restaurant-ad",
        "name": "Mediterranean Restaurant",
        "posts": [
            "Premium Mediterranean restaurant full-page ad. Noura aesthetic. Mezze spread: hummus, baba ganoush, tabouleh, warm pita on blue ceramic. 'A FEAST FROM THE SEA' serif headline in clear space above. FRESH DAILY · SHARING PLATES · OLIVE OIL PRESSED IN HOUSE.",
            "Mediterranean cuisine ad. Whole sea bass on rock salt in cast iron, lemon, olives. 'FROM THE SEA TO YOUR TABLE' headline in clear space above. Editorial.",
            "Mediterranean lifestyle ad. Outdoor terrace dining, white linen, olive tree, Santorini aesthetic. 'DINE LIKE THE GODS' headline in clear sky zone. Aspirational editorial.",
            "Mediterranean brand ad. Flatbread with za'atar, olive oil pour, herbs. 'SIMPLE IS PERFECT' headline in clear space above. Clean editorial."
        ],
        "thumb": "Mediterranean restaurant landscape thumbnail. Mezze spread on blue ceramic, fresh vibrant. 'A FEAST FROM THE SEA' headline in clear space. Editorial."
    },
    {
        "slug": "steakhouse-advertisement",
        "name": "Steakhouse Brand",
        "posts": [
            "Premium steakhouse full-page ad. Nobu Matsuhisa aesthetic. A5 wagyu ribeye on black cast iron, resting, dramatic sear marks, rosemary. 'THE FINEST CUT' bold serif headline in clear dark space above. DRY AGED · WOOD FIRED · SOMMELIER PAIRING.",
            "Luxury steak brand ad. Wagyu steak cross-section showing marbling, on slate, pepper sauce. 'MARBLING IS EVERYTHING' headline in clear space above. Dark culinary editorial.",
            "Steakhouse lifestyle ad. Suited couple at steakhouse table, sommelier presenting red wine, candlelit. 'AN EVENING WORTH SAVORING' headline in clear upper zone. Prestigious editorial.",
            "Steak brand ad. Bone-in ribeye emerging from wood-fire oven, flame visible, chef's hands with tongs. 'FIRED TO PERFECTION' headline in clear space above. Dramatic editorial."
        ],
        "thumb": "Steakhouse landscape thumbnail. A5 wagyu ribeye on cast iron, dramatic sear. 'THE FINEST CUT' headline in clear dark space. Dark editorial."
    },
    {
        "slug": "grocery-supermarket-advertisement",
        "name": "Grocery Supermarket",
        "posts": [
            "Premium grocery brand full-page ad. Eataly aesthetic. Abundance of colorful fresh produce arranged artfully, farmers market energy. 'FRESH. EVERY. DAY.' serif headline in clear space above. LOCALLY SOURCED · ORGANIC · FAMILY OWNED.",
            "Grocery lifestyle brand ad. Family choosing fresh bread at artisan bakery counter inside store. 'FOOD YOU CAN TRUST' headline in clear upper zone. Warm editorial.",
            "Supermarket brand ad. Fresh fish counter: whole salmon, oysters, lobster on ice. 'FROM THE SEA TO YOUR CART' headline in clear space above. Premium food editorial.",
            "Grocery brand ad. Seasonal produce harvest flatlay on wood: pumpkins, squash, apples, pears. 'THE BEST OF THE SEASON' headline in clear space above. Autumnal editorial."
        ],
        "thumb": "Grocery supermarket landscape thumbnail. Colorful fresh produce artfully arranged. 'FRESH. EVERY. DAY.' headline in clear space. Market editorial."
    },
    {
        "slug": "toy-brand-advertisement",
        "name": "Toy Brand",
        "posts": [
            "Premium toy brand full-page ad. LEGO aesthetic. Elaborate LEGO city build on white table, child's hands adding final piece, natural light. 'BUILD ANYTHING. IMAGINE EVERYTHING.' bold headline in clear space above. EDUCATIONAL · SAFE · AWARD WINNING.",
            "Luxury toy brand ad. Wooden toy train set on oak floor, child's feet in socks playing, warm home. 'PLAY THAT LASTS FOREVER' headline in clear space above. Warm editorial.",
            "Toy brand lifestyle ad. Art supply kit: paints, brushes, drawing pads on child's desk, creative mess. 'UNLEASH THEIR CREATIVITY' headline in clear space above. Colorful editorial.",
            "Premium toy ad. Stuffed animal bear beautifully presented in gift box with ribbon. 'THE PERFECT GIFT' headline in clear space above. Gift editorial."
        ],
        "thumb": "Toy brand landscape thumbnail. LEGO city build, child's hands adding piece. 'BUILD ANYTHING. IMAGINE EVERYTHING.' headline in clear space. Bright editorial."
    },
    {
        "slug": "plant-nursery-advertisement",
        "name": "Plant Nursery",
        "posts": [
            "Premium plant nursery full-page ad. Terrain aesthetic. Lush monstera in terra cotta pot on marble plant stand, warm natural light. 'BRING LIFE HOME' serif headline in clear space above. RARE VARIETIES · EXPERT CARE GUIDES · SAME DAY DELIVERY.",
            "Plant shop brand ad. Collection of succulents in ceramic pots arranged on white shelf. 'LOW MAINTENANCE. HIGH STYLE.' headline in clear space above. Clean editorial.",
            "Nursery lifestyle ad. Person repotting a large fiddle leaf fig, studio loft, golden light. 'YOUR GREEN SPACE AWAITS' headline in clear space above. Lifestyle editorial.",
            "Plant brand ad. Hanging pothos and trailing ivy in sunroom, botanical abundance. 'URBAN JUNGLE STARTER KIT' headline in clear space above. Botanical editorial."
        ],
        "thumb": "Plant nursery landscape thumbnail. Monstera in terra cotta on marble stand, warm light. 'BRING LIFE HOME' headline in clear space. Botanical editorial."
    },
    {
        "slug": "coffee-beans-roaster-ad",
        "name": "Coffee Roaster",
        "posts": [
            "Premium coffee roaster brand full-page ad. Intelligentsia aesthetic. Fresh roasted beans spilling from kraft bag onto dark oak, steam rising. 'ROASTED WITH OBSESSION' serif headline in clear space above. SINGLE ORIGIN · DIRECT TRADE · SMALL BATCH.",
            "Artisan coffee roaster ad. Open roaster drum at peak roast, beans tumbling, fire below, warehouse. 'THE PERFECT ROAST IS AN ART' headline in clear space above. Industrial editorial.",
            "Coffee bean brand lifestyle ad. Cupping table: small cups, beans, aroma moment, roaster in background. 'TASTE EVERY NOTE' headline in clear space above. Professional editorial.",
            "Roaster brand ad. Coffee bag with beautiful illustrated label on marble beside grinder. 'CRAFTED FOR CONNOISSEURS' headline in clear space above. Premium editorial."
        ],
        "thumb": "Coffee roaster landscape thumbnail. Fresh roasted beans spilling from kraft bag, steam. 'ROASTED WITH OBSESSION' headline in clear space. Dark editorial."
    },
    {
        "slug": "cocktail-bar-advertisement",
        "name": "Cocktail Bar",
        "posts": [
            "Premium cocktail bar full-page ad. NoMad Bar aesthetic. Signature cocktail in crystal coupe, smoke under glass dome, dark mahogany bar. 'CRAFTED FOR YOUR PLEASURE' serif headline in clear dark space above. CRAFT SPIRITS · BESPOKE COCKTAILS · MIXOLOGY MASTERS.",
            "Luxury bar brand ad. Bartender's hands finishing a cocktail garnish, precision, bokeh bar behind. 'EVERY DRINK A STORY' headline in clear upper zone. Dark editorial.",
            "Cocktail bar lifestyle ad. Group of friends in upscale bar, clinking cocktails, city view. 'WHERE THE NIGHT BEGINS' headline in clear space above. Vibrant editorial.",
            "Bar brand ad. Line of craft cocktails on marble bar top, each unique. 'THE ART OF THE POUR' headline in clear dark space above. Dark editorial."
        ],
        "thumb": "Cocktail bar landscape thumbnail. Signature cocktail under smoke dome, dark mahogany. 'CRAFTED FOR YOUR PLEASURE' headline in clear dark space. Dark editorial."
    },
    {
        "slug": "museum-cultural-advertisement",
        "name": "Museum Cultural",
        "posts": [
            "Premium museum full-page ad. MoMA aesthetic. Grand gallery hall, dramatic artwork on white wall, single visitor in awe. 'ART CHANGES EVERYTHING' serif headline in clear space above. PERMANENT COLLECTION · EXHIBITIONS · CURATED TOURS.",
            "Museum brand ad. Sculpture gallery at dusk, statues dramatically lit, marble floors. 'EXPERIENCE HISTORY' headline in clear space above. Editorial.",
            "Cultural institution ad. Visitor studying renaissance painting close-up, dramatic gallery light. 'EVERY VISIT A DISCOVERY' headline in clear upper zone. Editorial.",
            "Museum lifestyle ad. Café inside museum with skylight, artworks visible, people conversing. 'CULTURE. COMMUNITY. CAFÉ.' headline in clear space above. Warm editorial."
        ],
        "thumb": "Museum landscape thumbnail. Grand gallery hall, artwork on white wall, single visitor. 'ART CHANGES EVERYTHING' headline in clear space. Editorial."
    },
    {
        "slug": "cinema-entertainment-advertisement",
        "name": "Cinema Entertainment",
        "posts": [
            "Premium cinema brand full-page ad. Alamo Drafthouse aesthetic. Empty luxury cinema hall, recliner seats, giant glowing screen, perfect lighting. 'MOVIES LIKE THEY WERE MEANT TO BE SEEN' headline in clear screen space above. DOLBY ATMOS · RECLINERS · DINE-IN.",
            "Luxury cinema brand ad. Popcorn in premium branded box beside giant soda, dark theatre glow. 'THE COMPLETE EXPERIENCE' headline in clear dark space above. Cinematic editorial.",
            "Cinema lifestyle ad. Couple in recliners, laughing at screen, cocktails, gourmet snacks. 'DATE NIGHT. PERFECTED.' headline in clear upper zone. Warm editorial.",
            "Cinema brand ad. Film reel detail, bokeh cinema lights behind, nostalgia. 'STORIES THAT LAST FOREVER' headline in clear space above. Cinematic editorial."
        ],
        "thumb": "Cinema landscape thumbnail. Empty luxury hall, recliner seats, glowing screen. 'MOVIES LIKE THEY WERE MEANT TO BE SEEN' headline in clear space. Cinematic editorial."
    },
    {
        "slug": "sports-team-advertisement",
        "name": "Sports Team Brand",
        "posts": [
            "Premium sports team full-page ad. Nike FC aesthetic. Player silhouette against floodlit stadium at night, crowd energy. 'PLAY FOR MORE THAN THE GAME' bold headline in clear sky zone above. SEASON TICKETS · HOSPITALITY · MERCHANDISE.",
            "Sports brand lifestyle ad. Team jersey on hanger, stadium in soft focus behind, premium presentation. 'WEAR THE BADGE' headline in clear space above. Premium sports editorial.",
            "Sports team culture ad. Training ground: players in drill, early morning light, mist. 'CHAMPIONS ARE MADE AT DAWN' headline in clear mist zone. Cinematic editorial.",
            "Sports team ad. Trophy close-up on pedestal, stadium lights behind. 'FOR THE GLORY' headline in clear space above. Iconic editorial."
        ],
        "thumb": "Sports team landscape thumbnail. Player silhouette, floodlit stadium at night, crowd. 'PLAY FOR MORE THAN THE GAME' headline in clear sky. Cinematic editorial."
    },
    {
        "slug": "fashion-accessories-advertisement",
        "name": "Fashion Accessories",
        "posts": [
            "Luxury fashion accessories full-page ad. Gucci aesthetic. Silk scarf elegantly arranged on white marble, dramatic fold, soft natural light. 'DETAILS DEFINE ELEGANCE' serif headline in clear space above. ITALIAN SILK · HAND ROLLED · LIMITED EDITION.",
            "Premium accessories brand ad. Belt, cufflinks, tie bar arranged on dark leather surface. 'THE FINISHING TOUCH' headline in clear dark space above. Masculine editorial.",
            "Luxury hat brand ad. Fedora hat on marble surface, dramatic side light, texture. 'WEAR YOUR CHARACTER' headline in clear space above. Editorial.",
            "Fashion accessories ad. Elegant flat lay: gloves, hat, silk scarf, sunglasses on beige linen. 'THE COMPLETE LOOK' headline in clear space above. Fashion editorial."
        ],
        "thumb": "Fashion accessories landscape thumbnail. Silk scarf on white marble, dramatic fold. 'DETAILS DEFINE ELEGANCE' headline in clear space. Gucci editorial."
    },
    {
        "slug": "streetwear-brand-advertisement",
        "name": "Streetwear Brand",
        "posts": [
            "Premium streetwear brand full-page ad. Supreme aesthetic. Limited edition hoodie on dark concrete, dramatic edge lighting. 'DROP DAY' bold sans-serif headline in clear dark space above. LIMITED RUN · HAND SCREENED · CULTURE FIRST.",
            "Streetwear lifestyle brand ad. Young person in oversized graphic tee, urban concrete backdrop. 'WEAR YOUR IDENTITY' headline in clear upper zone. Urban editorial.",
            "Street fashion brand ad. Sneakers, joggers, cap flat lay on graffiti concrete. 'THE UNIFORM OF THE STREETS' headline in clear space above. Urban editorial.",
            "Streetwear culture ad. Group of friends in streetwear outside a vibrant mural wall. 'COMMUNITY IS THE BRAND' headline in clear space above. Dynamic editorial."
        ],
        "thumb": "Streetwear landscape thumbnail. Limited hoodie on dark concrete, edge lighting. 'DROP DAY' headline in clear dark space. Urban editorial."
    },
    {
        "slug": "financial-planning-advertisement",
        "name": "Financial Planning",
        "posts": [
            "Premium financial planning brand full-page ad. Vanguard aesthetic. Upward sloping graph on minimal screen on clean desk, plant. 'YOUR FINANCIAL FUTURE. SECURED.' serif headline in clear space above. RETIREMENT · INVESTING · WEALTH PLANNING.",
            "Financial brand ad. Mature couple reviewing plan with advisor at home, warm trust. 'PLANNING TOGETHER' headline in clear space above. Warm editorial.",
            "Investment brand ad. Hourglass with gold coins flowing, time is money concept. 'INVEST IN TIME' headline in clear space above. Abstract editorial.",
            "Financial lifestyle ad. Young professional at home reviewing portfolio on tablet, morning. 'START EARLY. WIN LATER.' headline in clear space above. Aspirational editorial."
        ],
        "thumb": "Financial planning landscape thumbnail. Upward graph on minimal screen, clean desk. 'YOUR FINANCIAL FUTURE. SECURED.' headline in clear space. Clean editorial."
    },
    {
        "slug": "recruitment-hr-advertisement",
        "name": "Recruitment HR Brand",
        "posts": [
            "Premium recruitment brand full-page ad. LinkedIn aesthetic. Confident professional in modern office, natural light, urban view. 'YOUR NEXT CHAPTER STARTS HERE' serif headline in clear space above. TOP EMPLOYERS · CAREER COACHING · GLOBAL REACH.",
            "HR brand lifestyle ad. Interview moment: candidate and interviewer, warm handshake, glass office. 'THE RIGHT FIT. EVERY TIME.' headline in clear upper zone. Professional editorial.",
            "Recruitment brand ad. Job offer letter on desk with coffee, excited hands holding. 'THE CALL YOU'VE BEEN WAITING FOR' headline in clear space above. Warm editorial.",
            "HR firm ad. Diverse team collaborating at modern office table, energy. 'GREAT TEAMS START HERE' headline in clear upper space. Dynamic editorial."
        ],
        "thumb": "Recruitment landscape thumbnail. Confident professional in modern office, natural light. 'YOUR NEXT CHAPTER STARTS HERE' headline in clear space. Editorial."
    },
    {
        "slug": "cleaning-products-advertisement",
        "name": "Cleaning Products",
        "posts": [
            "Premium cleaning brand full-page ad. Method aesthetic. Three sleek cleaning product bottles on white marble in sunlight. 'CLEAN. NATURALLY.' sans-serif headline in clear space above. PLANT-DERIVED · BIODEGRADABLE · CRUELTY FREE.",
            "Luxury cleaning brand ad. Kitchen after cleaning: marble surfaces gleaming, fresh lemon, morning light. 'SPOTLESS. EVERY TIME.' headline in clear space above. Clean editorial.",
            "Cleaning brand lifestyle ad. Happy family in clean bright kitchen after cleanup. 'CLEAN HOME. HAPPY LIFE.' headline in clear upper zone. Warm editorial.",
            "Cleaning product ad. Single spray bottle on white with lemon and eucalyptus. 'PURE CLEAN' headline in clear space above. Minimal wellness editorial."
        ],
        "thumb": "Cleaning products landscape thumbnail. Three sleek bottles on marble in sunlight. 'CLEAN. NATURALLY.' headline in clear space. Clean editorial."
    },
    {
        "slug": "book-publishing-advertisement",
        "name": "Book Publishing",
        "posts": [
            "Premium book publisher full-page ad. Penguin Classics aesthetic. Stack of five hardcover books with embossed spines on dark wood, warm library light. 'STORIES THAT SHAPE THE WORLD' serif headline in clear space above. BESTSELLERS · CLASSICS · NEW VOICES.",
            "Publishing brand ad. New hardcover book being opened, pages fanning, golden ratio composition. 'OPEN YOUR NEXT WORLD' headline in clear space above. Editorial.",
            "Book publisher lifestyle ad. Author at writing desk, typewriter, manuscript, warm lamp. 'FROM IDEA TO SHELF' headline in clear upper zone. Heritage editorial.",
            "Publishing ad. Book covers displayed like gallery art on white wall. 'COLLECTED STORIES' headline in clear space above. Gallery editorial."
        ],
        "thumb": "Book publisher landscape thumbnail. Hardcover stack on dark wood, warm library light. 'STORIES THAT SHAPE THE WORLD' headline in clear space. Editorial."
    },
    {
        "slug": "magazine-media-advertisement",
        "name": "Magazine Media",
        "posts": [
            "Premium magazine brand full-page ad. Vogue aesthetic. Magazine laid open to fashion editorial on marble desk beside champagne. 'THE DEFINITIVE WORD' serif headline in clear space above. MONTHLY ISSUES · DIGITAL · ARCHIVE ACCESS.",
            "Media brand lifestyle ad. Journalist at laptop on rooftop, city behind, golden hour. 'STORIES WORTH TELLING' headline in clear space above. Aspirational editorial.",
            "Magazine culture ad. Stack of back issues of premium magazine on coffee table. 'COLLECT CULTURE' headline in clear space above. Editorial.",
            "Magazine brand ad. Editor reviewing layout proofs in bright studio, magazine covers visible. 'WE SET THE STANDARD' headline in clear space above. Professional editorial."
        ],
        "thumb": "Magazine landscape thumbnail. Open magazine on marble desk, champagne. 'THE DEFINITIVE WORD' headline in clear space. Vogue editorial."
    },
    {
        "slug": "eco-sustainable-brand-ad",
        "name": "Eco Sustainable Brand",
        "posts": [
            "Premium eco brand full-page ad. Patagonia aesthetic. Reusable product line on natural wood surface, plant, stone, earthy tones. 'MADE FOR THE PLANET' serif headline in clear space above. RECYCLED MATERIALS · CARBON NEUTRAL · B-CORP.",
            "Sustainable brand lifestyle ad. Person in sustainable fashion on coastal cliff, wildflowers, blue ocean. 'WEAR THE CHANGE' headline in clear sky zone. Aspirational editorial.",
            "Eco brand ad. Hands planting tree seedling in soil, sunlight. 'EVERY PURCHASE PLANTS A TREE' headline in clear space above. Earth editorial.",
            "Sustainable product ad. Zero-waste packaging: paper, bamboo, glass on white. 'PACKAGING THAT DISAPPEARS' headline in clear space above. Clean editorial."
        ],
        "thumb": "Eco brand landscape thumbnail. Reusable products on natural wood, earthy tones. 'MADE FOR THE PLANET' headline in clear space. Earthy editorial."
    },
]

# ── Logo overlay ──────────────────────────────────────────────────────────────
def add_logo(image_path):
    img  = Image.open(image_path).convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")
    lw   = int(img.width * LOGO_RATIO)
    lh   = int(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    img.paste(logo, (img.width - lw - MARGIN, MARGIN), logo)
    img.convert("RGB").save(image_path, "PNG", optimize=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
import re as _re
import json as _json

# ── API request capture + replay ──────────────────────────────────────────────
# Strategy: capture the real generate API call from 1 manual click,
# then replay it for all 530 images — guaranteed 0 credits if manual was free.

async def capture_generate_request(page):
    """
    Ask user to manually click Generate ONCE with Unlimited ON.
    Capture the exact POST request Higgsfield makes.
    Returns captured request dict or None.
    """
    captured = {}

    def on_request(request):
        url = request.url
        method = request.method
        # Higgsfield generate endpoint patterns
        if method == "POST" and any(k in url for k in [
            "/generate", "/inference", "/image", "/create", "/run"
        ]) and "higgsfield" in url:
            pd = request.post_data
            if pd:
                captured["url"] = url
                captured["headers"] = dict(request.headers)
                captured["body"] = pd
                print(f"\n  ✅ CAPTURED: {url}")
                print(f"  Body preview: {pd[:200]}")

    page.on("request", on_request)

    print("\n" + "="*60)
    print("  STEP 1: Chrome madhe Unlimited toggle ON karo (green)")
    print("  STEP 2: Kontaahi prompt type karo (test prompt)")
    print("  STEP 3: Generate / Unlimited ✦ button MANUALLY click karo")
    print("  STEP 4: Image generate hoayla lagu de (5-10 sec)")
    print("  STEP 5: Khali Terminal madhe Enter daba")
    print("="*60)
    input("  → Generate click kela ki Enter daba: ")

    page.remove_listener("request", on_request)

    if not captured:
        print("\n  ⚠️  No API request captured.")
        print("  All buttons on page:")
        btns = await page.evaluate("""() =>
            [...document.querySelectorAll('button')].map(b => ({
                text: b.textContent.trim().substring(0, 40),
                w: Math.round(b.getBoundingClientRect().width),
                h: Math.round(b.getBoundingClientRect().height),
                x: Math.round(b.getBoundingClientRect().right),
                visible: b.offsetParent !== null
            })).filter(b => b.text && b.visible)
        """)
        for b in btns:
            print(f"    [{b['w']}x{b['h']} @x={b['x']}] '{b['text']}'")
        return None

    return captured


def _extract_url_from_response(text):
    """Find image URL in API response text (JSON or raw)."""
    # Try JSON parse first
    try:
        data = _json.loads(text)
    except Exception:
        # Raw text — regex for image URLs
        hits = _re.findall(r'https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)[^\s"\'<>]*', text)
        for u in hits:
            if "cloudfront" in u or "higgsfield" in u:
                return u
        return None

    def _search(obj, depth=0):
        if depth > 8:
            return None
        if isinstance(obj, str):
            if obj.startswith("http") and any(e in obj for e in [".png", ".jpg", ".jpeg", ".webp"]):
                return obj
            return None
        if isinstance(obj, dict):
            # Priority keys first
            for k in ["url", "image_url", "output_url", "file_url", "download_url",
                       "output", "result", "src", "image", "media_url", "video_url"]:
                if k in obj:
                    r = _search(obj[k], depth + 1)
                    if r:
                        return r
            for v in obj.values():
                r = _search(v, depth + 1)
                if r:
                    return r
        if isinstance(obj, list):
            for item in obj:
                r = _search(item, depth + 1)
                if r:
                    return r
        return None

    return _search(data)


def _extract_job_id(text):
    """Find job/task ID in JSON response."""
    try:
        data = _json.loads(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    for k in ["job_id", "id", "task_id", "inference_id",
              "generation_id", "run_id", "request_id", "jobId"]:
        v = data.get(k)
        if v and isinstance(v, str):
            return v
    return None


def _extract_status_url(text):
    """Find explicit status/polling URL in JSON response."""
    try:
        data = _json.loads(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    for k in ["status_url", "poll_url", "result_url", "check_url", "tracking_url"]:
        v = data.get(k)
        if v and isinstance(v, str) and v.startswith("http"):
            return v
    return None


async def _poll_job_status(page, captured, job_id):
    """Poll Higgsfield status endpoint until image URL found (3 min max)."""
    base_url = captured["url"]
    domain_m = _re.match(r'(https?://[^/]+)', base_url)
    domain    = domain_m.group(1) if domain_m else ""

    # Strip auth + content headers for GET requests
    get_hdrs = {k: v for k, v in captured["headers"].items()
                if k.lower() not in ("content-length", "content-type")}

    # Candidate status endpoints
    status_paths = [
        f"/api/inference/{job_id}",
        f"/api/inference/{job_id}/status",
        f"/api/job/{job_id}",
        f"/api/jobs/{job_id}",
        f"/api/status/{job_id}",
        f"/api/task/{job_id}",
        f"/api/generation/{job_id}",
        f"/api/v1/inference/{job_id}",
        f"/api/v1/job/{job_id}",
        f"/api/v1/generation/{job_id}",
    ]
    # Also try the same URL but GET with job_id appended
    gen_path = _re.sub(r'https?://[^/]+', '', base_url)
    status_paths.insert(0, f"{gen_path.rstrip('/')}/{job_id}")

    working_path = None  # remember which path actually responds

    for attempt in range(60):  # 60 × 3s = 3 min
        await page.wait_for_timeout(3000)

        paths_to_try = [working_path] if working_path else status_paths

        for spath in paths_to_try:
            try:
                sresp = await page.request.get(domain + spath, headers=get_hdrs)
                if not sresp.ok:
                    continue
                stext = await sresp.text()
                working_path = spath  # lock in the working path

                if attempt % 5 == 0 or attempt == 0:
                    print(f"\n  poll[{attempt}] {spath}: {stext[:250]}")
                else:
                    print(".", end="", flush=True)

                # Check for terminal failure
                try:
                    sdata = _json.loads(stext)
                    st = str(sdata.get("status", "")).lower()
                    if st in ("failed", "error", "cancelled", "rejected"):
                        print(f"\n  ❌ Job {job_id} failed: status={st}")
                        return None
                except Exception:
                    pass

                img_url = _extract_url_from_response(stext)
                if img_url:
                    print(f"\n  ✅ Image ready: {img_url[:80]}")
                    return img_url
            except Exception:
                pass

    print("\n  ⏱  poll timeout — no image URL after 3 min")
    return None


async def replay_generate(page, captured, prompt, aspect_ratio):
    """
    Replay captured generate POST with new prompt + ratio.
    Returns image URL or None.
    """
    url = captured["url"]
    headers = {k: v for k, v in captured["headers"].items()
               if k.lower() not in ("content-length",)}

    # Parse and patch body
    try:
        body = _json.loads(captured["body"])
    except Exception:
        body = captured["body"]

    if isinstance(body, dict):
        for k in ["prompt", "text", "description", "input"]:
            if k in body:
                body[k] = prompt
                break
        for k in ["aspect_ratio", "aspectRatio", "ratio", "size"]:
            if k in body:
                body[k] = aspect_ratio
                break
        # Force 4k resolution
        for k in ["resolution", "quality", "output_quality"]:
            if k in body:
                body[k] = IMAGE_RESOLUTION
                break
        else:
            body["resolution"] = IMAGE_RESOLUTION
        body_str = _json.dumps(body)
    else:
        body_str = _re.sub(r'"prompt"\s*:\s*"[^"]*"',
                           f'"prompt": "{prompt.replace(chr(34), chr(39))}"',
                           str(body))

    # ── Fire the POST ─────────────────────────────────────────────────────────
    try:
        resp     = await page.request.fetch(url, method="POST",
                                            headers=headers, data=body_str)
        resp_status = resp.status
        resp_text   = await resp.text()
        print(f"  API status : {resp_status}")
        print(f"  API resp   : {resp_text[:400]}")
        if resp_status not in (200, 201, 202):
            print(f"  ⛔ Non-2xx — skipping")
            return None
    except Exception as e:
        print(f"  replay fetch error: {e}")
        return None

    # ── 1. Direct URL in response body ───────────────────────────────────────
    image_url = _extract_url_from_response(resp_text)
    if image_url:
        print(f"  ✅ Immediate URL: {image_url[:80]}")
        return image_url

    # ── 2. Explicit status/poll URL ───────────────────────────────────────────
    status_url = _extract_status_url(resp_text)
    if status_url:
        print(f"  Status URL: {status_url}")
        job_id = _extract_job_id(resp_text) or "direct"
        # poll via that URL directly
        domain_m = _re.match(r'(https?://[^/]+)', status_url)
        domain   = domain_m.group(1) if domain_m else ""
        get_hdrs = {k: v for k, v in headers.items()
                    if k.lower() not in ("content-length", "content-type")}
        for _ in range(60):
            await page.wait_for_timeout(3000)
            try:
                sr = await page.request.get(status_url, headers=get_hdrs)
                if sr.ok:
                    st = await sr.text()
                    iu = _extract_url_from_response(st)
                    if iu:
                        return iu
            except Exception:
                pass
        return None

    # ── 3. Job ID → poll status endpoint ─────────────────────────────────────
    job_id = _extract_job_id(resp_text)
    if job_id:
        print(f"  Job ID: {job_id}")
        return await _poll_job_status(page, captured, job_id)

    # ── 4. DOM fallback (image appears in UI) ─────────────────────────────────
    print(f"  No URL/job in response — watching DOM (3 min max)...")
    for _ in range(180):
        await page.wait_for_timeout(1000)
        try:
            el = page.locator("img[src*='cloudfront'][src*='.png']").first
            if await el.is_visible(timeout=300):
                candidate = await el.get_attribute("src")
                if candidate and "min" not in candidate:
                    return candidate
        except Exception:
            pass

    print("  ❌ DOM fallback timed out")
    return None


# ── Single image generate (used in loop) ─────────────────────────────────────
async def generate_image(page, prompt, aspect_ratio, save_path, captured_req):
    """Replay captured API request with new prompt+ratio, download, add logo."""

    # Append quality booster suffix to every prompt
    enhanced_prompt = prompt.rstrip(".").rstrip(",") + QUALITY_SUFFIX

    image_url = await replay_generate(page, captured_req, enhanced_prompt, aspect_ratio)

    if not image_url:
        print("FAILED — no image URL")
        return False

    print("done")

    # Download via browser context (handles auth cookies)
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = await page.request.get(image_url)
        if resp.ok:
            save_path.write_bytes(await resp.body())
        else:
            print(f"  Download HTTP {resp.status} — trying with referer...")
            import urllib.request as _ur
            req = _ur.Request(image_url, headers={"Referer": "https://higgsfield.ai/"})
            with _ur.urlopen(req) as r:
                save_path.write_bytes(r.read())
    except Exception as e:
        print(f"  Download error: {e}")
        return False

    add_logo(save_path)
    print(f"  ✓ {save_path.name}")
    return True


async def main():
    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    async with async_playwright() as p:
        # Launch Chrome with separate profile (won't conflict with existing Chrome)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--password-store=basic",   # no keychain prompt
                "--use-mock-keychain",
            ],
            no_viewport=True,
        )

        # Prefer existing Higgsfield tab; fall back to first page or new page
        print("\n🌐 Selecting page...")
        all_pages = browser.pages
        print(f"   Open tabs: {len(all_pages)}")
        for _p in all_pages:
            print(f"     {_p.url[:80]}")

        page = None
        # 1. Find tab already on higgsfield.ai
        for _p in all_pages:
            if "higgsfield.ai" in _p.url:
                page = _p
                print(f"   Using existing Higgsfield tab: {_p.url[:80]}")
                break
        # 2. Find any non-blank tab
        if page is None:
            for _p in all_pages:
                if _p.url not in ("about:blank", "chrome://newtab/", ""):
                    page = _p
                    print(f"   Using existing tab: {_p.url[:80]}")
                    break
        # 3. Fall back to pages[0] or new page
        if page is None:
            page = all_pages[0] if all_pages else await browser.new_page()
            print(f"   Using pages[0]: {page.url[:80]}")

        # Navigate to correct model URL
        print(f"\n🌐 Navigating to {HIGGSFIELD_URL}")
        try:
            await page.goto(HIGGSFIELD_URL, wait_until="domcontentloaded", timeout=60000)
            print(f"   ✅ Loaded. Model: {HIGGSFIELD_MODEL} | Res: {IMAGE_RESOLUTION}")
            print(f"   Current URL: {page.url[:80]}")
        except Exception as e:
            print(f"   Navigation note: {e}")
            print(f"   Current URL: {page.url[:80]}")
            print("   Chrome still open — navigate manually if needed.\n")

        await page.bring_to_front()

        await page.wait_for_timeout(2000)

        # Bring Chrome window to front via AppleScript
        import subprocess
        subprocess.run([
            "osascript", "-e",
            'tell application "Google Chrome" to activate'
        ], capture_output=True)
        # Mac notification
        subprocess.run([
            "osascript", "-e",
            'display notification "Higgsfield Chrome window is open — please log in!" with title "Higgsfield Script" sound name "Glass"'
        ], capture_output=True)

        print("\n" + "="*50)
        print("  CHROME WINDOW UGHADLA AHE!")
        print("  Dock madhe Google Chrome var click kara.")
        print("  Higgsfield madhe LOGIN kara.")
        print("  Login zala ki script auto-start hoil.")
        print("="*50 + "\n")

        # Wait for Generate button = page loaded + logged in (up to 20 min)
        print("Generate button chi wait karto (max 20 min)...")
        print("(Login karo Higgsfield madhe — script auto-detect karil)\n")
        try:
            await page.wait_for_selector("button:has-text('Generate')", timeout=1200000)
            print("✅ Generate button found — logged in!\n")
        except Exception as e:
            print(f"   Generate button not found: {e}")
            print("   Continuing anyway...")

        # ── ONE-TIME: confirm Unlimited is ON before starting loop ──────────────
        print("\n" + "="*55)
        print("  IMPORTANT: Chrome madhe Unlimited toggle ON karo!")
        print("  Generate button var 'Generate' disla pahije (no +N).")
        print("  (Login nahi zale tar login karo first)")
        print("="*55)

        # ── CAPTURE PHASE: use cache if available ─────────────────────────────
        req_cache = Path.home() / "Desktop/online-work-site/.hf_req_cache.json"
        captured_req = None

        if req_cache.exists():
            try:
                cached = _json.loads(req_cache.read_text())
                if cached.get("url") and cached.get("body"):
                    print(f"\n✅ Cached API request found: {cached['url']}")
                    ans = input("  Reuse it? (y/n, default=y): ").strip().lower()
                    if ans != "n":
                        captured_req = cached
                        print("  Using cached request.")
            except Exception as e:
                print(f"  Cache read error: {e}")

        if not captured_req:
            captured_req = await capture_generate_request(page)
            if not captured_req:
                print("\n⛔ Could not capture API request.")
                print("  Possible: Higgsfield uses WebSocket (not HTTP POST).")
                print("  Check Terminal output above for button list debug info.")
                input("Press Enter to exit...")
                await browser.close()
                return
            req_cache.write_text(_json.dumps(captured_req))
            print(f"\n✅ Request captured + saved to {req_cache.name}")

        print(f"   URL: {captured_req['url']}")
        print(f"\n🚀 Starting {len(TOPICS)} topics ({sum(len(t['posts'])+1 for t in TOPICS)} images)...\n")

        for topic in TOPICS:
            slug = topic["slug"]
            name = topic["name"]
            folder = PROJECTS_DIR / slug
            folder.mkdir(parents=True, exist_ok=True)

            print(f"\n📁 {name}")

            # 4 posts (4:5)
            for i, post_prompt in enumerate(topic["posts"], 1):
                file_key = f"{slug}_post_{i:02d}"
                if file_key in done:
                    print(f"  ⏭ post_{i:02d} skip")
                    continue

                save_path = folder / f"{name}_0{i}.png"
                success = await generate_image(page, post_prompt, "4:5", save_path, captured_req)
                if success:
                    done[file_key] = True
                    DONE_FILE.write_text(json.dumps(done))

            # 1 thumbnail (3:2)
            thumb_key = f"{slug}_thumb"
            if thumb_key not in done:
                save_path = folder / f"{name}_Thumbnail.png"
                success = await generate_image(page, topic["thumb"], "3:2", save_path, captured_req)
                if success:
                    done[thumb_key] = True
                    DONE_FILE.write_text(json.dumps(done))

        print("\n\n✅ ALL DONE!")
        await browser.close()


if __name__ == "__main__":
    import sys
    print(f"Python: {sys.version}")
    print(f"Projects dir: {PROJECTS_DIR}")
    print(f"Profile dir: {PROFILE_DIR}")
    print("Starting...\n")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        import traceback
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
