from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.publishing.validate_evidence import validate_trigger


def scan(directory: Path, repositories: dict[str, Path] | None = None) -> dict[str, object]:
    valid: list[str] = []
    diagnostics: list[dict[str, object]] = []
    for path in sorted(directory.glob("*.yml")):
        result = validate_trigger(path, repositories)
        if result.ok:
            valid.append(str(path))
        else:
            diagnostics.append({"path": str(path), "errors": list(result.errors)})
    return {"eligible": valid, "diagnostics": diagnostics}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("content/triggers"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = scan(args.directory)
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 1 if report["diagnostics"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
