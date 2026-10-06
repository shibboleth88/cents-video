#!/usr/bin/env python3
"""Reconcile a transcript against the written script.

Free transcription is non-deterministic: two runs over the SAME audio produced
".opherRutherford" and then "Rhodeford" for the same word. Anything keyed to
exact recognised tokens — a correction list, an anchor, a caption — is therefore
built on sand.

But the script is known. So:
  * where transcript and script agree          -> keep (timings from the audio)
  * where they differ word-for-word            -> take the SCRIPT's spelling,
                                                  keep the AUDIO's timing
                                                  (a recognition error)
  * where they differ structurally             -> keep what was SPOKEN and flag
                                                  it (an adlib or a revision)

That last rule is the important one. The written script is a spelling reference,
not a substitute for the recording, and an adlib must survive into the captions.

  python3 pipeline/reconcile.py --self-test
"""
from __future__ import annotations
import difflib, re, sys

def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("’", "'"))

def heal_split_tokens(words: list[dict]) -> list[dict]:
    """Join a token that is only a hyphen plus letters onto the one before it.

    Whisper emits a hyphenated word as two tokens with the hyphen leading the
    second: "ready" + "-made". That is one word with a tokenisation seam, not
    two words. Left split, it reaches the comparison below as a 2-against-1
    opcode, which is the shape of a STRUCTURAL difference - so a spelling
    artefact gets preserved as though the speaker had departed from the script,
    and "The ready -made he chose" goes on screen.
    """
    out: list[dict] = []
    for w in words:
        if out and re.fullmatch(r"-\w[\w'\u2019-]*", w["word"]):
            out[-1] = {**out[-1], "word": out[-1]["word"] + w["word"], "end": w["end"]}
        else:
            out.append(dict(w))
    return out


def reconcile(words: list[dict], script: str) -> tuple[list[dict], list[dict]]:
    """Returns (corrected_words, divergences)."""
    words = heal_split_tokens(words)
    sw = [t for t in re.findall(r"\S+", script) if norm(t)]
    a = [norm(w["word"]) for w in words]
    b = [norm(t) for t in sw]
    if not a: raise ValueError("transcript is empty")
    if not b: raise ValueError("script is empty")

    out, diverge = [], []
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                heard, meant = words[i1 + k]["word"], sw[j1 + k]
                out.append({**words[i1 + k], "word": meant})
                # Normalisation hides case and punctuation, and those carry
                # meaning here: Cents and CENTS normalise equal but denote
                # different things. Record the raw difference so it is visible.
                if heard != meant:
                    diverge.append({"kind": "recognition", "heard": heard, "used": meant,
                                    "at": words[i1 + k]["start"]})
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            # Same number of words: a recognition error. Script spelling wins,
            # audio timing is kept.
            for k in range(i2 - i1):
                heard, meant = words[i1 + k]["word"], sw[j1 + k]
                out.append({**words[i1 + k], "word": meant})
                diverge.append({"kind": "recognition", "heard": heard, "used": meant,
                                "at": words[i1 + k]["start"]})
        else:
            # Structural difference: the speaker departed from the script. Keep
            # what was actually said; flag it so a human decides.
            for k in range(i1, i2):
                out.append(words[k])
            diverge.append({"kind": "spoken_differs",
                            "heard": " ".join(words[k]["word"] for k in range(i1, i2)) or "(nothing)",
                            "script": " ".join(sw[j] for j in range(j1, j2)) or "(nothing)",
                            "at": words[i1]["start"] if i1 < len(words) else None})
    # FLOOR: reconciliation must not lose or invent words relative to the audio.
    if len(out) != len(words):
        raise ValueError(f"reconciliation changed word count {len(words)} -> {len(out)}")
    return out, diverge

def self_test() -> int:
    script = "What happens when a systems artwork produces something the system itself cannot witness."
    base = script.split()
    def mk(ws): return [{"word": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate(ws)]

    cases = [
        ("recognition error is corrected",
         mk(["What","happens","when","a","system's","artwork","produces","something","the",
             "system","itself","cannot","witness."]),
         lambda o, d: o[4]["word"] == "systems" and any(x["kind"] == "recognition" for x in d)),
        ("merge artefact is corrected",
         mk(["What","happens","when","a",".opherSystems","artwork","produces","something","the",
             "system","itself","cannot","witness."]),
         lambda o, d: o[4]["word"] == "systems"),
        ("ADLIB SURVIVES, is not overwritten",
         mk(["What","happens","when","a","systems","artwork","actually","produces","something",
             "the","system","itself","cannot","witness."]),
         lambda o, d: any(w["word"] == "actually" for w in o)
                      and any(x["kind"] == "spoken_differs" for x in d)),
        ("hyphen-split token is healed, not treated as a departure",
         mk(["What","happens","when","a","systems","artwork","produces","something","the",
             "system","itself","cannot","witness."])[:4] +
         [{"word":"sys","start":1.6,"end":1.8},{"word":"-tems","start":1.8,"end":2.0}] +
         mk(["artwork","produces","something","the","system","itself","cannot","witness."])[0:8],
         lambda o, d: any(w["word"] == "systems" for w in o)
                      and not any(x["kind"] == "spoken_differs" for x in d)),
        ("timings come from the audio, never the script",
         mk(["What","happens","when","a","system's","artwork","produces","something","the",
             "system","itself","cannot","witness."]),
         lambda o, d: abs(o[4]["start"] - 1.6) < 1e-9),
    ]
    bad = 0
    for name, words, check in cases:
        out, div = reconcile(words, script)
        ok = check(out, div)
        print(f"  {'\033[32mPASS\033[0m' if ok else '\033[31mFAIL\033[0m'} {name}")
        if not ok:
            bad += 1
            print(f"       got: {' '.join(w['word'] for w in out)}")
            print(f"       div: {div}")

    # CONTROL: if reconciliation silently took the script wholesale, the adlib
    # case above would pass vacuously. Prove the script does NOT overwrite speech.
    out, _ = reconcile(mk(base[:6] + ["completely","different","words","here"]), script)
    spoken_kept = any(w["word"] == "completely" for w in out)
    print(f"  {'\033[32mPASS\033[0m' if spoken_kept else '\033[31mVACUOUS\033[0m'} control: a large divergence keeps the SPOKEN words")
    if not spoken_kept: bad += 1
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else 0)
