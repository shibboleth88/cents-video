#!/usr/bin/env python3
"""Run each reviewer against every corpus script and store the raw verdicts.

Blinding is structural, not requested. The script text is passed inline in the
prompt and every tool is disallowed, so a reviewer cannot reach the repository
and read the commit message that names the defect. Asking it not to look would
have left recall inflated by exactly the amount I could not measure.

The reviewer prompts deliberately do NOT reuse the examples from
.claude/skills/video-concept-relations/SKILL.md, because those examples ARE
these corpus cases. Each reviewer gets the relation stated abstractly with an
invented example in another domain.
"""
import argparse, concurrent.futures as cf, json, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
H = ROOT / "harness"
CORPUS = H / "corpus"
RV = H / "reviewers"
NO_TOOLS = ("Bash,Read,Write,Edit,Grep,Glob,WebFetch,WebSearch,Task,Agent,"
            "NotebookEdit,TodoWrite,Skill,SlashCommand")

def numbered(text):
    return "\n".join(f"{i:>3}  {l}" for i, l in enumerate(text.strip().splitlines(), 1))

def build_prompt(relation, script_text):
    body = (RV / f"{relation}.md").read_text()
    contract = (RV / "_contract.md").read_text()
    return (f"{contract}\n\n---\n\n{body}\n\n---\n\n"
            f"## The draft to review\n\n```\n{numbered(script_text)}\n```\n\n"
            "Reply with the JSON object only.")

def parse_verdict(out):
    """Return (dict, None) or (None, reason). Unparseable is its own outcome -
    it is not a NONE, and counting it as one would quietly credit a broken
    reviewer with a correct silence."""
    s = out.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.S).strip()
    i = s.find("{")
    if i < 0:
        return None, "no JSON object in output"
    depth = 0
    for j, ch in enumerate(s[i:], i):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    d = json.loads(s[i:j + 1])
                except Exception as e:
                    return None, f"JSON parse failed: {e}"
                if d.get("verdict") not in ("FOUND", "NONE"):
                    return None, f"verdict not FOUND/NONE: {d.get('verdict')!r}"
                if not isinstance(d.get("instances"), list):
                    return None, "instances is not a list"
                if d["verdict"] == "NONE" and d["instances"]:
                    return None, "verdict NONE with non-empty instances"
                if d["verdict"] == "FOUND" and not d["instances"]:
                    return None, "verdict FOUND with no instances"
                return d, None
    return None, "unbalanced JSON object"

def one(job):
    relation, case_id, version, script_text, outdir, model = job
    prompt = build_prompt(relation, script_text)
    cmd = ["claude", "-p", prompt, "--disallowed-tools", NO_TOOLS, "--max-turns", "1"]
    if model: cmd += ["--model", model]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    dur = round(time.time() - t0, 1)
    verdict, err = (None, f"CLI exited {r.returncode}: {r.stderr.strip()[:200]}") \
        if r.returncode != 0 else parse_verdict(r.stdout)
    rec = {"relation": relation, "case": case_id, "version": version,
           "seconds": dur, "exit": r.returncode, "verdict": verdict,
           "malformed": err, "raw": r.stdout.strip()[:4000]}
    (outdir / f"{relation}__{case_id}__{version}.json").write_text(json.dumps(rec, indent=1) + "\n")
    tag = err if err else verdict["verdict"]
    print(f"  {relation:<19} {case_id:<32} {version:<7} {dur:>5}s  {tag}", flush=True)
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parallel", type=int, default=6)
    ap.add_argument("--model", default=None)
    ap.add_argument("--tag", default=time.strftime("%Y%m%d-%H%M%S"))
    a = ap.parse_args()

    idx = json.loads((CORPUS / "index.json").read_text())
    relations = sorted(p.stem for p in RV.glob("*.md") if not p.stem.startswith("_"))
    cases = idx["cases"]
    assert relations, "no reviewer prompts found in harness/reviewers/"
    assert cases, "corpus index lists no cases"

    outdir = H / "runs" / a.tag
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(rel, c["id"], v, (CORPUS / c["id"] / f"{v}.txt").read_text(), outdir, a.model)
            for rel in relations for c in cases for v in ("before", "after")]
    expected = len(relations) * len(cases) * 2
    assert len(jobs) == expected, f"built {len(jobs)} jobs, expected {expected}"
    print(f"{len(jobs)} reviews: {len(relations)} reviewers x {len(cases)} cases x 2 versions"
          f"  (parallel={a.parallel})\n")

    with cf.ThreadPoolExecutor(max_workers=a.parallel) as ex:
        recs = list(ex.map(one, jobs))

    # Floors. A run that produced nothing parseable must not look like a run of
    # unanimous silence, and a run that crashed every call must not look empty.
    bad = [r for r in recs if r["malformed"]]
    assert len(recs) == len(jobs), f"{len(recs)} records for {len(jobs)} jobs"
    print(f"\n{len(recs)-len(bad)}/{len(recs)} parseable; {len(bad)} malformed")
    if len(bad) == len(recs):
        sys.exit("FATAL: every review was malformed - the reviewers produced no data at all")
    (outdir / "manifest.json").write_text(json.dumps(
        {"tag": a.tag, "relations": relations, "cases": [c["id"] for c in cases],
         "runs": len(recs), "malformed": len(bad),
         "model": a.model or "default", "disallowed_tools": NO_TOOLS}, indent=1) + "\n")
    print(f"-> {outdir}")
    return 1 if len(bad) > len(recs) // 4 else 0

if __name__ == "__main__":
    sys.exit(main())
