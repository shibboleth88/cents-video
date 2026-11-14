"""Check what a take actually SAYS against the text it was asked to say.

Why this exists: `check_take.py` compares a scribe_v1 transcript of the TTS node
with the TTS text. On the ElevenLabs flows, scribe on a TTS node returns the
node's own prompt (the [thoughtfully] [calm] tags even come back as words), so
that comparison passes by construction (LEDGER: "A transcript identical to the
prompt is not evidence of what was said"). Here the take is fetched by URL into
a fresh asset that carries no prompt, so scribe has to recognise the audio. The
signs that it did: no tag tokens, numbers written as digits ("478", "10,000").

Both sides are normalised the same way: every run of number words becomes its
digits, read the way the voice reads them ("four seventy-eight" = 478,
"nineteen sixty-three" = 1963, "ten thousand" = 10000), and a few spellings of
the same sound are folded ("Dope Mind" = "Dopemind", "cents dot vision").

    python3 -I films/wall-blacktongue-character/audio/check_heard.py <heard_words.json> <tts_text.txt> [--control]

`--control` drops one word from the expected text and must fail.

Copied from films/wall-dopemind/audio/check_heard.py for the blacktongue character
episode (2026-11-14). Changes: both sides now go through the one tracked
normaliser (so the check and the alignment cannot disagree), and the recogniser's
written conventions are folded: "No. 3217" = "number 3217", "2.4" = "two point
four", "1,000" = "a thousand", "CL7" = "C L seven", "timeworn" = "time-worn",
"1960s" = "nineteen sixties". The
one proper-name spelling ("DidaTep" for Daidatep) is accepted only from a fixed
list, and every fold used on the heard side is printed, never passed silently.
"""
import json, re, sys

UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
NUMWORDS = set(UNITS) | set(TENS) | {"hundred", "thousand"}
HOMOPHONES = {("where", "wear"), ("sense", "cents")}   # (heard, said); v3: "Cents" came back as "Sense"
ORDINALS = {"ninth": "9"}          # spoken ordinal -> the digits a recogniser writes ("9th" -> "9")


def groups_to_digits(ws):
    """A run of number words -> digits. With hundred/thousand, ordinary arithmetic;
    otherwise pair-reading: each 1-99 group contributes its digits in turn."""
    if "hundred" in ws or "thousand" in ws:
        total, cur = 0, 0
        for w in ws:
            if w in UNITS: cur += UNITS[w]
            elif w in TENS: cur += TENS[w]
            elif w == "hundred": cur *= 100
            elif w == "thousand": total += cur * 1000; cur = 0
        return str(total + cur)
    out, i = [], 0
    while i < len(ws):
        w = ws[i]
        if w in TENS and i + 1 < len(ws) and ws[i + 1] in UNITS and 0 < UNITS[ws[i + 1]] < 10:
            v = TENS[w] + UNITS[ws[i + 1]]; i += 2
        else:
            v = TENS.get(w, UNITS.get(w)); i += 1
        out.append(v)
    if len(out) == 1: return str(out[0])
    return "".join(f"{v:02d}" if k else str(v) for k, v in enumerate(out))


def norm(text, used=None):
    return [t for t, _ in norm_tracked(text.split(), used)]


def main():
    heard = json.load(open(sys.argv[1]))["words"]
    heard = " ".join(w["text"] for w in heard if w.get("type", "word") == "word")
    if re.search(r"\[(thoughtfully|calm)\]", heard):
        sys.exit("INSTRUMENT: the transcript contains the direction tags, so it is the prompt, not the audio")
    used = []
    a, b = norm(heard, used), norm(open(sys.argv[2]).read())
    for u in sorted(set(used)): print(f"recogniser spelling folded: {u}")
    if "--control" in sys.argv: del b[len(b) // 2]
    # Words that sound the same cannot be told apart by any recogniser. Each accepted pair is
    # printed, never passed silently. ("wear" in "time, wear, and accumulated human use" came
    # back as "where" on v2 take 1.)
    if len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y and (x, y) in HOMOPHONES:
                print(f"homophone accepted at token {i}: heard {x!r} for {y!r} ({' '.join(b[max(0,i-3):i+3])})"); a[i] = y
    if a != b:
        k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"MISMATCH at token {k}: heard {a[max(0,k-4):k+4]} vs text {b[max(0,k-4):k+4]} ({len(a)} vs {len(b)} tokens)")
        sys.exit(0 if "--control" in sys.argv else 1)
    if "--control" in sys.argv: sys.exit("CONTROL PASSED, which it must not")
    print(f"heard = text: {len(a)} tokens equal")




# ---- alignment from the recognised timings -------------------------------------------
# `--write-alignment <out.json> <duration>`: give each word of the TTS text the timing of
# the recognised words it was matched to. The two sides are normalised as above, keeping
# track of which original words made each normalised token; where one token spans several
# words (a number said as "four seventy-eight", heard as "478"), those words share the span
# in proportion to their length.

NAME_SPELLINGS = {"didatep": "daidatep", "die2tepp": "daidatep"}   # heard spellings of one proper name
WORD_SPLITS = {"timeworn": ["time", "worn"]}
DECADES = {w: f"{10 * i}s" for i, w in enumerate("_ _ twenties thirties forties fifties sixties seventies eighties nineties".split()) if w != "_"}


def _subtokens(word):
    t = word.lower()
    t = re.sub(r"\[[a-z ]+\]", " ", t)
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t).replace("cents.vision", "cents dot vision").replace("dope_mind", "dope mind")
    t = re.sub(r"(\d)\.(\d)", r"\1 point \2", t)                  # 2.4 -> 2 point 4
    t = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", t)
    for w, d in ORDINALS.items(): t = re.sub(rf"\b{w}\b", d, t)
    t = re.sub(r"[.,;:!?\"]", " | ", t.replace("-", " "))
    return re.sub(r"[^a-z0-9|]+", " ", t).split()


def norm_tracked(words, used=None):
    used = [] if used is None else used
    subs = []
    for i, w in enumerate(words):
        for s in _subtokens(w):
            if s in NAME_SPELLINGS: used.append(f"{s!r} = {NAME_SPELLINGS[s]!r}"); s = NAME_SPELLINGS[s]
            if s in WORD_SPLITS:
                used.append(f"{s!r} = {' '.join(WORD_SPLITS[s])!r}"); subs += [(x, i) for x in WORD_SPLITS[s]]; continue
            subs.append((s, i))
    merged, k = [], 0
    while k < len(subs):
        s, i = subs[k]
        nxt = [x[0] for x in subs[k + 1:k + 3]]
        if s == "dope" and nxt[:1] == ["mind"]:                     # "dope mind" = "dopemind"
            merged.append(("dopemind", {i, subs[k + 1][1]})); k += 2
        elif s == "c" and nxt == ["l", "seven"]:                    # "C L seven" = "CL7"
            merged.append(("cl7", {i, subs[k + 1][1], subs[k + 2][1]})); k += 3
        elif s == "cl7":
            merged.append(("cl7", {i})); k += 1
        elif s == "a" and nxt[:1] in (["hundred"], ["thousand"]):   # "a thousand" = "1,000"
            merged.append(("one", {i})); k += 1
        elif s == "no" and nxt[:1] == ["|"] and len(nxt) > 1 and nxt[1][:1].isdigit():   # "No. 3217"
            used.append("'No.' = 'number'"); merged.append(("number", {i})); k += 2
        else:
            merged.append((s, {i})); k += 1
    out, run, src = [], [], set()
    for s, ids in merged + [("|", set())]:
        if s in NUMWORDS: run.append(s); src |= ids; continue
        if run and s in DECADES:                                    # "nineteen sixties" = "1960s"
            out.append((groups_to_digits(run) + DECADES[s], src | ids)); run, src = [], set(); continue
        if run: out.append((groups_to_digits(run), src)); run, src = [], set()
        if s != "|": out.append((s, ids))
    return out


def write_alignment(heard_words, tts_text, out_path, duration, source):
    tts = tts_text.split()
    A, B = norm_tracked([w["text"] for w in heard_words]), norm_tracked(tts)
    if len(A) != len(B): sys.exit(f"REFUSING: {len(A)} heard tokens vs {len(B)} text tokens")
    timing = {}
    for (ta, ha), (tb, wb) in zip(A, B):
        if ta != tb and (ta, tb) not in HOMOPHONES: sys.exit(f"REFUSING: heard {ta!r} vs text {tb!r}")
        s0, s1 = min(heard_words[h]["start"] for h in ha), max(heard_words[h]["end"] for h in ha)
        ws = sorted(wb)
        L = sum(len(tts[w]) for w in ws); t = s0
        for w in ws:
            d = (s1 - s0) * len(tts[w]) / L
            prev = timing.get(w)
            timing[w] = (min(prev[0], t), max(prev[1], t + d)) if prev else (t, t + d)
            t += d
    missing = [i for i in range(len(tts)) if i not in timing]
    if missing: sys.exit(f"REFUSING: no timing for words {[tts[i] for i in missing[:5]]}")
    words = [{"word": tts[i], "start": round(timing[i][0], 3), "end": round(timing[i][1], 3)} for i in range(len(tts))]
    for a, b in zip(words, words[1:]):
        if b["start"] < a["start"]: sys.exit(f"REFUSING: timing goes backwards at {b['word']!r}")
    json.dump({"_source": source, "words": words, "duration": duration}, open(out_path, "w"), indent=1)
    print(f"wrote {out_path}: {len(words)} words, duration {duration}")


if __name__ == "__main__" and "--write-alignment" in sys.argv:
    i = sys.argv.index("--write-alignment")
    hw = [w for w in json.load(open(sys.argv[1]))["words"] if w.get("type", "word") == "word"]
    write_alignment(hw, open(sys.argv[2]).read(), sys.argv[i + 1], float(sys.argv[i + 2]), sys.argv[i + 3])


if __name__ == "__main__" and "--write-alignment" not in sys.argv:
    main()
