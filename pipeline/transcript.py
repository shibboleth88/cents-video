#!/usr/bin/env python3
"""Produce the recording script — the pipeline's FIRST deliverable.

The transcript comes before the video. It is what the user reads aloud, so it is
laid out for reading, not for editing: one sentence per line, numbered, with the
places that trip a reader marked. Everything downstream is built from the
recording of this, so it is the one artefact that has to be right first.

  python3 pipeline/transcript.py          # write exports/recording_script.txt
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Words a reader stumbles on, or that must be said a particular way. Taken from
# the production notes' terminology section plus anything the essay introduces.
NOTES = {
    "CENTS": "say 'cents' — the PROJECT (capitals are for the reader, not the voice)",
    "Cents": "the collection pieces, said the same as 'cents'",
    "sat": "rhymes with 'cat'; a satoshi",
    "839969": "read as 'eight three nine, nine six nine'",
    "1982": "'nineteen eighty-two'",
    "pre-1982": "'pre nineteen eighty-two'",
    "Rutherford": "RUTH-er-ford",
    "shibboleth": "SHIB-o-leth",
    "satoshi": "sa-TOH-shee",
    "objecthood": "OB-ject-hood",
    "decentralized": "four syllables, do not rush",
    "intersubjective": "in-ter-sub-JEC-tive",
}

def main() -> int:
    vo = (ROOT/"script"/"voiceover.txt").read_text()
    body = "\n".join(l for l in vo.splitlines() if l.strip())
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", body) if s.strip()]
    words = len(body.split())

    out = ["CENTS & digital objecthood — RECORDING SCRIPT",
           "=" * 52, "",
           f"{len(sents)} sentences, {words} words.",
           f"At 130-145 words a minute that is about {words/145*60:.0f}-{words/130*60:.0f} seconds "
           f"of speech, before pauses.", "",
           "HOW TO RECORD",
           "  One take, straight through. Do not stop to fix a stumble — say the line",
           "  again and carry on; the alignment keeps whatever you actually said, and",
           "  a second attempt inside one take is easier to cut than a second take.",
           "  Leave a breath between sentences. Leave four seconds of silence at the",
           "  end: the credits live there.",
           "  Changing a line as you read is fine. The transcript follows your voice,",
           "  not the page, and anything you add is flagged for review rather than",
           "  overwritten.", "",
           "  Save as: inputs/vo_raw.wav", "",
           "-" * 52, ""]

    seen = set()
    for i, s in enumerate(sents, 1):
        out.append(f"{i:2}.  {s}")
        hits = [(w, n) for w, n in NOTES.items()
                if re.search(rf"\b{re.escape(w)}\b", s) and w not in seen]
        for w, n in hits:
            seen.add(w)
            out.append(f"      [{w}: {n}]")
        out.append("")

    out += ["-" * 52, "",
            "AFTER RECORDING", "",
            "  pipeline/audio_clean.sh inputs/vo_raw.wav public/vo.wav",
            "  python3 pipeline/align.py public/vo.wav --script script/voiceover.txt",
            "  npm run render && npm run render:captioned && npm run render:essential",
            "  python3 pipeline/verify.py", "",
            "  The edit re-cuts itself around your timing. Nothing needs re-timing by hand.",
            ""]
    dst = ROOT/"exports"/"recording_script.txt"
    dst.write_text("\n".join(out))
    # FLOOR: a script with no sentences is not a short script, it is a failure.
    if len(sents) < 5: sys.exit(f"only {len(sents)} sentences — voiceover.txt looks empty")
    print(f"{len(sents)} sentences, {words} words -> {dst.relative_to(ROOT)}")
    print(f"estimated {words/145*60:.0f}-{words/130*60:.0f}s of speech")
    return 0

if __name__ == "__main__":
    sys.exit(main())
