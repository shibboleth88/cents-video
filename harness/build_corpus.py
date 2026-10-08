#!/usr/bin/env python3
"""Extract labeled defect pairs from this repo's own script history.

Each case is a commit whose message names a relational defect it fixed. The
parent holds the defect; the commit holds the fix. That gives a positive and a
negative for the same relation, so a reviewer can be scored for recall AND
precision rather than only asked whether it says something plausible.

Honest limits, recorded here because they bound every number computed from it:
  - These are defects a human CAUGHT. Nothing here represents one that shipped
    unnoticed, so measured recall is recall against known-findable problems.
  - They are one author's failure modes on one project.
  - Several commits fix more than one thing. `also_fixed` records that, so a
    case is never read as a clean single-variable manipulation when it isn't.
  - A script that is the negative for one relation may be the positive for
    another; `other_relations_present` records it, and precision is therefore
    scored per-relation.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "harness" / "corpus"
PATH = "script/voiceover.txt"

RELATIONS = {
    "order-causation": "Order asserts causation: putting B after A proposes that A explains B, though no sentence says so.",
    "dangling-premise": "A cut premise leaves its conclusion standing: a surviving sentence refers to something no longer in the piece.",
    "synonym-repetition": "Repetition in synonyms mistaken for emphasis: restatements that add no new register, only another word for the last one.",
    "foreign-passage": "A passage answering a question the piece never asked.",
}

CASES = [
    {
        "id": "order-causation-brenner",
        "commit": "6ebc608",
        "relation": "order-causation",
        "defect": "The script opens on Brenner's Lincoln being the most reproduced artwork on "
                  "Earth, and the next line is 'This is the readymade Rutherford Chang chose.' "
                  "The sequence asserts that the portrait's ubiquity was the REASON for the "
                  "choice. The source gives the origin as a value discrepancy. A property of "
                  "the readymade is not a motive for selecting it.",
        "evidence_lines_before": [1, 2],
        "fix": "Opens on the value discrepancy; Brenner demoted to a property of the object, stated after the origin.",
        "also_fixed": ["Restructured the closing passage; replaced the objecthood arc."],
        "other_relations_present": {"before": [], "after": ["dangling-premise"]},
    },
    {
        "id": "dangling-premise-remained",
        "commit": "6ccd148",
        "relation": "dangling-premise",
        "defect": "'The object remained, buoyed into physicality by the force of its context.' "
                  "has no antecedent: nothing earlier says the penny lost its function, so "
                  "'remained' refers to nothing in the piece.",
        "evidence_lines_before": [5],
        "fix": "Adds 'Nothing has been sold for a single cent since before Chang was born.' "
               "immediately before it, and makes the line a 'Yet...' continuation.",
        "also_fixed": ["'hundreds or thousands' -> 'thousands'", "cut a decoupling line"],
        "other_relations_present": {"before": [], "after": []},
    },
    {
        "id": "dangling-premise-set",
        "commit": "7fdce22",
        "relation": "dangling-premise",
        "defect": "'Each object, initially identical, bears the marks of touch and time.' "
                  "depends on a permanent set of ten thousand that the script never "
                  "establishes, so 'each object' has no set to be a member of.",
        "evidence_lines_before": [17],
        "fix": "Adds 'A permanent set of ten thousand, with its own logics and rarities.' before it.",
        "also_fixed": [],
        "other_relations_present": {"before": ["synonym-repetition"], "after": ["synonym-repetition", "foreign-passage"]},
    },
    {
        "id": "synonym-repetition-redefinition",
        "commit": "2f9c7cd",
        "relation": "synonym-repetition",
        "defect": "Continual redefinition is stated three times in six lines, sharing the root "
                  "'redefin': 'continually redefined by decentralized consensus', 'an ongoing "
                  "process of redefinition', and 'indeterminate and continually redefined'. "
                  "None adds a register the previous one lacked.",
        "evidence_lines_before": [16, 17, 21],
        "fix": "Cuts two; keeps the mechanism inside the transformation list and replaces the "
               "others with register-distinct lines (collectors reading the set; canon).",
        "also_fixed": ["Rewrote the canon simile as a grammatical continuation."],
        "other_relations_present": {"before": ["foreign-passage"], "after": []},
    },
]

def show(commit, path):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: git show {commit}:{path} failed: {r.stderr.strip()}")
    return r.stdout

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for c in CASES:
        before = show(c["commit"] + "^", PATH)
        after = show(c["commit"], PATH)
        # Floors. A corpus that silently extracts nothing reads exactly like a
        # corpus of clean cases, and every score computed from it would be noise.
        assert before.strip(), f"{c['id']}: before is empty"
        assert after.strip(), f"{c['id']}: after is empty"
        assert before != after, f"{c['id']}: before and after are identical - no manipulation"
        bl = before.strip().splitlines()
        for ln in c["evidence_lines_before"]:
            assert 1 <= ln <= len(bl), f"{c['id']}: evidence line {ln} outside 1..{len(bl)}"
        d = OUT / c["id"]; d.mkdir(exist_ok=True)
        (d / "before.txt").write_text(before)
        (d / "after.txt").write_text(after)
        meta = dict(c)
        meta["relation_definition"] = RELATIONS[c["relation"]]
        meta["before_lines"] = len(bl)
        meta["after_lines"] = len(after.strip().splitlines())
        meta["evidence_text"] = [bl[i - 1] for i in c["evidence_lines_before"]]
        (d / "label.json").write_text(json.dumps(meta, indent=1) + "\n")
        index.append({"id": c["id"], "relation": c["relation"], "commit": c["commit"],
                      "subject": subprocess.run(
                          ["git", "-C", str(ROOT), "log", "-1", "--format=%s", c["commit"]],
                          capture_output=True, text=True).stdout.strip()})
    assert len(index) == len(CASES) >= 4, f"expected >=4 cases, built {len(index)}"
    rels = {c["relation"] for c in CASES}
    assert len(rels) >= 3, f"expected >=3 distinct relations, got {rels}"
    (OUT / "index.json").write_text(json.dumps(
        {"cases": index, "relations": RELATIONS,
         "limits": ["defects a human caught, not defects that shipped unnoticed",
                    "one author, one project",
                    "several commits fix more than one thing (see also_fixed)",
                    "a negative for one relation can be a positive for another"]},
        indent=1) + "\n")
    print(f"{len(index)} cases, {len(rels)} relations -> {OUT}")
    for c in index:
        print(f"  {c['id']:<34} {c['relation']:<20} {c['commit']}")

if __name__ == "__main__":
    main()
