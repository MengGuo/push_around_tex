#!/usr/bin/env bash
# Build the RA-L camera-ready manuscript, response, and selected blue-marked copy
# without changing the frozen v2 package. The publication PDF is the clean copy.
set -euo pipefail
cd "$(dirname "$0")"

for program in pdflatex bibtex gs pdfinfo rg python3; do
  command -v "$program" >/dev/null || {
    printf 'Required program missing: %s\n' "$program" >&2
    exit 1
  }
done

mkdir -p ral_final_submit
(
  cd ral_tex
  for job in root root_clean; do
    entry='root.tex'
    if [ "$job" = root_clean ]; then
      entry='\def\CLEANCOPY{}\input{root.tex}'
    fi
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$entry" >/dev/null
    bibtex "$job" >/dev/null
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$entry" >/dev/null
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$entry" >/dev/null
    if rg -n '^!|Overfull|undefined' "$job.log"; then
      printf 'Resolve the manuscript issues above before final submission.\n' >&2
      exit 1
    fi
  done
)

pages=$(pdfinfo ral_tex/root_clean.pdf | awk '/^Pages:/{print $2}')
if [ "$pages" -gt 8 ]; then
  printf 'Camera-ready manuscript exceeds eight pages: %s\n' "$pages" >&2
  exit 1
fi

# Preserve page geometry and image pixel dimensions. Optimize color-image
# encoding at JPEG quality 95; keep grayscale data and alpha masks lossless.
gs -q -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dNOPAUSE -dBATCH -dSAFER \
  -dEmbedAllFonts=true -dSubsetFonts=true -dCompressFonts=true \
  -dDetectDuplicateImages=true -dPassThroughJPEGImages=true \
  -dDownsampleColorImages=false -dDownsampleGrayImages=false \
  -dDownsampleMonoImages=false -dAutoFilterColorImages=false \
  -dColorImageFilter=/DCTEncode -dAutoFilterGrayImages=false \
  -dGrayImageFilter=/FlateEncode -dJPEGQ=95 \
  -sOutputFile=ral_final_submit/root.pdf ral_tex/root_clean.pdf

final_bytes=$(wc -c < ral_final_submit/root.pdf)
if [ "$final_bytes" -gt 5000000 ]; then
  printf 'Publication PDF exceeds the 5 MB upload limit: %s bytes\n' "$final_bytes" >&2
  exit 1
fi
printf 'Camera-ready PDF: ral_final_submit/root.pdf (%s pages, %s bytes)\n' "$pages" "$final_bytes"

python3 packaging/build_final_review.py --manuscript-built
python3 packaging/package_final.py
