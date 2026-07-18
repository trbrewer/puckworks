#!/usr/bin/env python3
"""Assert an executed notebook reached its completion marker and had no cell error.

Usage: check_notebook_marker.py <path> [MARKER]
MARKER defaults to QUICKSTART_COMPLETE (CPU quickstart); the guided pull uses GUIDED_PULL_COMPLETE.
"""
import json
import sys


def main(path: str, marker: str = "QUICKSTART_COMPLETE") -> int:
    nb = json.load(open(path, encoding="utf-8"))
    text = []
    for c in nb["cells"]:
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                raise SystemExit(f"cell errored: {o.get('ename')}: {o.get('evalue')}")
            t = o.get("text")
            if isinstance(t, list):
                text += t
            elif t:
                text.append(t)
            plain = o.get("data", {}).get("text/plain")
            if isinstance(plain, list):
                text += plain
    blob = "".join(t for t in text if t)
    if marker not in blob:
        raise SystemExit(f"notebook did not reach its completion marker ({marker})")
    print(f"{marker} marker present; no cell errors")
    return 0


if __name__ == "__main__":
    _marker = sys.argv[2] if len(sys.argv) > 2 else "QUICKSTART_COMPLETE"
    raise SystemExit(main(sys.argv[1], _marker))
