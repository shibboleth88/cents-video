#!/usr/bin/env python3
"""Script fidelity gates — run BEFORE anything is recorded or rendered.

The previous production's real failures were not rendering bugs. They were
comprehension failures: an incidental fact promoted to the organising principle,
a thesis cleaner than the source supported, the satoshi conflated with its
inscription and with the penny. No amount of ffmpeg catches any of that.

  python3 pipeline/fidelity.py
  python3 pipeline/fidelity.py --self-test   # corrupt the script, require RED
"""
from __future__ import annotations
import argparse, difflib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = ROOT / "script"

class Fail(Exception): pass

class Unbuildable(Exception):
    """A control could not be constructed: the subject lacks what it corrupts."""


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("—", "-")).strip().lower()

def sentences(text: str) -> list[str]:
    body = "\n".join(l for l in text.splitlines() if l.strip())
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", body) if s.strip()]

# ---------------------------------------------------------------- gates

def g_coverage(vo: str, cl: dict) -> str:
    """Every spoken sentence must be accounted for. An unmapped sentence is
    exactly where an invented thesis enters unchallenged."""
    said = sentences(vo)
    mapped = {norm(c["say"]) for c in cl["claims"]}
    if not said: raise Fail("voiceover.txt is empty — nothing to check")
    missing = [s for s in said if norm(s) not in mapped]
    if missing:
        raise Fail(f"{len(missing)} narration sentence(s) not in the claims ledger: " +
                   "; ".join(repr(m[:60]) for m in missing[:3]))
    extra = [c["say"] for c in cl["claims"] if norm(c["say"]) not in {norm(s) for s in said}]
    if extra:
        raise Fail(f"{len(extra)} ledger entr(ies) are not spoken — the ledger describes a different script: " +
                   "; ".join(repr(e[:50]) for e in extra[:3]))
    return f"{len(said)} narration sentences, all mapped"

def g_spans(essay: str, cl: dict) -> str:
    """A cited span must actually exist in the essay. This is the gate that
    catches a citation that was never there to begin with."""
    hay = norm(essay)
    missing = [c for c in cl["claims"] if c["kind"] in ("quotation", "paraphrase")
               and norm(c.get("span", "")) not in hay]
    if missing:
        raise Fail(f"{len(missing)} cited span(s) do not appear in the essay: " +
                   "; ".join(repr(norm(c.get("span",""))[:50]) for c in missing[:3]))
    n = sum(1 for c in cl["claims"] if c["kind"] in ("quotation", "paraphrase"))
    if n == 0: raise Fail("no quotations or paraphrases to check — the ledger is all additions")
    return f"{n} cited spans all located in the essay"

def g_quotation_exact(essay: str, cl: dict, tol=0.90) -> str:
    """Tagged as a quotation means the words are the essay's. Near-misses that
    change the claim are the dangerous case, so compare against the span."""
    hay = norm(essay)
    bad = []
    for c in cl["claims"]:
        if c["kind"] != "quotation": continue
        say, span = norm(c["say"]).rstrip(".?!"), norm(c["span"]).rstrip(".?!")
        r = difflib.SequenceMatcher(None, say, span).ratio()
        if r < tol: bad.append(f"{c['say'][:48]!r} vs span (similarity {r:.2f})")
    if bad: raise Fail(f"{len(bad)} quotation(s) diverge from the cited span: " + "; ".join(bad[:3]))
    q = sum(1 for c in cl["claims"] if c["kind"] == "quotation")
    if q == 0: raise Fail("no quotations tagged — nothing for this gate to measure")
    return f"{q} quotations match their spans"

def g_additions(cl: dict) -> str:
    """Additions are legitimate — they are how a film explains. They must be
    VISIBLE and approved, not smuggled in as if the essay said them."""
    adds = [c for c in cl["claims"] if c["kind"] == "addition"]
    un = [c for c in adds if not c.get("approved")]
    if un:
        raise Fail(f"{len(un)} unapproved addition(s) — these are not in the essay and need your sign-off: " +
                   "; ".join(repr(c["say"][:60]) for c in un[:3]))
    return f"{len(adds)} additions, all approved" if adds else "no additions"

def g_terminology(vo: str, gl: dict) -> str:
    hits = []
    for f in gl["forbidden_phrases"]:
        for m in re.finditer(f["pattern"], vo):
            hits.append(f"{m.group(0)!r} — {f['why']}")
    if hits: raise Fail(f"{len(hits)} forbidden phrase(s): " + "; ".join(hits[:3]))
    if not gl["forbidden_phrases"]: raise Fail("glossary has no forbidden phrases — gate is vacuous")
    return f"{len(gl['forbidden_phrases'])} phrase rules, no violations"

def g_equations(vo: str, gl: dict) -> str:
    """Catch the script asserting that two things the essay holds apart are the
    same thing. Mechanical and therefore partial: it finds the explicit form."""
    bad = []
    for e in gl["must_not_equate"]:
        a, b = re.escape(e["a"]), re.escape(e["b"])
        pat = rf"(?i){a}\s+(is|are|means|equals|amounts to)\s+{b}|{b}\s+(is|are|means|equals|amounts to)\s+{a}"
        if re.search(pat, vo): bad.append(f"{e['a']} == {e['b']} — {e['why']}")
    if bad: raise Fail("; ".join(bad))
    return f"{len(gl['must_not_equate'])} distinctions checked for explicit collapse"

# A source's deictic points at the SOURCE'S date, not the film's. The script
# once read "288 billion still in existence" against a span dated March 2024 -
# "still" was added by the narration and asserted a 2026 measurement nobody
# made. Nothing caught it, because every per-claim check looked only at whether
# the span existed, never at when it was written.
DEICTICS = r"\b(now|currently|still|today|nowadays|at present|these days|to date|so far|at the moment)\b"
TIMEVARY = [
    (r"\b(18|19|20)\d\d\b",                      "names a year"),
    (r"\b(billion|million|trillion)\b",           "states a population"),
    (r"\bcents?\b|\u00a2",                           "states a money value"),
    (r"\bsats?\b|\bsatoshis?\b",                    "states a price in satoshis"),
    (r"\bkilograms?\b|\bkg\b|\bpounds?\b",          "states a mass"),
    (r"\b(worth|valued|asking|listed|price[sd]?)\b", "states a valuation"),
    (r"\b(most|least|largest|smallest|biggest|only|first|last)\b", "makes a superlative or uniqueness claim"),
]

def g_epochs(cl: dict) -> str:
    """Every time-varying claim must say which moment it describes (epoch) and
    when its source was written or measured (as_of). Mechanical and therefore
    partial: it detects years, populations, money, mass and superlatives."""
    bad, n_tv = [], 0
    for i, c in enumerate(cl["claims"]):
        say, span = c.get("say", ""), str(c.get("span", ""))
        d = re.search(DEICTICS, say, re.I)
        if d:
            bad.append(f"claim {i} narration contains the deictic '{d.group(0)}' - convert it to the "
                       f"source's absolute date: {say[:60]!r}")
        why = [w for pat, w in TIMEVARY if re.search(pat, say + " " + span, re.I)]
        if not why:
            continue
        n_tv += 1
        for field in ("epoch", "as_of"):
            if not str(c.get(field, "")).strip():
                bad.append(f"claim {i} {why[0]} but declares no {field}: {say[:60]!r}")
    # Floors. A ledger whose claims happen to contain no years, no money and no
    # superlatives has almost certainly not been read by this gate at all, and a
    # pass would then mean "found nothing to check" - which renders identically
    # to "everything is dated".
    if not cl["claims"]:
        raise Fail("the ledger holds no claims - the gate has nothing to measure")
    if n_tv == 0:
        raise Fail(f"no time-varying claim found among {len(cl['claims'])} claims - "
                   f"the detector is broken, not the script")
    if bad:
        raise Fail(f"{len(bad)} epoch problem(s): " + "; ".join(bad[:3]))
    return f"{n_tv}/{len(cl['claims'])} claims are time-varying; each declares epoch and as_of"

def g_distinctions_reviewed(cl: dict) -> str:
    """The semantic half. A machine cannot settle it, so it must be ANSWERED,
    with the answer recorded and attributable — not left blank and assumed."""
    ds = cl.get("distinctions_kept", [])
    if not ds: raise Fail("no distinctions recorded — the essay's conceptual distinctions were never enumerated")
    bad = [d for d in ds if d.get("verdict") not in ("kept", "n/a")]
    if bad: raise Fail(f"{len(bad)} distinction(s) not confirmed kept: " +
                       "; ".join(repr(d["distinction"][:50]) for d in bad[:3]))
    return f"{len(ds)} distinctions reviewed and recorded as kept"

def g_thesis(cl: dict) -> str:
    t = (cl.get("thesis") or "").strip()
    if len(t.split()) < 6: raise Fail("no stated thesis — without one, 'the script is faithful' has no referent")
    return f"thesis stated ({len(t.split())} words)"

TEXT_KEYS = ("title", "subtitle", "quote", "attribution", "caption", "author", "readout", "centre")
TEXT_LISTS = ("lines", "nodes", "items")

def _onscreen(tl: dict) -> list[tuple[str, str, str]]:
    """(shot_id, field, text) for every string the viewer reads on screen.

    Walks nested props, because a diagram keeps its labels inside states[] and
    nodes[] — and text the ledger cannot see is text that can say anything. This
    is the same escape route a raw styled div used past the bounds gate."""
    out = []

    def walk(sid: str, node, path: str):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in TEXT_KEYS and isinstance(v, str) and v.strip():
                    out.append((sid, f"{path}{k}", v))
                elif k in TEXT_LISTS and isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, str) and item.strip():
                            out.append((sid, f"{path}{k}[{i}]", item))
                else:
                    walk(sid, v, f"{path}{k}.")
        elif isinstance(node, list):
            for i, item in enumerate(node): walk(sid, item, f"{path}{i}.")

    for sh in tl["shots"]:
        walk(sh["shot_id"], sh.get("props") or {}, "")
    return out

def g_onscreen_covered(tl: dict, cl: dict) -> str:
    """Words on screen are claims too. The claims ledger covered only the
    NARRATION, so a quotation from the essay could be — and was — credited on
    screen to the wrong person with every gate green."""
    spoken = {norm(c["say"]).rstrip(".?!") for c in cl["claims"]}
    declared = {norm(o["text"]).rstrip(".?!") for o in cl.get("onscreen", [])}
    unc = [(sid, f, t) for sid, f, t in _onscreen(tl)
           if norm(t).rstrip(".?!") not in spoken | declared]
    if unc:
        raise Fail(f"{len(unc)} on-screen string(s) not in the ledger: " +
                   "; ".join(f"{sid}.{f}={t[:34]!r}" for sid, f, t in unc[:3]))
    n = len(_onscreen(tl))
    if n == 0: raise Fail("no on-screen text found — the gate has nothing to measure")
    return f"{n} on-screen strings all traceable to the ledger"

def g_attributions(tl: dict, cl: dict) -> str:
    """An attribution names who said a thing. Getting it wrong is the most
    quietly damaging error a title card can make, so each one is declared and
    signed off rather than inferred from whoever is nearby in the script."""
    att = [(sid, t) for sid, f, t in _onscreen(tl) if f == "attribution"]
    ok = {(a["shot_id"], norm(a["attributed_to"])) for a in cl.get("attributions", [])
          if a.get("verdict") == "correct"}
    bad = [(sid, t) for sid, t in att if (sid, norm(t)) not in ok]
    if bad:
        raise Fail(f"{len(bad)} unverified attribution(s): " +
                   "; ".join(f"{sid} credits {t!r}" for sid, t in bad))
    return f"{len(att)} attributions verified" if att else "no attributions on screen"

# ---------------------------------------------------------------- controls

def self_test() -> int:
    essay = (S/"essay.txt").read_text(); vo = (S/"voiceover.txt").read_text()
    cl = json.loads((S/"claims.json").read_text()); gl = json.loads((S/"glossary.json").read_text())
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())

    def corrupt_unmapped():
        v = vo + "\nThe work is ultimately about the fragility of all value.\n"
        return lambda: g_coverage(v, cl)
    def corrupt_fabricated_span():
        # Target the first claim g_spans actually INSPECTS. claims[1] was a
        # paraphrase on the first two films and an addition on the Sets film,
        # so the fixed index planted the fake span where the gate never looks
        # and the control passed: VACUOUS on 2026-10-24.
        c = json.loads(json.dumps(cl))
        i = next((j for j, x in enumerate(c["claims"]) if x["kind"] in ("quotation", "paraphrase")), None)
        if i is None:
            raise Unbuildable("no quotation or paraphrase claim to give a fabricated span")
        c["claims"][i]["span"] = "Chang has described the project as a meditation on entropy."
        return lambda: g_spans(essay, c)
    def corrupt_misquote():
        # Target the first claim actually TAGGED as a quotation. A fixed index
        # silently decouples from the ledger: claims[3] was a paraphrase, which
        # g_quotation_exact does not inspect, so this control passed for every
        # script it was ever run against.
        c = json.loads(json.dumps(cl))
        i = next((j for j, x in enumerate(c["claims"]) if x["kind"] == "quotation"), None)
        if i is None:
            return lambda: (_ for _ in ()).throw(
                Fail("no claim is tagged quotation - this control has nothing to misquote"))
        c["claims"][i]["say"] = "The object vanishes."
        return lambda: g_quotation_exact(essay, c)
    def corrupt_addition():
        c = json.loads(json.dumps(cl))
        c["claims"].append({"say": "Brenner's portrait is the most reproduced artwork in history.",
                            "kind": "addition", "approved": False})
        return lambda: g_additions(c)
    def corrupt_distancing():
        return lambda: g_terminology(vo + "\nThe essay argues that the gap is the point.\n", gl)
    def corrupt_equation():
        # Was a hardcoded "Attention is recovery." - a pair from the objecthood
        # film's glossary. Carried to a film with a different glossary it asserted
        # nothing the gate looks for, so the control read green and the gate was
        # never shown able to fire. Build the collapse out of the glossary under
        # test instead, so the control cannot decouple from its subject again.
        pairs = gl.get("must_not_equate") or []
        if not pairs:
            raise Unbuildable("glossary declares no must_not_equate pairs to collapse")
        e = pairs[0]
        return lambda: g_equations(vo + f"\n{e['a']} is {e['b']}.\n", gl)
    def corrupt_distinction():
        c = json.loads(json.dumps(cl)); c["distinctions_kept"][0]["verdict"] = "collapsed"
        return lambda: g_distinctions_reviewed(c)
    def corrupt_thesis():
        c = json.loads(json.dumps(cl)); c["thesis"] = ""
        return lambda: g_thesis(c)

    # A control that cannot be built is not a control that passed, and it is not
    # a control that fired. Before this, corrupt_onscreen() indexed shots[1] and
    # raised IndexError on a film whose timeline is still a stub - crashing the
    # whole suite, so the eight controls that COULD be built were never reported.
    # The three outcomes are now distinct: RED (fired), VACUOUS (gate is blind),
    # UNBUILDABLE (the subject has nothing for this control to corrupt yet).
    def _shot_for_control(t, prop, value):
        shots = t.get("shots") or []
        targets = [sh for sh in shots if isinstance(sh.get("props"), dict)]
        if not targets:
            raise Unbuildable(
                f"timeline has {len(shots)} shots with props - nothing to put bad {prop} on")
        targets[min(1, len(targets) - 1)]["props"][prop] = value

    def corrupt_undated():
        # Must strip the epoch from a claim the gate actually INSPECTS. The first
        # version took the first claim carrying an epoch, which was line 1 - not
        # time-varying by the detector, so removing its epoch changed nothing and
        # the control read green. Select with the gate's own detector instead.
        c = json.loads(json.dumps(cl))
        def timevary(x):
            blob = x.get("say", "") + " " + str(x.get("span", ""))
            return any(re.search(pat, blob, re.I) for pat, _ in TIMEVARY)
        i = next((j for j, x in enumerate(c["claims"])
                  if timevary(x) and str(x.get("epoch", "")).strip()), None)
        if i is None:
            raise Unbuildable("no time-varying claim declares an epoch - nothing to strip")
        c["claims"][i].pop("epoch", None)
        return lambda: g_epochs(c)
    def corrupt_deictic():
        c = json.loads(json.dumps(cl))
        i = next((j for j, x in enumerate(c["claims"])
                  if re.search(r"\b(18|19|20)\d\d\b", x.get("say", ""))), None)
        if i is None:
            raise Unbuildable("no claim names a year - nothing to re-deicticise")
        c["claims"][i]["say"] = c["claims"][i]["say"] + " It is still true now."
        return lambda: g_epochs(c)
    def corrupt_onscreen():
        t = json.loads(json.dumps(tl))
        _shot_for_control(t, "quote", "CENTS is finally about the fragility of money.")
        return lambda: g_onscreen_covered(t, cl)
    def corrupt_attribution():
        t = json.loads(json.dumps(tl))
        _shot_for_control(t, "attribution", "Marcel Duchamp")
        return lambda: g_attributions(t, cl)

    controls = [
        ("coverage / invented thesis", corrupt_unmapped),
        ("unledgered on-screen text",  corrupt_onscreen),
        ("wrong attribution",          corrupt_attribution),
        ("fabricated citation",        corrupt_fabricated_span),
        ("misquotation",               corrupt_misquote),
        ("unapproved addition",        corrupt_addition),
        ("distancing phrase",          corrupt_distancing),
        ("collapsed distinction",      corrupt_equation),
        ("unconfirmed distinction",    corrupt_distinction),
        ("missing thesis",             corrupt_thesis),
        ("undated time-varying claim", corrupt_undated),
        ("uncoverted source deictic",  corrupt_deictic),
    ]
    print("CONTROLS \u2014 each corrupts the script in a way a production actually shipped.\n")
    bad = 0; unbuilt = []
    for name, build in controls:
        try:
            fn = build()
        except Unbuildable as e:
            print(f"  \033[33mUNBUILT\033[0m {name:<28} {e}"); unbuilt.append(name); continue
        try:
            fn()
            print(f"  \033[31mVACUOUS\033[0m {name:<28} passed a script that should fail"); bad += 1
        except Unbuildable as e:
            print(f"  \033[33mUNBUILT\033[0m {name:<28} {e}"); unbuilt.append(name)
        except Fail as e:
            print(f"  \033[32mRED\033[0m     {name:<28} {str(e)[:84]}")
    built = len(controls) - len(unbuilt)
    print(f"\n{built-bad}/{built} buildable controls went red"
          f" ({len(controls)} gates, {len(unbuilt)} control(s) unbuildable).")
    if unbuilt:
        print("  unbuildable: " + ", ".join(unbuilt)
              + "\n  these gates are UNDEMONSTRATED on this film - not passing, not failing.")
    # A suite that could not build half its controls has not vouched for itself.
    return 1 if bad or len(unbuilt) > len(controls) // 2 else 0

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test: return self_test()
    essay = (S/"essay.txt").read_text(); vo = (S/"voiceover.txt").read_text()
    cl = json.loads((S/"claims.json").read_text()); gl = json.loads((S/"glossary.json").read_text())
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    checks = [("thesis stated", lambda: g_thesis(cl)),
              ("on-screen text ledgered", lambda: g_onscreen_covered(tl, cl)),
              ("attributions verified", lambda: g_attributions(tl, cl)),
              ("sentence coverage", lambda: g_coverage(vo, cl)),
              ("cited spans exist", lambda: g_spans(essay, cl)),
              ("quotations exact", lambda: g_quotation_exact(essay, cl)),
              ("additions approved", lambda: g_additions(cl)),
              ("terminology", lambda: g_terminology(vo, gl)),
              ("distinctions not collapsed", lambda: g_equations(vo, gl)),
              ("distinctions reviewed", lambda: g_distinctions_reviewed(cl)),
              ("epochs declared", lambda: g_epochs(cl))]
    fails = 0
    for n, fn in checks:
        try: print(f"  \033[32mPASS\033[0m {n:<28} {fn()}")
        except Fail as e: print(f"  \033[31mFAIL\033[0m {n:<28} {e}"); fails += 1
    print(f"\n{len(checks)-fails}/{len(checks)} fidelity gates passed.")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
