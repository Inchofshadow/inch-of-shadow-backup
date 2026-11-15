#!/bin/sh
# Builds a PDF from an HTML file in this folder with headless Chrome (own temp profile,
# never touches his named Chrome profiles). Usage: sh build_pdf.sh rate-card
set -e
cd "$(dirname "$0")"
NAME="${1:-rate-card}"
PROFILE="$(mktemp -d)"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-first-run --user-data-dir="$PROFILE" \
  --no-pdf-header-footer --allow-file-access-from-files \
  --print-to-pdf="$PWD/$NAME.pdf" "file://$PWD/$NAME.html"
rm -rf "$PROFILE"
echo "built $PWD/$NAME.pdf"
