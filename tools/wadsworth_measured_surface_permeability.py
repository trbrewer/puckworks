#!/usr/bin/env python3
"""Execute one frozen four-arm campaign using an authenticated private parent bundle."""
import argparse
from pathlib import Path

from puckworks.analysis.wadsworth_measured_surface_permeability import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1], args.parent_bundle, args.output)
    print(result["status"])
    return 0 if result["status"] == "COMPLETED_PRIVATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
