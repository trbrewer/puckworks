#!/usr/bin/env python3
"""Run one frozen task-local campaign into a new private directory."""
import argparse
import json
from pathlib import Path

from puckworks.analysis.wadsworth_percolation_kc_transfer import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inspection", type=Path, required=True)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1], args.parent_bundle, args.output,
                 json.loads(args.inspection.read_text()))
    print(result["status"])
    return 0 if result["status"] == "COMPLETED_PRIVATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
