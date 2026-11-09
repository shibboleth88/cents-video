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

    python3 -I films/wall-dopemind/audio/check_heard.py <heard_words.json> <tts_text.txt> [--control]

`--control` drops one word from the expected text and must fail.
"""
import json, re, sys

UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
NUMWORDS = set(UNITS) | set(TENS) | {"hundred", "thousand"}


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


def norm(text):
    t = text.lower()
    t = re.sub(r"\[[a-z ]+\]", " ", t)                    # direction tags, if any reached the text
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)               # 10,000 -> 10000
    t = t.replace("cents.vision", "cents dot vision").replace("dope mind", "dopemind")
    # Punctuation ends a number run ("nineteen seventy-nine, one of the three" is 1979 then 1),
    # and is then dropped, so it never has to agree between the two sides.
    t = re.sub(r"[.,;:!?\"]", " | ", t.replace("-", " "))
    toks = re.sub(r"[^a-z0-9|]+", " ", t).split()
    out, run = [], []
    for w in toks + ["|"]:
        if w in NUMWORDS: run.append(w); continue
        if run: out.append(groups_to_digits(run)); run = []
        if w != "|": out.append(w)
    return out


def main():
    heard = json.load(open(sys.argv[1]))["words"]
    heard = " ".join(w["text"] for w in heard if w.get("type", "word") == "word")
    if re.search(r"\[(thoughtfully|calm)\]", heard):
        sys.exit("INSTRUMENT: the transcript contains the direction tags, so it is the prompt, not the audio")
    a, b = norm(heard), norm(open(sys.argv[2]).read())
    if "--control" in sys.argv: del b[len(b) // 2]
    if a != b:
        k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"MISMATCH at token {k}: heard {a[max(0,k-4):k+4]} vs text {b[max(0,k-4):k+4]} ({len(a)} vs {len(b)} tokens)")
        sys.exit(0 if "--control" in sys.argv else 1)
    if "--control" in sys.argv: sys.exit("CONTROL PASSED, which it must not")
    print(f"heard = text: {len(a)} tokens equal")


if __name__ == "__main__":
    main()
