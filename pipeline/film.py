#!/usr/bin/env python3
"""Which film is checked out.

Per-film state lives in films/<slug>/ and the working directories at the repo
root are SYMLINKS into the active one. Symlinks rather than copies on purpose:
a copy is how you end up with two versions of a file and only one of them
current, which is the failure this project keeps meeting. There is exactly one
of every file; switching repoints, it never duplicates.

Shared across films and never per-film: shared/assets.json (the inventory),
shared/generation_log.json (API spend), inputs/ (raw material), public/assets/
(staged imagery), pipeline/, src/.

  python3 pipeline/film.py status
  python3 pipeline/film.py switch introduction
  python3 pipeline/film.py new <slug>
"""
from __future__ import annotations
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILMS = ROOT / "films"
LINKS = ["script", "timeline", "captions", "exports", "review"]
AUDIO = ROOT / "public" / "vo.wav"


def films() -> list[str]:
    return sorted(p.name for p in FILMS.iterdir() if p.is_dir()) if FILMS.is_dir() else []


def active() -> str | None:
    """The slug every root symlink points into — or None if they disagree.

    A MIXED state is the dangerous one: script from one film and timeline from
    another renders a coherent-looking film of a script that was never written.
    So this reports None rather than guessing, and `status` fails on it.
    """
    seen = set()
    for name in LINKS:
        p = ROOT / name
        if not p.is_symlink(): return None
        try: rel = p.resolve().relative_to(FILMS)
        except Exception: return None
        seen.add(rel.parts[0])
    if AUDIO.is_symlink():
        try: seen.add(AUDIO.resolve().relative_to(FILMS).parts[0])
        except Exception: return None
    return seen.pop() if len(seen) == 1 else None


def point(slug: str) -> None:
    base = FILMS / slug
    missing = [d for d in LINKS if not (base / d).is_dir()]
    if missing: sys.exit(f"films/{slug} is missing: {', '.join(missing)}")
    for name in LINKS:
        link = ROOT / name
        if link.exists() and not link.is_symlink():
            sys.exit(f"{name}/ is a real directory, not a symlink — refusing to replace it")
        if link.is_symlink(): link.unlink()
        link.symlink_to(pathlib.Path("films") / slug / name)
    (base / "audio").mkdir(exist_ok=True)
    stage_audio(slug)


def master_audio(slug: str) -> pathlib.Path:
    return FILMS / slug / "audio" / "vo.wav"


def stage_audio(slug: str) -> None:
    """Copy the active film's voiceover into public/.

    Not a symlink: Remotion serves public/ over HTTP and will not follow a link
    out of it — the render 404s. public/ is a serving directory that other
    staging already populates (assets.py stage), so the voiceover is staged the
    same way. The master stays in films/<slug>/audio/ and `status` compares
    hashes, so the copy cannot go stale unnoticed.
    """
    import shutil
    src = master_audio(slug)
    if AUDIO.is_symlink(): AUDIO.unlink()
    if src.exists():
        shutil.copy2(src, AUDIO)
    elif AUDIO.exists():
        AUDIO.unlink()


def _sha(p: pathlib.Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:16]


def status() -> int:
    a = active()
    print(f"films: {', '.join(films()) or '(none)'}")
    if a is None:
        print("ACTIVE: INCONSISTENT — the root symlinks do not all point at one film.")
        for name in LINKS + ["public/vo.wav"]:
            p = ROOT / name
            tgt = p.readlink() if p.is_symlink() else "(not a symlink)"
            print(f"  {name:16} -> {tgt}")
        return 1
    print(f"ACTIVE: {a}")
    src = master_audio(a)
    if not src.exists():
        print("  voiceover: not recorded yet")
        if AUDIO.exists():
            print("  public/vo.wav EXISTS but this film has no master — stale staging from another film.")
            return 1
        return 0
    if not AUDIO.exists():
        print("  voiceover: master present, public/vo.wav MISSING — run switch again to stage it.")
        return 1
    a_sha, b_sha = _sha(src), _sha(AUDIO)
    print(f"  voiceover: {src.relative_to(ROOT)}  staged={a_sha == b_sha}")
    if a_sha != b_sha:
        print(f"  public/vo.wav DIFFERS from the master ({b_sha} vs {a_sha}) — restage before rendering.")
        return 1
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status": return status()
    if cmd == "switch":
        if len(sys.argv) < 3: sys.exit("switch needs a slug")
        point(sys.argv[2])
        if active() != sys.argv[2]: sys.exit("switch did not take — symlinks are inconsistent")
        return status()
    if cmd == "new":
        if len(sys.argv) < 3: sys.exit("new needs a slug")
        slug = sys.argv[2]
        base = FILMS / slug
        if base.exists(): sys.exit(f"films/{slug} already exists")
        for d in LINKS + ["audio"]: (base / d).mkdir(parents=True)
        for f in ("assets.json", "generation_log.json"):
            (base / "timeline" / f).symlink_to(pathlib.Path("../../../shared") / f)
        print(f"created films/{slug}; switch to it with: python3 pipeline/film.py switch {slug}")
        return 0
    sys.exit(f"unknown command {cmd!r}")


if __name__ == "__main__":
    sys.exit(main())
