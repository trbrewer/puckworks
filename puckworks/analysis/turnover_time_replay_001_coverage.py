"""Read-only Visualizer scored-window census with whole-partition disclosure.

No predictor, optimizer or target-flow score is evaluated. Authenticated pickle
objects are decoded into passive containers so this checkout does not need to
import the unmerged empirical fitting implementation. Private linkage never
enters public rows, including when a partition is withheld.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import pickle
import time

import numpy as np

from . import wasz_turnover_time_001 as O

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/TURNOVER_TIME_REPLAY_001"
BINS = ("P<9", "9<=P<=10", "10<P<=11", "11<P<=12", "12<P<=13", "P>13")


class SnapshotWindow:
    """Passive saved fields; identical stored mean-pressure dot product."""
    @property
    def mean_pressure_bar(self):
        return float(self.pressure_bar @ self.quadrature_weight)


class SnapshotShot:
    """Passive saved fields, including private identity, user, role and flags."""


class SnapshotUnpickler(pickle.Unpickler):
    """Decode only after file-hash authentication; preserve all stored fields."""
    def find_class(self, module, name):
        if module == "puckworks.empirical.visualizer" and name in ("Window", "Shot"):
            return {"Window": SnapshotWindow, "Shot": SnapshotShot}[name]
        return super().find_class(module, name)


def pressure_bin(p):
    """Exact disjoint closed/open boundaries; no rounding before assignment."""
    if not np.isfinite(p):
        raise ValueError("Authenticated scored pressure is nonfinite")
    if p < 9:
        return 0
    for i, upper in enumerate((10., 11., 12., 13.), 1):
        if p <= upper:
            return i
    return 5


def cell_safe(ids, shots, universe=None):
    """Inherited 20-shot/10-user rule, including a nonempty complement."""
    ids = set(ids)
    if not ids:
        return True
    if len(ids) < 20 or len({shots[i].user for i in ids}) < 10:
        return False
    if universe is not None:
        remaining = set(universe) - ids
        if remaining and (len(remaining) < 20 or len({shots[i].user for i in remaining}) < 10):
            return False
    return True


def partition_safe(groups, shots, universe):
    """Whole partition, complements and inherited neighboring-set linkage checks."""
    if not all(cell_safe(ids, shots, universe) for ids in groups):
        return False
    prior = set(universe)
    prior_users = {shots[i].user for i in prior}
    for ids in groups:
        if not ids:
            continue  # Empty cells have no private time summaries.
        users = {shots[i].user for i in ids}
        if not cell_safe(ids - prior, shots) or not cell_safe(prior - ids, shots):
            return False
        if any(0 < len(change) < 10 for change in (users - prior_users, prior_users - users)):
            return False
        prior, prior_users = ids, users
    return True


def census(shots):
    """Return releasable rows plus a PRIVATE audit; never return raw identifiers."""
    groups = [set() for _ in BINS]
    midpoints = [[] for _ in BINS]
    scored_shots = set()
    total_retained = 0
    for i, shot in enumerate(shots):
        total_retained += len(shot.windows)
        for window in shot.windows:
            if window.role != "score":
                continue
            index = pressure_bin(window.mean_pressure_bar)
            groups[index].add(i)
            scored_shots.add(i)
            midpoints[index].append((window.start_s + window.end_s) / 2.)
    total = sum(map(len, midpoints))
    if not total or scored_shots != set(range(len(shots))):
        raise ValueError("Authenticated cohort lost score support")
    safe = partition_safe(groups, shots, scored_shots)
    raw = []
    for name, ids, times in zip(BINS, groups, midpoints):
        quartiles = np.quantile(times, [.25, .5, .75]) if times else [None]*3
        raw.append(dict(pressure_bin=name, scored_windows=len(times),
                        percent_all_scored=100*len(times)/total, distinct_shots=len(ids),
                        distinct_users=len({shots[i].user for i in ids}),
                        midpoint_q25_s=quartiles[0], midpoint_median_s=quartiles[1], midpoint_q75_s=quartiles[2]))
    public = []
    total_safe = cell_safe(scored_shots, shots)
    public.append(dict(pressure_bin="ALL_SCORED", release="released" if total_safe else "withheld",
                       scored_windows=total if total_safe else None,
                       percent_all_scored=100. if total_safe else None,
                       distinct_shots=len(scored_shots) if total_safe else None,
                       distinct_users=len({shots[i].user for i in scored_shots}) if total_safe else None))
    for row in raw:
        if safe:
            public.append(dict(row, release="released"))
        else:
            public.append({k: v if k == "pressure_bin" else None for k, v in row.items()} |
                          {"release": "whole_partition_withheld"})
    audit = dict(partition_releasable=safe, all_score_releasable=total_safe,
                 retained_windows=total_retained, scored_windows=total, bins=raw,
                 cell_and_complement_checks=[cell_safe(ids, shots, scored_shots) for ids in groups])
    return public, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vis", type=Path, required=True)
    parser.add_argument("--vis-private", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    for target in (args.output.resolve(), args.private.resolve()):
        for protected in (args.vis.resolve(), args.vis_private.resolve()):
            if target == protected or protected in target.parents:
                raise ValueError("Output overlaps historical inputs")
    if ROOT == args.private.resolve() or ROOT in args.private.resolve().parents:
        raise ValueError("Private census must stay outside Git")
    cpu, wall = time.process_time(), time.perf_counter()
    if np.__version__ != "2.0.2":
        raise ValueError("Use the retained Visualizer NumPy 2.0.2 runtime")
    frozen = json.loads((OUT / "INPUT_MANIFEST.json").read_text())
    manifest_path = args.vis / "docs/research/VIS_PREDICTOR_002/FROZEN_MANIFEST.json"
    if O.digest(manifest_path) != frozen["vis_freeze_sha256"]:
        raise ValueError("Not the pinned 002 freeze")
    manifest = json.loads(manifest_path.read_text())
    for name, key in (("windows.pkl", "windows_sha256"), ("corpus-folds.json", "corpus_fold_sha256")):
        if O.digest(args.vis_private / name) != manifest[key]:
            raise ValueError("Retained cohort bytes changed")
    with (args.vis_private / "windows.pkl").open("rb") as f:
        shots = SnapshotUnpickler(f).load()
    if len(shots) != 10231 or len({s.user for s in shots}) != 315 or any(s.flags["reset_like"] is not False for s in shots):
        raise ValueError("Wrong retained cohort; no filtering is performed")
    public, audit = census(shots)
    if audit["retained_windows"] != manifest["windows"]:
        raise ValueError("Retained window count changed")
    args.private.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.private / "visualizer-coverage-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    O.write_csv(args.output / "VIS_HIGH_PRESSURE_COVERAGE.csv", public)
    receipt = dict(input_windows_sha256=manifest["windows_sha256"], code_sha256=O.digest(__file__),
                   plan_sha256=O.digest(OUT / "PLAN.md"), input_manifest_sha256=O.digest(OUT / "INPUT_MANIFEST.json"),
                   output_sha256=O.digest(args.output / "VIS_HIGH_PRESSURE_COVERAGE.csv"),
                   private_audit_sha256=O.digest(args.private / "visualizer-coverage-audit.json"),
                   partition_release="released" if audit["partition_releasable"] else "whole_partition_withheld",
                   numpy=np.__version__, cpu_seconds=time.process_time() - cpu,
                   wall_seconds=time.perf_counter() - wall)
    receipt["core_hours"] = receipt["cpu_seconds"] / 3600
    (args.output / "VIS_CENSUS_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(public_rows=public, core_hours=receipt["core_hours"])), flush=True)


if __name__ == "__main__":
    main()
