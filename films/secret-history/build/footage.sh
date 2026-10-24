#!/usr/bin/env bash
# Rebuild public/secret-history/ftg/ (gitignored) from the user's "cents shortlist".
# Usage: bash films/secret-history/build/footage.sh "<path to cents shortlist>"
set -euo pipefail
SRC="${1:?path to the cents shortlist folder}"; V="$SRC/for videos"
cd "$(dirname "$0")/../../.."
OUT=public/secret-history/ftg; mkdir -p "$OUT"
# Nixon address: only the clean head of the user's edit (0-3.95 s); the rest is composited.
ffmpeg -v error -y -i "$V/nixon 1971 bretton video to post.MP4" -t 3.95 -an \
  -vf "crop=960:720:160:0,scale=732:-2" -c:v libx264 -crf 18 -pix_fmt yuv420p "$OUT/nixon_hd.mp4"
# NYT 16 Aug 1971 front page: crop away the browser controls in the screenshot.
ffmpeg -v error -y -i "$V/nixon gold standard.JPG" -vf "crop=705:381:8:95" -q:v 2 "$OUT/nyt1971.jpg"
# Block model loop: white ground keyed to the film's bg (#0b0a0a).
ffmpeg -v error -y -i "$V/BLOCK loop.mp4" -f lavfi -i "color=c=0x0b0a0a:s=1080x1080:r=30" \
  -filter_complex "[0:v]crop=1080:1080:420:0,colorkey=0xFFFFFF:0.18:0.12[k];[1:v][k]overlay=shortest=1,format=yuv420p" \
  -an -c:v libx264 -crf 18 "$OUT/block_dark.mp4"
ffmpeg -v error -y -i "$V/copper pour clip.mov" -an -c:v libx264 -crf 18 -pix_fmt yuv420p "$OUT/pour.mp4"
ffmpeg -v error -y -i "$V/1971 face covered with block copy.mp4" -an -c:v libx264 -crf 18 -pix_fmt yuv420p "$OUT/face1971.mp4"
echo "footage rebuilt in $OUT"
