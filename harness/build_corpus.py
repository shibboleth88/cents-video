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


# Clean drafts: negatives, so precision has something to be measured against.
# Run 1 could not measure precision for synonym-repetition because the corpus
# held only two cells where the relation was absent. "Clean" is adjudicated per
# relation below, not assumed - each rationale points at the text.
CLEAN = [
    {
        "id": "clean-introduction",
        "source": {"worktree": "films/introduction/script/voiceover.txt"},
        "note": "The 3-minute introduction script, written after all three shapes were known.",
        "absent": {
            "invented-motive": "Every decision line is preceded by an explicit temporal marker "
                               "('Then he destroyed them', 'Each photograph he inscribed'), and the "
                               "origin is stated outright at 1-5 ('Recognising those discrepancies'). "
                               "The adjacency I considered hardest is 18->19 (indestructible ingot, "
                               "then release at one sat each); 'He released' follows a property, but "
                               "no motive is proposed and the stated origin precedes it.",
            "dangling-premise": "The set of ten thousand is introduced at 5, before every quantifier "
                                "over it ('More than half the set' at 14, 'all ten thousand' at 19). "
                                "'The project had described this as coming' at 23 is resolved by the "
                                "colon in its own line.",
            "synonym-repetition": "'redefined' occurs once, at 24. Continual redefinition is carried "
                                  "structurally (closed set -> arbitrary edges -> value still moving) "
                                  "rather than by restatement.",
        },
    },
    {
        "id": "clean-objecthood-shipped",
        "source": {"worktree": "films/objecthood/script/voiceover.txt"},
        "note": "The script as recorded and released.",
        "absent": {
            "invented-motive": "Line 1 states the origin and contains it ('began CENTS with a simple "
                               "value discrepancy'). Line 4 is the single-line form ('The readymade he "
                               "chose is also perhaps the most reproduced...'), which is one claim, not "
                               "a property-then-decision order.",
            "dangling-premise": "'yet the object remained' at 3 carries its premise in the same "
                                "sentence. 'each with the portrait' at 5 is anchored in its own line. "
                                "'every cent' at 10 is a universal over a kind inside the clause that "
                                "introduces the system, not a claim about a bounded population - there "
                                "is no 'initially identical' style assertion requiring fixed membership.",
            "synonym-repetition": "15, 16 and 17 touch indeterminacy in three different registers - "
                                  "mechanism (redefined by consensus), object (a vessel of indeterminate "
                                  "value), form (CENTS is a becoming). Three registers, not three synonyms.",
        },
    },
    {
        "id": "clean-objecthood-bridge",
        "source": {"ref": "5ae2a21", "path": "script/voiceover.txt"},
        "note": "The state after the collector-dynamics passage was replaced by the three-line bridge.",
        "absent": {
            "invented-motive": "Decisions at 1 (reason in the line) and 5 (single-line form). No "
                               "property-then-decision pair.",
            "dangling-premise": "'Yet the object remained' at 4 is anchored by 3. 'each Cent' at 18 is "
                                "anchored by 'Ten thousand inscriptions, and never any more' at 17. "
                                "'The way words do' at 19 is a grammatical continuation of 18.",
            "synonym-repetition": "Continual redefinition occurs at 16 (mechanism) and 20 (form). Two "
                                  "registers, no restatement.",
        },
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
                      "versions": ["before", "after"],
                      "subject": subprocess.run(
                          ["git", "-C", str(ROOT), "log", "-1", "--format=%s", c["commit"]],
                          capture_output=True, text=True).stdout.strip()})
    for c in CLEAN:
        src = c["source"]
        if "worktree" in src:
            f = ROOT / src["worktree"]
            assert f.is_file(), f"{c['id']}: {f} is not a file"
            text = f.read_text()
            origin = f"worktree:{src['worktree']}"
        else:
            text = show(src["ref"], src["path"])
            origin = f"{src['ref']}:{src['path']}"
        assert text.strip(), f"{c['id']}: clean draft is empty"
        assert len(text.strip().splitlines()) >= 10, \
            f"{c['id']}: only {len(text.strip().splitlines())} lines - too short to review"
        d = OUT / c["id"]; d.mkdir(exist_ok=True)
        (d / "only.txt").write_text(text)
        meta = dict(c); meta["origin"] = origin
        meta["lines"] = len(text.strip().splitlines())
        meta["kind"] = "clean"
        (d / "label.json").write_text(json.dumps(meta, indent=1) + "\n")
        index.append({"id": c["id"], "relation": None, "commit": None,
                      "versions": ["only"], "subject": c["note"]})

    assert len(index) == len(CASES) + len(CLEAN) >= 7, f"expected >=7 cases, built {len(index)}"
    n_clean = sum(1 for c in index if c["versions"] == ["only"])
    assert n_clean >= 3, f"expected >=3 clean drafts, built {n_clean}"
    n_scripts = sum(len(c["versions"]) for c in index)
    assert n_scripts >= 11, f"expected >=11 scripts, built {n_scripts}"
    rels = {c["relation"] for c in CASES}
    assert len(rels) >= 3, f"expected >=3 distinct relations, got {rels}"
    (OUT / "index.json").write_text(json.dumps(
        {"cases": index, "relations": RELATIONS,
         "limits": ["defects a human caught, not defects that shipped unnoticed",
                    "one author, one project",
                    "several commits fix more than one thing (see also_fixed)",
                    "a negative for one relation can be a positive for another"]},
        indent=1) + "\n")
    print(f"{len(index)} cases ({n_clean} clean), {n_scripts} scripts, "
          f"{len(rels)} defect relations -> {OUT}")
    for c in index:
        print(f"  {c['id']:<28} {str(c['relation'] or 'clean'):<20} "
              f"{c['commit'] or '':<9} {','.join(c['versions'])}")

if __name__ == "__main__":
    main()
