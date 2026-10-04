"""Find FAL_KEY wherever it actually lives.

The environment is the right place for a credential, but "the environment"
differs by how a process was started: a non-login, non-interactive shell never
reads ~/.bash_profile, so a key exported there is invisible to anything launched
that way — which is how this pipeline is usually run. The symptom is a key that
is plainly saved and plainly absent at the same time.

So: environment first, then the one well-formed export line in the usual shell
profiles. The value is never printed, logged or written anywhere.
"""
from __future__ import annotations
import os, pathlib, re

PROFILES = ("~/.bash_profile", "~/.zshrc", "~/.zprofile", "~/.bashrc", "~/.profile")
LINE = re.compile(r'^\s*export\s+FAL_KEY\s*=\s*(["\']?)(.+?)\1\s*$')

def load_key() -> tuple[str | None, str]:
    """Returns (key, where_it_came_from). key is None when nothing is found."""
    k = os.environ.get("FAL_KEY")
    if k: return k, "environment"
    for pth in PROFILES:
        p = pathlib.Path(pth).expanduser()
        if not p.exists(): continue
        try:
            for line in p.read_text(errors="ignore").splitlines():
                m = LINE.match(line)
                if m and m.group(2).strip():
                    key = m.group(2).strip()
                    os.environ["FAL_KEY"] = key   # so fal_client finds it too
                    return key, str(p)
        except OSError:
            continue
    return None, "nowhere"

def redact(text: str, key: str | None) -> str:
    """Never let a key reach a log, even one the library put in an exception."""
    return text.replace(key, "<redacted>") if key else text
