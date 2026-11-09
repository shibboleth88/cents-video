"""Spoken text for the TTS from script/voiceover.txt and script/spoken.json, the
same table captions/build_cues.py uses to map the voice back to the script, so
the two cannot drift. Writes audio/tts_text.txt and audio/tts_prompt.txt (the
user's calm direction, [thoughtfully] [calm], on every line, per the brief §5).

    python3 -I films/wall-dopemind-next/audio/make_tts.py   (from the repo root)
"""
import json, pathlib, re, sys
F = pathlib.Path(__file__).resolve().parents[1]
S = json.load(open(F / "script/spoken.json"))
out = []
for line in open(F / "script/voiceover.txt").read().splitlines():
    toks = []
    for tok in line.split():
        m = re.match(r'^(["“]?)(.*?)([.,:;?!"”]*)$', tok)
        lead, key, p = m.groups()
        toks.append(lead + S.get(key, key) + p)
    s = " ".join(toks)
    if re.search(r"\d", s): sys.exit(f"REFUSING: a digit would reach the voice: {s!r}")
    out.append(s)
unused = [k for k in S if not any(re.search(rf'(^|[\s"]){re.escape(k)}([\s.,:;?!"]|$)', l) for l in open(F / "script/voiceover.txt").read().splitlines())]
if unused: sys.exit(f"REFUSING: spoken.json keys never used in the script: {unused}")
(F / "audio/tts_text.txt").write_text("\n".join(out) + "\n")
(F / "audio/tts_prompt.txt").write_text("\n".join("[thoughtfully] [calm] " + s for s in out) + "\n")
print(f"{len(out)} lines, {sum(len(s.split()) for s in out)} spoken words")
