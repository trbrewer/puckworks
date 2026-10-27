#!/usr/bin/env python3
"""Run the single frozen campaign into a new directory outside the checkout."""
import argparse
from pathlib import Path

from puckworks.analysis.wadsworth_held_coffee_permeability import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1], args.output)
    print(result["status"])
    return 0 if result["status"] == "COMPLETED_PRIVATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
