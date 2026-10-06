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
# RE-FITTED 2026-10-06 for the delivered recording (48kHz mono AAC ~68kbps,
# phone-held, strong proximity effect). The previous chain was fitted to a
# different microphone and, measured on THIS source against its own 630-1000Hz
# band, it ADDED +4.6dB below 100Hz and CUT -4.3dB at 6-10kHz - it was making
# the voice boomier and duller, which is the failure the comment above warns
# about and which nobody had measured.
#
# Measured on the raw edit, relative to 630-1000Hz: +19dB at 100-160Hz where a
# speech LTAS predicts about +15, and -9.8dB at 2.5-4kHz. So: take out the
# proximity boom, leave the fundamentals, put back the presence that the
# denoiser and de-esser remove. Nothing is boosted above 12kHz because the
# 68kbps encode has nothing there (16-20kHz measures -69dB).
# Second fit. The first overshot: it moved the low end -10.8dB and the presence
# +7.6dB where 5-6 and 3 were intended, and raised quiet-frame noise 2.7dB. The
# bands compound, so each move is roughly halved here. Measured, not guessed.
CHAIN="highpass=f=80:poles=1,equalizer=f=120:t=q:w=0.9:g=-2.5,equalizer=f=300:t=q:w=1.0:g=-1,afftdn=nf=-22:tn=1,equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=6000:t=q:w=1.5:g=1,deesser=i=0.35,acompressor=ratio=2:threshold=-19dB:attack=12:release=200"
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
