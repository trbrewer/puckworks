#!/usr/bin/env python3
"""Assert an executed notebook reached QUICKSTART_COMPLETE and had no cell error. Usage: <path>."""
import json
import sys


def main(path: str) -> int:
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
    if "QUICKSTART_COMPLETE" not in blob:
        raise SystemExit("quickstart did not reach its completion marker")
    print("QUICKSTART_COMPLETE marker present; no cell errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
