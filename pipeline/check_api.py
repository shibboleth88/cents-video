#!/usr/bin/env python3
"""Confirm the fal connection works, without ever handling the key itself.

Reads FAL_KEY from the environment, reports only whether it is present and
whether a call succeeds. The value is never printed, logged or written anywhere,
and nothing in this repo stores it.
"""
from __future__ import annotations
import os, sys

def main() -> int:
    key = os.environ.get("FAL_KEY")
    if not key:
        print("  \033[31mFAIL\033[0m FAL_KEY is not set in this shell.")
        print("         Add it to your shell profile (see README), open a new terminal,")
        print("         and run this again.")
        return 1
    # Shape only — enough to catch a truncated paste, revealing nothing.
    print(f"  \033[32mOK\033[0m   FAL_KEY present ({len(key)} characters)")
    try:
        import fal_client
    except ImportError:
        print("  \033[31mFAIL\033[0m fal-client is not installed:  pip3 install fal-client")
        return 1
    print("  \033[32mOK\033[0m   fal-client importable")
    try:
        # Cheapest possible real call: upload a few bytes and confirm the
        # credential is accepted. No model runs, so nothing is billed for
        # generation.
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "ping.txt"
            p.write_text("ping")
            url = fal_client.upload_file(str(p))
        print(f"  \033[32mOK\033[0m   credential accepted (upload returned a URL)")
    except Exception as e:
        msg = str(e)
        # Never echo a key back even if the library put it in the message.
        if key in msg: msg = msg.replace(key, "<redacted>")
        print(f"  \033[31mFAIL\033[0m call rejected: {msg[:200]}")
        return 1
    print("\n  Ready. Next:  python3 pipeline/generate.py plan")
    return 0

if __name__ == "__main__":
    sys.exit(main())
