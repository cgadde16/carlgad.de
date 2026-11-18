#!/usr/bin/env bash
# Puts a CV PDF on the site: copies it to public/cv/Carl-Gadde-CV.pdf (the download) and renders each page
# to public/cv/page-N.png (the sheets on /office/cv/). Needs pdftoppm (poppler-utils).
# Usage: scripts/cv/render.sh path/to/cv.pdf
set -euo pipefail
src=${1:?usage: $0 path/to/cv.pdf}
out=$(dirname "$0")/../../public/cv
mkdir -p "$out"
rm -f "$out"/page-*.png
cp "$src" "$out/Carl-Gadde-CV.pdf"
# 1400 px wide: sharp on 2x screens at the sheet's 640 px max width; pdftoppm names them page-1.png, ...
pdftoppm -png -scale-to-x 1400 -scale-to-y -1 "$out/Carl-Gadde-CV.pdf" "$out/page"
# pdftoppm pads the number when there are 10+ pages (page-01.png); strip the zeros
for f in "$out"/page-0*.png; do [ -e "$f" ] && mv "$f" "$out/page-$(basename "$f" .png | sed 's/^page-0*//').png"; done
ls -1 "$out"
