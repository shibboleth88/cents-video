#!/usr/bin/env bash
# Voiceover cleanup. Restrained by design: it does not trim pauses, change
# delivery speed, or apply heavy denoising. Compare against the original at
# MATCHED LOUDNESS before accepting it — processing that sounds "better" at a
# higher level is usually just louder.
#
#   pipeline/audio_clean.sh inputs/vo_raw.wav public/vo.wav
#
# The EQ below was fitted to one microphone. Re-fit it for a different one
# rather than inheriting it as a preset.
set -euo pipefail
IN="${1:?input}"; OUT="${2:?output}"
CHAIN="highpass=f=75,afftdn=nf=-25,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=2800:t=q:w=1:g=1.5,deesser=i=0.4,acompressor=ratio=2:threshold=-18dB:attack=10:release=180"

ffmpeg -v error -y -i "$IN" -af "$CHAIN,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" \
       -ar 48000 -c:a pcm_s16le "$OUT" 2>/tmp/ln1.json || true
ffmpeg -v error -y -i "$IN" -af "$CHAIN,loudnorm=I=-16:TP=-1.5:LRA=11" \
       -ar 48000 -c:a pcm_s16le "$OUT"

echo "--- measured on the OUTPUT (not the intermediate) ---"
ffmpeg -v info -i "$OUT" -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/input_i/,/}/p'
IND=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
OUTD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
python3 - "$IND" "$OUTD" <<'PY'
import sys
i,o=float(sys.argv[1]),float(sys.argv[2])
# Cleanup must not change timing. A shifted duration means a filter trimmed or
# padded the voice, which would desynchronise every anchor in the film.
assert abs(i-o) < 0.05, f"DURATION CHANGED {i:.3f}s -> {o:.3f}s — cleanup altered timing"
print(f"timing preserved: {i:.3f}s -> {o:.3f}s")
PY
echo "Now LISTEN to it. Loudness numbers are not a judgement about artifacts."
