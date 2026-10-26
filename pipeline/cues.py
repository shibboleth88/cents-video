#!/usr/bin/env python3
"""Caption chunking, shared by align.py and make_fixture.py.

Replaces a greedy word-cap chunker that reliably produced single-word cues
("witness.", "inscribed.") held for 0.4s — forbidden by the production notes,
and invisible to every numeric gate because the FILE was perfectly well formed.

Algorithm: split on sentence boundaries, then split long sentences into BALANCED
chunks (never a long chunk plus a stub), preferring punctuation breaks, then
merge anything still too short into a neighbour.

  python3 pipeline/cues.py --self-test
"""
from __future__ import annotations
import math, sys

MAX_CHARS = 52      # ~2 lines in the caption region at 48px
MIN_WORDS = 2
MIN_DUR = 0.70
BREAK_AFTER = (",", ";", ":", "—", "-")
# A line that ends on one of these strands its phrase across two cues
# ("That year copper went to the / war"). Never break after them.
WEAK = {"a", "an", "the", "to", "of", "in", "into", "on", "at", "by", "for", "from", "with",
        "and", "or", "but", "as", "is", "be", "can", "its", "their", "his", "her", "when", "that",
        "what", "which", "who"}

Word = dict  # {"word": str, "start": float, "end": float}

def _text(ws: list[Word]) -> str:
    return " ".join(w["word"] for w in ws)

def _sentences(words: list[Word]) -> list[list[Word]]:
    out, buf = [], []
    for w in words:
        buf.append(w)
        if w["word"].endswith((".", "?", "!", "…")):
            out.append(buf); buf = []
    if buf: out.append(buf)
    return out

def _split_balanced(ws: list[Word]) -> list[list[Word]]:
    """Split one sentence into near-equal chunks under MAX_CHARS. Equal sizing is
    the point: a greedy fill leaves the remainder as a stub, which is the orphan."""
    n = len(_text(ws))
    if n <= MAX_CHARS or len(ws) <= MIN_WORDS: return [ws]
    k = math.ceil(n / MAX_CHARS)
    target = n / k
    chunks, cur, used = [], [], 0
    for i, w in enumerate(ws):
        cur.append(w)
        remaining_words = len(ws) - i - 1
        remaining_chunks = k - len(chunks) - 1
        cur_len = len(_text(cur))
        # Close the chunk at the target, or earlier on punctuation, but never so
        # early that a later chunk would be left with fewer than MIN_WORDS.
        weak = w["word"].lower().strip("\"'") in WEAK or w.get("nobreak", False)
        at_target = cur_len >= target * 0.82 and not weak
        on_punct = w["word"].endswith(BREAK_AFTER) and cur_len >= target * 0.55
        enough_left = remaining_words >= remaining_chunks * MIN_WORDS
        if remaining_chunks > 0 and (at_target or on_punct) and enough_left and len(cur) >= MIN_WORDS:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return [c for c in chunks if c]

def _seg(w: Word, boundaries: list[float]) -> int:
    """Which picture segment a word is spoken in: the number of cuts at or before it."""
    return sum(1 for b in boundaries if w["start"] >= b - 1e-6)

def _merge_short(cues: list[list[Word]], boundaries: list[float] = ()) -> list[list[Word]]:
    """Fold any cue that is too short, or too brief to read, into the neighbour
    it fits best with. Runs to a fixed point.

    Never across a picture cut. A one-word year sentence ("1979.") was folded
    into the PREVIOUS sentence because that neighbour was shorter, so the year
    was read out under the previous year's picture. Same-segment neighbours
    only; an orphan with none stays, and audit() reports it."""
    boundaries = list(boundaries)
    changed = True
    while changed and len(cues) > 1:
        changed = False
        for i, c in enumerate(cues):
            dur = c[-1]["end"] - c[0]["start"]
            if len(c) >= MIN_WORDS and dur >= MIN_DUR: continue
            seg = _seg(c[0], boundaries)
            prev = cues[i-1] if i > 0 and _seg(cues[i-1][-1], boundaries) == seg else None
            nxt = cues[i+1] if i < len(cues)-1 and _seg(cues[i+1][0], boundaries) == seg else None
            cand = []
            if prev is not None: cand.append((len(_text(prev)), i-1, "prev"))
            if nxt is not None: cand.append((len(_text(nxt)), i+1, "next"))
            if not cand: continue
            # Merge into the shorter neighbour, but never into one that would
            # then be over-long: a fix for an orphan must not create a wall.
            cand.sort()
            # `c` is the cue being folded away; the comprehension variable must
            # not shadow it. It did, so `_text` was handed a (len, index, side)
            # tuple and raised, and the filter was never measuring what it says:
            # neighbour length + THIS cue's length against the limit.
            cur_len = len(_text(c))
            cand = [t for t in cand if t[0] + cur_len + 1 <= MAX_CHARS + 8] or cand
            _, j, side = cand[0]
            if side == "prev": cues[j] = cues[j] + c
            else: cues[j] = c + cues[j]
            cues.pop(i); changed = True; break
    return cues

def _split_until_fits(ws: list[Word], depth: int = 0) -> list[list[Word]]:
    """Split, then split the parts that are still too long. One pass leaves a
    tail chunk over the limit whenever the first cut lands short of centre."""
    parts = _split_balanced(ws)
    if len(parts) == 1 or depth > 4: return parts
    out: list[list[Word]] = []
    for p in parts:
        out.extend(_split_until_fits(p, depth + 1) if len(_text(p)) > MAX_CHARS and len(p) > MIN_WORDS else [p])
    return out

def _cut_at(sentences: list[list[Word]], boundaries: list[float]) -> list[list[Word]]:
    """Also split wherever a picture cut falls inside a sentence."""
    out = []
    for s in sentences:
        buf = []
        for w in s:
            if buf and _seg(w, boundaries) != _seg(buf[0], boundaries):
                out.append(buf); buf = []
            buf.append(w)
        if buf: out.append(buf)
    return out

def build(words: list[Word], boundaries: list[float] = ()) -> list[dict]:
    """`boundaries`: picture-cut times (s). A cue never spans one."""
    boundaries = sorted(boundaries)
    chunks: list[list[Word]] = []
    for s in _cut_at(_sentences(words), boundaries):
        chunks.extend(_split_until_fits(s))
    chunks = _merge_short(chunks, boundaries)
    return [{"start": c[0]["start"], "end": c[-1]["end"], "text": _text(c)} for c in chunks]

def audit(cues: list[dict], boundaries: list[float] = ()) -> list[str]:
    """Problems a numeric gate cannot see. Returned, not printed, so callers can
    fail on them."""
    bad = []
    for c in cues:
        for b in boundaries:
            if c["start"] < b - 0.05 and c["end"] > b + 0.05:
                bad.append(f"cue spans the picture cut at {b:.2f}s: {c['text']!r}")
    for c in cues:
        n = len(c["text"].split()); dur = c["end"] - c["start"]
        if n < MIN_WORDS: bad.append(f"orphan cue ({n} word) at {c['start']:.2f}s: {c['text']!r}")
        if dur < MIN_DUR: bad.append(f"cue too brief ({dur:.2f}s) at {c['start']:.2f}s: {c['text']!r}")
        last = c["text"].split()[-1].lower() if c["text"].split() else ""
        if last in WEAK: bad.append(f"cue ends on a weak word ({last!r}) at {c['start']:.2f}s: {c['text']!r}")
        if len(c["text"]) > MAX_CHARS + 8: bad.append(f"cue too long ({len(c['text'])} chars) at {c['start']:.2f}s")
    for a, b in zip(cues, cues[1:]):
        if b["start"] < a["end"] - 1e-6: bad.append(f"cues overlap at {b['start']:.2f}s")
    return bad

# Real tokens that look like a merge: a domain's dot has no space after it. An
# exact list, not a pattern, so a genuine seam like 'cents.Rutherford' is still caught.
DOMAINS = {"cents.vision", "cents.gallery", "rutherfordchang.com"}

MERGE_RE = __import__("re").compile(
    r"(^[.,;:!?])"          # leading punctuation glued to a word
    r"|([.,;:][A-Za-z])"    # punctuation with no space after it, inside a token
    r"|([a-z][A-Z])"        # camelCase seam: two words run together
)

def audit_transcript(words: list[Word]) -> list[str]:
    """Catch aligner noise BEFORE it reaches the screen.

    A scratch pass emitted the token '.opherRutherford' — a segment-boundary
    merge. Fuzzy anchors survived it; the caption did not, and the caption gate
    passed it because malformed words are the right length and the right
    duration. Nothing downstream can tell a real word from a mangled one, so it
    has to be caught here."""
    bad = []
    for w in words:
        t = w["word"]
        if t.rstrip(",;:.!?") in DOMAINS: continue
        if MERGE_RE.search(t): bad.append(f"malformed token {t!r} at {w['start']:.2f}s")
        elif len(t) > 20: bad.append(f"suspiciously long token {t!r} at {w['start']:.2f}s")
    return bad

# ---------------------------------------------------------------- control

def _old_chunker(words: list[Word]) -> list[dict]:
    """The chunker this replaces. Kept ONLY as a control: the audit must flag it.
    An audit that passes both algorithms is not measuring anything."""
    cues, buf = [], []
    for w in words:
        buf.append(w)
        if w["word"].endswith((".", "?")) or len(buf) >= 6 or len(_text(buf)) >= 42:
            cues.append({"start": buf[0]["start"], "end": buf[-1]["end"], "text": _text(buf)}); buf = []
    if buf: cues.append({"start": buf[0]["start"], "end": buf[-1]["end"], "text": _text(buf)})
    return cues

def self_test() -> int:
    import json, pathlib
    # Any film's alignment can be named; the default is the active film's.
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    p = pathlib.Path(args[0]) if args else pathlib.Path(__file__).resolve().parent.parent / "script" / "alignment.json"
    words = json.loads(p.read_text())["words"]
    assert len(words) > 20, f"FLOOR: only {len(words)} words to test with"

    # CONTROL for the transcript audit: a known-good word list must be clean,
    # and the real merge artefact must be flagged.
    assert not audit_transcript([{"word": "witness.", "start": 0, "end": 1}]), "transcript audit false-positives on a normal word"
    probe = audit_transcript([{"word": ".opherRutherford", "start": 0, "end": 1}])
    if not probe:
        print("\033[31mVACUOUS\033[0m transcript audit does not flag the merge artefact it was written for."); return 1
    print(f"CONTROL  transcript audit flags the real artefact: {probe[0]}\n")

    old_bad = audit(_old_chunker(words))
    new_bad = audit(build(words))
    print(f"CONTROL  old chunker: {len(old_bad)} problems")
    for b in old_bad[:4]: print(f"           {b}")
    if not old_bad:
        print("\033[31mVACUOUS\033[0m the audit does not flag the chunker it was written against."); return 1
    print(f"\nNEW      {len(new_bad)} problems")
    for b in new_bad: print(f"           {b}")
    for c in build(words): print(f"  {c['start']:6.2f} ({c['end']-c['start']:.2f}s) {c['text']}")
    return 1 if new_bad else 0

if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else 0)
