#!/usr/bin/env python3
"""Export the non-scoring source audit; keep the long-form view outside Git."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from puckworks.analysis.maille_transfer import analysis_view, audit  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="private output directory outside the repository and source collection")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("long-form source exports must remain outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    rows, receipt = analysis_view()
    result = audit()
    for name, values in (("analysis_view.csv", rows),
                         ("reference_summaries.csv", receipt["reference_summaries"])):
        with (output / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows(values)
    (output / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    names = ("analysis_view.csv", "reference_summaries.csv", "RESULT.json")
    manifest = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in names}
    (output / "artifact_hashes.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["scientific_verdict"], "observed_cells": len(rows),
                      "executed_folds": 0, "artifact_hashes": manifest}, indent=2))


if __name__ == "__main__":
    main()
