#!/usr/bin/env bash
# Scratch voiceover from the written script, so the WHOLE pipeline can run and a
# complete draft film can be watched before anyone records anything.
#
# This inverts the ordering problem: you no longer have to record to find out
# whether the edit works. You record once, against an edit you have already seen.
#
# The output is a TIMING AND REVIEW ARTEFACT, never a deliverable. It is written
# to inputs/, not public/, and build_scratch.sh stamps the draft so it cannot be
# mistaken for the real film.
set -euo pipefail
SCRIPT="${1:-script/voiceover.txt}"
OUT="${2:-inputs/vo_scratch.wav}"
VOICE="${VOICE:-Daniel}"
RATE="${RATE:-170}"   # words/min; close to a measured 130-145 delivery once pauses land
say -v "$VOICE" -r "$RATE" -o /tmp/scratch.aiff -f "$SCRIPT"
ffmpeg -v error -y -i /tmp/scratch.aiff -ar 48000 -ac 1 -c:a pcm_s16le "$OUT"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
W=$(wc -w < "$SCRIPT")
python3 - "$D" "$W" <<'PY'
import sys
d, w = float(sys.argv[1]), int(sys.argv[2])
assert d > 1.0, f"FLOOR: scratch audio is {d:.2f}s — synthesis failed"
print(f"scratch VO: {d:.2f}s, {w} words, {w/(d/60):.0f} wpm")
print("This is a SCRATCH track for timing and review. It is not the film's audio.")
PY
