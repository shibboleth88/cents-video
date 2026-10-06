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
#
# loudnorm runs in TWO passes. In one pass it works in dynamic mode and only
# approaches the target: on this production it landed at -17.2 LUFS against a
# -16.0 target, which the release gate reads as a failure at ±1.0. Measuring
# first and feeding the measurements back lets it apply a linear gain, which
# hits the target and leaves the dynamics alone.
set -euo pipefail
IN="${1:?input}"; OUT="${2:?output}"
CHAIN="highpass=f=75,afftdn=nf=-25,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=2800:t=q:w=1:g=1.5,deesser=i=0.4,acompressor=ratio=2:threshold=-18dB:attack=10:release=180"
I=-16.0; TP=-1.5; LRA=11

# -v info, not -v error: loudnorm prints its measurement JSON at info level,
# so measuring under -v error silently yields nothing.
MEAS=$(ffmpeg -v info -i "$IN" -af "$CHAIN,loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" \
       -f null - 2>&1 | sed -n '/^{/,/^}/p')
[ -n "$MEAS" ] || { echo "loudnorm measurement pass produced nothing" >&2; exit 1; }
eval "$(python3 - "$MEAS" <<'PY2'
import json, sys
m = json.loads(sys.argv[1])
for k in ("input_i","input_tp","input_lra","input_thresh","target_offset"):
    if k not in m: sys.exit(f"measurement is missing {k}")
print(f"MI={m['input_i']}; MTP={m['input_tp']}; MLRA={m['input_lra']}; MTH={m['input_thresh']}; OFF={m['target_offset']}")
PY2
)"
echo "measured: I=$MI TP=$MTP LRA=$MLRA thresh=$MTH offset=$OFF"

ffmpeg -v error -y -i "$IN" \
  -af "$CHAIN,loudnorm=I=$I:TP=$TP:LRA=$LRA:measured_I=$MI:measured_TP=$MTP:measured_LRA=$MLRA:measured_thresh=$MTH:offset=$OFF:linear=true" \
  -ar 48000 -c:a pcm_s16le "$OUT"

echo "--- measured on the OUTPUT (not the intermediate) ---"
ffmpeg -v info -i "$OUT" -af loudnorm=print_format=json -f null - 2>&1 | sed -n '/input_i/,/}/p'
IND=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
OUTD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
python3 - "$IND" "$OUTD" <<'PY3'
import sys
i,o=float(sys.argv[1]),float(sys.argv[2])
# Cleanup must not change timing. A shifted duration means a filter trimmed or
# padded the voice, which would desynchronise every anchor in the film.
assert abs(i-o) < 0.05, f"DURATION CHANGED {i:.3f}s -> {o:.3f}s — cleanup altered timing"
print(f"timing preserved: {i:.3f}s -> {o:.3f}s")
PY3
echo "Now LISTEN to it. Loudness numbers are not a judgement about artifacts."
