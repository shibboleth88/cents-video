#!/usr/bin/env python3
"""Confirm the fal connection works, without ever handling the key itself.

Reads FAL_KEY from the environment, reports only whether it is present and
whether a call succeeds. The value is never printed, logged or written anywhere,
and nothing in this repo stores it.
"""
from __future__ import annotations
import os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from falenv import load_key, redact

def main() -> int:
    key, where = load_key()
    if not key:
        print("  \033[31mFAIL\033[0m FAL_KEY not found in the environment or any shell profile.")
        print("         Add  export FAL_KEY=\"...\"  to ~/.bash_profile and run this again.")
        return 1
    # Shape only — enough to catch a truncated paste, revealing nothing.
    print(f"  \033[32mOK\033[0m   FAL_KEY found via {where} ({len(key)} characters)")
    try:
        import fal_client  # noqa: F401
    except ImportError:
        print("  \033[31mFAIL\033[0m fal-client is not installed:  pip3 install fal-client")
        return 1
    print("  \033[32mOK\033[0m   fal-client importable")
    # A failure here has several distinct causes and they are NOT interchangeable:
    # no key, a malformed key, a rejected credential, a valid credential on an
    # account with no balance, and a network that is down all produce "it did
    # not work". Each gets its own message and its own remedy, because the
    # remedy differs completely.
    if key.count(":") != 1 or not all(key.split(":")):
        print("  \033[31mFAIL\033[0m key is not in the expected key_id:key_secret shape — "
              "check for a truncated paste")
        return 1
    print("  \033[32mOK\033[0m   key shape looks right (key_id:key_secret)")

    import json, urllib.request, urllib.error
    req = urllib.request.Request(
        "https://rest.fal.ai/storage/auth/token?storage_type=fal-cdn-v3",
        data=b"{}", method="POST",
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30):
            print("  \033[32mOK\033[0m   credential accepted and account is in good standing")
    except urllib.error.HTTPError as e:
        body = redact(e.read(800).decode("utf-8", "replace"), key)
        try: detail = json.loads(body).get("detail", body)
        except Exception: detail = body
        if e.code in (401, 400):
            print(f"  \033[31mFAIL\033[0m credential rejected ({e.code}): {detail[:160]}")
            print("         The key is wrong or has been deleted. Make a new one at")
            print("         fal.ai/dashboard/keys with the API scope.")
        elif e.code == 403 and "balance" in str(detail).lower():
            print(f"  \033[33mKEY OK, ACCOUNT LOCKED\033[0m  {detail[:160]}")
            print("         The credential is valid and correctly installed. The account")
            print("         simply has no credits. Top up at fal.ai/dashboard/billing;")
            print("         nothing here needs changing afterwards.")
        else:
            print(f"  \033[31mFAIL\033[0m refused ({e.code}): {detail[:200]}")
        return 1
    except Exception as e:
        print(f"  \033[31mFAIL\033[0m could not reach fal: {redact(str(e), key)[:160]}")
        print("         This is a network problem, not a credential problem.")
        return 1

    print("\n  Ready. Next:  python3 pipeline/generate.py plan")
    return 0

if __name__ == "__main__":
    sys.exit(main())
