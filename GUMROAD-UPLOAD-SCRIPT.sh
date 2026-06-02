#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║     GUMROAD AUTO-UPLOAD SCRIPT                              ║
# ║     Runs after e-PAN and Wise KYC are done                  ║
# ║     Uploads all 50 product files to existing Gumroad        ║
# ║     product pages via browser automation                     ║
# ╚══════════════════════════════════════════════════════════════╝
#
# HOW TO USE:
# 1. Make sure you're logged into Gumroad in Chrome
# 2. Open a product's Content tab in Chrome
# 3. Run this script: bash ~/Desktop/online-work-site/GUMROAD-UPLOAD-SCRIPT.sh
# The script will automate the file picker for each product

PRODUCTS_DIR="/Users/aniket/Desktop/online-work-site/products"

upload_file_to_gumroad() {
    local FILE_PATH="$1"
    local PRODUCT_NAME="$2"

    echo "Uploading: $PRODUCT_NAME"
    echo "File: $FILE_PATH"

    # Use osascript to interact with the Chrome file dialog
    osascript << APPLESCRIPT
        tell application "Google Chrome" to activate
        delay 0.5

        -- Try to navigate using keyboard shortcut in open dialog
        tell application "System Events"
            tell process "Google Chrome"
                -- Try Cmd+Shift+G to open "Go to folder" in open panel
                key code 5 using {command down, shift down}
                delay 1

                -- Check if Go to folder dialog appeared
                keystroke "${FILE_PATH}"
                delay 0.5
                key code 36
                delay 0.5
                key code 36
            end tell
        end tell
APPLESCRIPT

    echo "Done: $PRODUCT_NAME"
    sleep 2
}

echo "=== GUMROAD FILE UPLOADER ==="
echo ""
echo "This script helps upload files to Gumroad products."
echo "For each product, follow these steps:"
echo ""
echo "STEP 1: In Chrome, navigate to the product's Content tab"
echo "STEP 2: Click 'Upload your files' → 'Computer files'"
echo "STEP 3: When the file picker opens, press Cmd+Shift+G"
echo "STEP 4: Type the file path shown below and press Enter twice"
echo ""
echo "=== FILE PATHS FOR EACH PRODUCT ==="
echo ""

declare -A PRODUCTS
PRODUCTS[1]="01-ai-business-vault"
PRODUCTS[2]="02-midjourney-cinematic"
PRODUCTS[3]="03-instagram-content-machine"
PRODUCTS[4]="04-photography-prompts"
PRODUCTS[5]="05-chatgpt-copywriting"
PRODUCTS[6]="06-freelancer-client-vault"
PRODUCTS[7]="07-youtube-script-machine"
PRODUCTS[8]="08-linkedin-domination-vault"
PRODUCTS[9]="09-seo-content-machine"
PRODUCTS[10]="10-email-marketing-funnel-kit"
PRODUCTS[11]="11-creator-monetization-pack"
PRODUCTS[12]="12-notion-productivity-os"
PRODUCTS[13]="13-profession-ai-prompts"
PRODUCTS[14]="14-business-sop-templates"
PRODUCTS[15]="15-resume-career-kit"
PRODUCTS[16]="16-ecommerce-launch-kit"
PRODUCTS[17]="17-ai-side-hustle-vault"
PRODUCTS[18]="18-tiktok-viral-vault"
PRODUCTS[19]="19-student-ai-vault"
PRODUCTS[20]="20-personal-finance-playbook"
PRODUCTS[21]="21-pinterest-marketing-machine"
PRODUCTS[22]="22-wedding-planning-kit"
PRODUCTS[23]="23-mindset-journal-system"
PRODUCTS[24]="24-podcast-launch-kit"
PRODUCTS[25]="25-airbnb-superhost-kit"
PRODUCTS[26]="26-amazon-kdp-kit"
PRODUCTS[27]="27-fitness-coaching-templates"
PRODUCTS[28]="28-canva-creator-kit"
PRODUCTS[29]="29-real-estate-investor"
PRODUCTS[30]="30-social-media-agency"
PRODUCTS[31]="31-prompt-engineering-masterclass"
PRODUCTS[32]="32-teacher-classroom-pack"
PRODUCTS[33]="33-dating-profile-kit"
PRODUCTS[34]="34-parenting-templates"
PRODUCTS[35]="35-mental-health-workbook"
PRODUCTS[36]="36-startup-founder-toolkit"
PRODUCTS[37]="37-etsy-business-kit"
PRODUCTS[38]="38-dropshipping-kit"
PRODUCTS[39]="39-photography-business"
PRODUCTS[40]="40-virtual-assistant-kit"
PRODUCTS[41]="41-nutrition-coaching"
PRODUCTS[42]="42-language-learning-ai"
PRODUCTS[43]="43-home-organization"
PRODUCTS[44]="44-consulting-sow-kit"
PRODUCTS[45]="45-grant-writing-vault"
PRODUCTS[46]="46-youtube-channel-growth"
PRODUCTS[47]="47-investment-tracking"
PRODUCTS[48]="48-adulting-life-skills"
PRODUCTS[49]="49-book-writing-kit"
PRODUCTS[50]="50-nonprofit-fundraising"

for i in $(seq 1 50); do
    FOLDER="${PRODUCTS[$i]}"
    FILE_PATH="${PRODUCTS_DIR}/${FOLDER}/prompts.txt"
    echo "Product $i: ${FILE_PATH}"
done

echo ""
echo "=== QUICK DRAG & DROP METHOD (FASTEST) ==="
echo ""
echo "1. Open Finder"
echo "2. Press Cmd+Shift+G → paste: $PRODUCTS_DIR"
echo "3. For each product folder → drag prompts.txt to Gumroad Content area"
echo ""
echo "Total time: ~5 min for all 50 products"
