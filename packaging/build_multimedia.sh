#!/usr/bin/env bash
# Rebuild the RA-L multimedia attachment (ral_2nd_submit/multimedia.zip) from
# the evaluation data and the response plotting script.
#
#   bash packaging/build_multimedia.sh
#
# The archive contains, as required by the RA-L multimedia guidelines:
#   * exactly one video,
#   * ReadMe.txt  (minimum software requirements and contact information),
#   * Summary.txt (contents, usage and value),
#   * datasets and source code only (no supplemental text or figures).
# It is kept well below the 50 MB archive limit.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/packaging/multimedia"
OUT="$REPO/ral_2nd_submit/multimedia.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/evaluation_data"

# --- per-trial records, aggregates and resolved configurations -----------------
# CSV/JSON for the numbers; Markdown only for the readme digests.  Formatted
# table renderings (paper_table_*.md/.tex/.txt) and the large rollout logs
# (console.log, trial_logs/) as well as Windows "Zone.Identifier" sidecars are
# deliberately excluded.
find "$REPO/data" -type f \( -name '*.csv' -o -name '*.json' -o -name '*.md' \) \
     ! -name '*Zone.Identifier' ! -name 'paper_table_*.md' ! -name 'backend_comparison*' \
     | sort | while read -r f; do
  rel="${f#"$REPO"/data/}"
  mkdir -p "$STAGE/evaluation_data/$(dirname "$rel")"
  cp "$f" "$STAGE/evaluation_data/$rel"
done

# drop empty or placeholder files (0-byte, or 1-byte CSVs standing for an empty table)
find "$STAGE/evaluation_data" -type f -size 0 -delete
find "$STAGE/evaluation_data" -type f -name '*.csv' -size -2c -delete

# --- figure-regeneration script and mapping -----------------------------------
cp "$REPO/response/make_figures.py" "$STAGE/evaluation_data/make_figures.py"
cp "$REPO/ral_tex/scripts/plot_density_scaling_paper.py" \
   "$STAGE/evaluation_data/plot_density_scaling_paper.py"
cp "$SRC/evaluation_data/README.md" "$STAGE/evaluation_data/README.md"

# --- required text files and the single video ---------------------------------
cp "$SRC/ReadMe.txt" "$SRC/Summary.txt" "$STAGE/"
cp "$REPO/ral_1st_submit/video.mp4" "$STAGE/video.mp4"

# --- build the archive from scratch -------------------------------------------
rm -f "$OUT"
( cd "$STAGE" && zip -X -q -r "$OUT" video.mp4 ReadMe.txt Summary.txt evaluation_data )

echo "wrote $OUT  ($(du -h "$OUT" | cut -f1), $(unzip -Z1 "$OUT" | wc -l) entries)"
