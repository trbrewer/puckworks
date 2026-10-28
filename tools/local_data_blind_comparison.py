#!/usr/bin/env python3
"""Reproduce SCI-LOCAL-DATA-BLIND-COMPARISON-001's bounded, unscored stop.

Uses the existing private manifest, never traverses the collection. Mixed chemistry
CSVs expose headers, clocks and missingness only; target strings are never converted
to numbers or returned. No solver, fitting, scoring or inventory refresh is invoked.
Source attribution: Waszkiewicz et al., Zenodo 10.5281/zenodo.18046315, CC-BY-4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "docs/analysis/sci_local_data_blind_comparison_001"
BASE = "f38ad4285a5daae54b9325ca52d3b0e7d04d05ac"
MANIFEST_ID = "f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766"
FAMILIES = ("waszkiewicz2025", "angeloni2023", "vacaguerra2023a")
FILES = {
    "W-TDS-RAW": "tds_fractions_replicates.csv",
    "W-TDS-MEAN": "tds_fractions.csv",
    "W-INPUT-CONSTANTS": "constants.csv",
    "W-INPUT-PSD": "mastersizer_psd.csv",
}
EVIDENCE = (
    "docs/analysis/sci_h1_pannusch_fair_tds_001/HOLDOUT_MAP.csv",
    "docs/analysis/sci_h1_pannusch_fair_tds_001/SOURCE.json",
    "docs/analysis/sci_h1_pannusch_fair_tds_001/CONFIG.json",
    "docs/analysis/sci_h1_pannusch_fair_tds_001/PARAMETERS.json",
    "docs/analysis/sci_h1_pannusch_fair_tds_001/SCORES.csv",
    "docs/analysis/sci_h1_pannusch_fair_tds_001/NUMERICS.json",
    "puckworks/analysis/pannusch_fair_tds.py",
    "puckworks/analysis/pannusch_equilibrium_limit.py",
    "puckworks/validation/slow/external_waszkiewicz.py",
    "docs/figures/paper_a/results.json",
    "puckworks/data/waszkiewicz2025/PROVENANCE.md",
    "puckworks/data/LOCAL_CORPUS_SNAPSHOT.json",
    "puckworks/data/AVAILABLE_DATA_REGISTER.json",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def structure(data, raw):
    """Discard chemistry except its presence/absence; do not infer shot identity."""
    reader = csv.reader(io.StringIO(data.decode("utf-8-sig")))
    header = next(reader)
    expected = (["time_s", "tds_percent_1", "tds_percent_2", "tds_percent_3"] if raw
                else ["time__s", "tds__percent", "tds_std__percent"])
    if header != expected:
        raise ValueError("Unexpected chemistry schema; do not guess a mapping")
    times, present = [], [0] * (len(header) - 1)
    for row in reader:
        if len(row) != len(header):
            raise ValueError("Ragged chemistry record")
        times.append(float(row[0]))
        for i, value in enumerate(row[1:]):
            present[i] += bool(value.strip())
    if times != [2.5 + 5 * i for i in range(12)]:
        raise ValueError("Changed non-target clock")
    return {"fields": header, "time_rows": len(times), "time_centres_s": times,
            "nonempty_target_cells_by_column": present,
            "physical_shots": "UNKNOWN", "shot_campaign_or_mass_fields": []}


def inspect_sources():
    config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    cfg = json.loads((config / "puckworks/data_sources.json").read_text())
    manifest = json.loads(Path(cfg["inventory"]["manifest"]).read_text())
    if manifest["content_identity"] != MANIFEST_ID:
        raise ValueError("Private manifest identity changed; qualification is not transferable")
    roots = dict(manifest["roots"])
    roots["collection"] = os.environ.get("PUCKWORKS_EXTERNAL_DATA_ROOT") or cfg["inventory"]["root"]
    entries = [r for r in manifest["entries"] if r.get("family_id") in FAMILIES
               and r["file_type"] == "file"]
    public, private = {}, {}
    for source_id, name in FILES.items():
        relative = "puckworks/data/waszkiewicz2025/" + name
        candidates = [r for r in entries if r.get("family_id") == "waszkiewicz2025"
                      and relative in r.get("repository_matches", [])]
        if len(candidates) != 1:
            raise ValueError("Source identity is missing or ambiguous")
        row = candidates[0]
        path = Path(roots[row["root_alias"]]) / row["relative_path"]
        data = path.read_bytes()
        sha = digest(data)
        if sha != row["sha256"] or sha != digest((ROOT / relative).read_bytes()):
            raise ValueError("Original/accepted-copy identity mismatch")
        private[source_id] = {"locator": str(path), "sha256": sha}
        if source_id.startswith("W-TDS"):
            facts = structure(data, source_id == "W-TDS-RAW")
        elif source_id == "W-INPUT-CONSTANTS":
            records = list(csv.DictReader(io.StringIO(data.decode())))
            if {r["parameter"] for r in records} != {
                "r_basket__m", "mu__Pas", "h_zero__m", "dose__g"}:
                raise ValueError("Changed constants schema")
            facts = {"fields": ["parameter", "value", "comment"],
                     "parameters": records, "shot_specific": False}
        else:
            records = list(csv.reader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))
            facts = {"rows": len(records), "column_counts": [len(r) for r in records],
                     "kind": "size bins and three PSD series; not chemistry shots"}
        public[source_id] = {"accepted_copy": relative, "sha256": sha, "inspection": facts}
    # These are routing checks only: no additional Angeloni/Vaca measurement identity
    # is inferred from a family directory, file count, hash or missing search hit.
    private["metadata_only_entries"] = [r for r in entries if r["family_id"] != "waszkiewicz2025"]
    return public, private


def reproduce(output, private_output):
    if private_output.resolve().is_relative_to(ROOT):
        raise ValueError("Private evidence must remain outside the repository")
    inspected, private = inspect_sources()
    historical = json.loads((ROOT / "docs/figures/paper_a/results.json").read_text())
    if not historical.get("external_waszkiewicz", {}).get("per_case"):
        raise ValueError("Historical execution evidence unavailable")
    evidence = {f: digest((ROOT / f).read_bytes()) for f in EVIDENCE}
    result = json.loads((BUNDLE / "COMPARISON.json").read_text())
    if result["identities"]["puckworks_start"] != BASE:
        raise ValueError("Starting revision mismatch")
    if inspected != result["original_inspection"] or evidence != result["evidence_sha256"]:
        raise ValueError("Inspection or evidence differs from the reviewed result")
    if result["runner_sha256"] != digest(Path(__file__).read_bytes()):
        raise ValueError("Runner differs from the reviewed identity")
    if result["status"] != "BLOCKED" or result["blind_score_occurred"] is not False:
        raise ValueError("This runner cannot execute or reproduce a scored comparison")
    private_output.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_path = private_output / "inspection_receipt.json"
    private_path.write_text(json.dumps(private, indent=2, sort_keys=True) + "\n")
    private_path.chmod(0o600)
    output.mkdir(parents=True, exist_ok=True)
    (output / "COMPARISON.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    columns = ["arm", "status", "selected_training_shots", "selected_test_shots",
               "rmse_tds_pp", "mae_tds_pp", "signed_bias_tds_pp", "ci95", "model_evaluations"]
    with (output / "COMPARISON.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for arm in ("F", "E", "B", "N"):
            writer.writerow(dict(arm=arm, status="BLOCKED_NOT_SCORED",
                                 selected_training_shots=0, selected_test_shots=0,
                                 ci95="NOT_ESTIMABLE", model_evaluations=0))
    print("BLOCKED; no model comparison scored; original structure and exposure evidence verified")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--private-output", type=Path,
                        default=Path.home() / ".local/share/puckworks/sci-local-data-blind-comparison-001")
    args = parser.parse_args()
    try:
        reproduce(args.output, args.private_output)
    except (OSError, ValueError, KeyError, StopIteration) as error:
        # File exceptions may contain private locators. Keep public failure output bounded.
        print(f"BLOCKED: reproduction failed ({type(error).__name__}); no targets exposed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
