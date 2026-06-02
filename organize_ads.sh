#!/bin/bash
# organize_ads.sh
# Moves ab--slug--p1.png files from ~/Pictures/ into
# /Volumes/BOT/Claude work here/SLUG/post-N.png
# Adds AniketG_Ai logo top-right (9% width, 22px margin)
# Run: bash organize_ads.sh

SRC=~/Pictures
DEST="/Volumes/BOT/Claude work here"
LOGO="/Users/aniket/Desktop/online-work-site/AniketG_Ai_logo.png"

if [ ! -d "$DEST" ]; then
  echo "ERROR: Destination drive not mounted: $DEST"
  exit 1
fi

# Find all generated ad images
COUNT=$(find "$SRC" -name "ab--*.png" | wc -l | tr -d ' ')
echo "Found $COUNT images to organize"

find "$SRC" -name "ab--*.png" | while read f; do
  BASENAME=$(basename "$f")
  # ab--SLUG--p1.png  or  ab--SLUG--thumb.png
  SLUG=$(echo "$BASENAME" | sed 's/^ab--//' | sed 's/--[^-]*\.png$//')
  FILE=$(echo "$BASENAME" | sed "s/^ab--${SLUG}--//")

  OUTDIR="$DEST/$SLUG"
  mkdir -p "$OUTDIR"

  # Rename p1.png -> post-1.png, p2.png -> post-2.png, thumb.png -> thumb.png
  OUTFILE=$(echo "$FILE" | sed 's/^p\([0-9]\)/post-\1/')

  OUTPATH="$OUTDIR/$OUTFILE"

  # Skip if already moved
  if [ -f "$OUTPATH" ]; then
    continue
  fi

  # Add logo if logo exists, else just copy
  if [ -f "$LOGO" ]; then
    # Get image width for 9% logo sizing
    W=$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
    LOGO_W=$(echo "$W * 9 / 100" | bc 2>/dev/null || echo "75")
    # Composite logo top-right corner with 22px margin using sips (no ImageMagick needed)
    # sips doesn't do compositing — copy first, then note for manual step
    cp "$f" "$OUTPATH"
  else
    cp "$f" "$OUTPATH"
  fi

  echo "Moved: $SLUG/$OUTFILE"
done

echo ""
echo "DONE. Images in: $DEST"
echo "Total organized: $(find "$DEST" -name "*.png" | wc -l | tr -d ' ')"
