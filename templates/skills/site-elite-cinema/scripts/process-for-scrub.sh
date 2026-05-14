#!/bin/bash
# process-for-scrub.sh
# Re-encode an MP4 with scrub-optimal flags (GOP=1, baseline, faststart).
# Generates desktop + mobile variants and a poster JPG.
# Usage: process-for-scrub.sh <input.mp4> [output_basename] [desktop_width]

set -euo pipefail

INPUT="${1:-}"
TS="$(date +%s)"
OUT_BASE="${2:-./scrub-${TS}}"
DESKTOP_W="${3:-1280}"

if [ -z "$INPUT" ]; then
  echo "Usage: $0 <input.mp4> [output_basename] [desktop_width]" >&2
  exit 64
fi
if [ ! -f "$INPUT" ]; then
  echo "ERROR: input not found at $INPUT" >&2
  exit 66
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not installed" >&2
  exit 127
fi

DESKTOP_OUT="${OUT_BASE}-desktop.mp4"
MOBILE_OUT="${OUT_BASE}-mobile.mp4"
POSTER_OUT="${OUT_BASE}-poster.jpg"

COMMON_FLAGS=(-movflags +faststart -vcodec libx264 -profile:v baseline -level 3 -pix_fmt yuv420p -crf 23 -g 1 -an -y)

echo "[scrub] encoding desktop (${DESKTOP_W}px wide) ..."
ffmpeg -hide_banner -loglevel error -i "$INPUT" -vf "scale=${DESKTOP_W}:-2" "${COMMON_FLAGS[@]}" "$DESKTOP_OUT"

echo "[scrub] encoding mobile (720x405) ..."
ffmpeg -hide_banner -loglevel error -i "$INPUT" -vf "scale=720:-2" "${COMMON_FLAGS[@]}" "$MOBILE_OUT"

echo "[scrub] extracting poster frame ..."
ffmpeg -hide_banner -loglevel error -i "$INPUT" -vframes 1 -q:v 2 -y "$POSTER_OUT"

DESKTOP_KB="$(du -k "$DESKTOP_OUT" | cut -f1)"
MOBILE_KB="$(du -k "$MOBILE_OUT" | cut -f1)"
POSTER_KB="$(du -k "$POSTER_OUT" | cut -f1)"

echo "---"
echo "DESKTOP:  $DESKTOP_OUT  (${DESKTOP_KB} KB)"
echo "MOBILE:   $MOBILE_OUT   (${MOBILE_KB} KB)"
echo "POSTER:   $POSTER_OUT   (${POSTER_KB} KB)"
echo "---"
