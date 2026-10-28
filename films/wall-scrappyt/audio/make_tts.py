"""Spoken text for the TTS from script/voiceover.txt and script/spoken.json, the
same table captions/build_cues.py uses to map the voice back to the script, so
the two can't drift. Writes audio/tts_text.txt and the prompt with the user's
calm direction tags ([thoughtfully] [calm], chosen 2026-10-27) on every line.

    python3 -I films/wall-scrappyt/audio/make_tts.py   (from the repo root)
"""
import json, pathlib, re, sys
F = pathlib.Path(__file__).resolve().parents[1]
S = json.load(open(F / "script/spoken.json"))
out = []
for line in open(F / "script/voiceover.txt").read().splitlines():
    toks = []
    for tok in line.split():
        m = re.match(r"^(.*?)([.,:;]*)$", tok)
        key, p = m.group(1), m.group(2)
        toks.append(S.get(key, key) + p)
    s = " ".join(toks)
    if re.search(r"\d", s): sys.exit(f"REFUSING: a digit would reach the voice: {s!r}")
    out.append(s)
(F / "audio/tts_text.txt").write_text("\n".join(out) + "\n")
(F / "audio/tts_prompt_v3.txt").write_text("\n".join("[thoughtfully] [calm] " + s for s in out) + "\n")
print(f"{len(out)} lines, {sum(len(s.split()) for s in out)} spoken words")
