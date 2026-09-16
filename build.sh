#!/usr/bin/env bash
#
# Rebuild every deliverable of this RA-L revision from source.
#
#   ./build.sh [path/to/video.mp4]
#
# Produces (all git-ignored; they are regenerated, never versioned):
#   ral_tex/root.pdf                 manuscript, changes highlighted in blue
#   ral_tex/root_clean.pdf           same manuscript without the highlighting
#   response/response.pdf            point-by-point response letter
#   ral_2nd_submit/root.pdf          copy for submission
#   ral_2nd_submit/root_clean.pdf    copy for submission
#   ral_2nd_submit/response.pdf      copy for submission
#   ral_2nd_submit/response_and_diff.pdf   response + highlighted paper (single PDF)
#   ral_2nd_submit/multimedia.zip    multimedia attachment (video + evaluation data)
#
# Requirements: pdflatex (TeX Live with IEEEtran), pdfinfo + pdfunite (poppler-utils),
# zip, and optionally python3 for the page/quality report.
#
set -euo pipefail
cd "$(dirname "$0")"

VIDEO="${1:-ral_2nd_submit/PushAround.mp4}"
LATEX=(pdflatex -interaction=nonstopmode -halt-on-error)

step() { printf '\n== %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { printf 'ERROR: %s is required but not installed.\n' "$1" >&2; exit 1; }; }

need pdflatex; need pdfinfo; need pdfunite; need zip

# ---------------------------------------------------------------- manuscript
step "1/6  manuscript with highlighted changes -> ral_tex/root.pdf"
( cd ral_tex && "${LATEX[@]}" root.tex >/dev/null && "${LATEX[@]}" root.tex >/dev/null )

step "2/6  clean manuscript -> ral_tex/root_clean.pdf"
( cd ral_tex && "${LATEX[@]}" -jobname=root_clean '\def\CLEANCOPY{}\input{root.tex}' >/dev/null \
             && "${LATEX[@]}" -jobname=root_clean '\def\CLEANCOPY{}\input{root.tex}' >/dev/null )

# -------------------------------------------------------------- response letter
step "3/6  response letter -> response/response.pdf"
( cd response && "${LATEX[@]}" response.tex >/dev/null && "${LATEX[@]}" response.tex >/dev/null )

# --------------------------------------------------------------- submission set
step "4/6  refresh ral_2nd_submit/"
mkdir -p ral_2nd_submit
cp ral_tex/root.pdf         ral_2nd_submit/root.pdf
cp ral_tex/root_clean.pdf   ral_2nd_submit/root_clean.pdf
cp response/response.pdf    ral_2nd_submit/response.pdf

step "5/6  merged response + highlighted paper -> ral_2nd_submit/response_and_diff.pdf"
pdfunite ral_2nd_submit/response.pdf ral_2nd_submit/root.pdf ral_2nd_submit/response_and_diff.pdf

# --------------------------------------------------------- multimedia attachment
step "6/6  multimedia attachment -> ral_2nd_submit/multimedia.zip"
if [ ! -f ral_2nd_submit/multimedia.zip ]; then
  printf 'WARNING: ral_2nd_submit/multimedia.zip not found - skipping the attachment.\n' >&2
else
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  unzip -q ral_2nd_submit/multimedia.zip -d "$tmp"
  if [ -f "$VIDEO" ]; then
    cp "$VIDEO" "$tmp/video.mp4"
    printf '  video: %s (%s)\n' "$VIDEO" "$(du -h "$VIDEO" | cut -f1)"
  else
    printf 'WARNING: %s not found - keeping the video already inside the archive.\n' "$VIDEO" >&2
  fi
  rm -f ral_2nd_submit/multimedia.zip
  ( cd "$tmp" && zip -qr "$OLDPWD/ral_2nd_submit/multimedia.zip" . )
  printf '  multimedia.zip: %s\n' "$(du -h ral_2nd_submit/multimedia.zip | cut -f1)"
fi

# ------------------------------------------------------------------- QA report
step "checks"
fail=0
for pdf in ral_tex/root.pdf ral_tex/root_clean.pdf response/response.pdf ral_2nd_submit/response_and_diff.pdf; do
  [ -f "$pdf" ] || { printf '  MISSING  %s\n' "$pdf"; fail=1; continue; }
  printf '  %-42s %s pages\n' "$pdf" "$(pdfinfo "$pdf" | awk '/^Pages/{print $2}')"
done
for log in ral_tex/root.log ral_tex/root_clean.log response/response.log; do
  [ -f "$log" ] || continue
  over=$(grep -c 'Overfull' "$log" || true)
  err=$(grep -c '^!' "$log" || true)
  und=$(grep -c 'undefined' "$log" || true)
  printf '  %-42s overfull=%s errors=%s undefined=%s\n' "$log" "$over" "$err" "$und"
  [ "$over" = "0" ] && [ "$err" = "0" ] && [ "$und" = "0" ] || fail=1
done

printf '\n'
if [ "$fail" = "0" ]; then
  printf 'All deliverables rebuilt and clean (0 overfull, 0 errors, 0 undefined references).\n'
else
  printf 'Rebuilt, but check the warnings above.\n' >&2
fi
