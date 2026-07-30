#!/usr/bin/env python3
"""Freeze Paper A's accepted numerical results, so an assurance repair cannot move one.

Round-10. The round-10 review found the stale-number category EMPTY for the second consecutive
round: every headline value agreed across the manuscript, supplement, cover letter, front matter and
captions. Its five findings are about *inference, source-of-truth and validator scope* — none of
them is fixed by changing a number, and P0-1's remediation (Path A) is explicitly a wording change
with **zero** numerical movement.

That combination is exactly when a numerical regression is easiest to ship: the work is scientific
prose and validator internals, the reviewer's attention is on sentences, and nobody re-reads the
third decimal of a bound. So the accepted values are extracted from the committed artefacts ONCE,
at full precision, and pinned:

``--write``   extract from the artefacts and (re)write the invariant file
``--check``   extract again and require exact agreement, field by field

The file is a *record of what was accepted*, not a second source of truth: it is derived from the
artefacts, so `--check` fails if either side moves. Deliberate numerical work (a new producer run, a
Path B analysis) updates it in its own commit with the moved values enumerated in the message —
never as a side effect of a wording or validator change.

CLI::

    python tools/paper_a_numerical_invariants.py --check
    python tools/paper_a_numerical_invariants.py --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

RESOURCE = _REPO / "docs" / "paper1_resource"
ENDPOINT_JSON = RESOURCE / "PAPER_A_ENDPOINT_PROPAGATION.json"
CORPUS_JSON = RESOURCE / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json"
LOSS_JSON = RESOURCE / "PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json"
INVARIANTS = RESOURCE / "PAPER_A_ROUND10_NUMERICAL_INVARIANTS.json"

#: Preserved to the last bit. These are full-precision floats read straight out of the artefacts,
#: not the display-rounded values the paper quotes: rounding first would hide drift smaller than a
#: displayed digit, which is precisely the drift a display-preserving refactor can introduce.
_SCHEMES = ("cond_in_variety", "sample_in_variety_grind", "cond_in_group", "group")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _interval(node: dict) -> dict:
    fp = node["interval"]["full_precision_pp"]
    return {"lower": fp["lower"], "upper": fp["upper"]}


def _relative_reduction_pct(model: float, comparator: float) -> float:
    """The descriptive relative MAPE reduction, from FULL PRECISION pooled values.

    Recomputed here rather than read from a stored field so that the invariant survives the round-10
    renaming of the artefact's undefined ``skill`` column: the quantity is the science, the field
    name is not. Positive values favour the mechanistic model.
    """
    return 100.0 * (float(comparator) - float(model)) / float(comparator)


def _estimand_identity(design: dict) -> dict:
    """The estimand's identity in whichever schema the artefact carries.

    Pre-round-10 artefacts store ``estimand`` as one free-text sentence (the P1-2 defect); from
    schema 4 it is a typed object. Both are reduced to the same three invariant facts so freezing
    the baseline does not have to wait for the schema migration it is meant to protect.
    """
    est = design.get("estimand")
    if isinstance(est, dict):
        return {"id": est["id"], "operation": est["operation"],
                "negative_values_favour": est["negative_values_favour"]}
    return {"id": "pre_schema4_free_text", "operation": "left_minus_right",
            "negative_values_favour": "mechanistic_model"}


def extract() -> dict:
    """Pull every protected value out of the committed artefacts."""
    from puckworks.paper_a import transfer_semantics as TS

    ep, corpus, loss = _load(ENDPOINT_JSON), _load(CORPUS_JSON), _load(LOSS_JSON)

    endpoints = {}
    for row in ep["rows"]:
        key = "%g" % float(row["m_target_g"])
        endpoints[key] = {
            "pooled_model_mape": row["pooled_model_mape"],
            "pooled_const_mape": row["pooled_const_mape"],
            "paired_difference_pp": row["paired_difference_pp"],
            "paired_median_pp": row["paired_median_pp"],
            "n_points": row["n_points"],
            "n_model_worse_than_const": row["n_model_worse_than_const"],
            "relative_mape_reduction_pct": _relative_reduction_pct(
                row["pooled_model_mape"], row["pooled_const_mape"]),
            "schemes": {
                name: {"observed_mean_delta_pp": row["resampling"][name]["observed_mean_delta_pp"],
                       "interval": _interval(row["resampling"][name])}
                for name in _SCHEMES},
        }

    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    design = ep["resampling_design"]

    return {
        "_what": ("Paper A's accepted numerical results, frozen at the round-10 remediation. "
                  "Regenerate with `python tools/paper_a_numerical_invariants.py --write` ONLY as "
                  "part of deliberate numerical work, never to make a failing check pass."),
        "source_sha256": ep["source_sha256"],
        "endpoint_targets": [float(t) for t in ep["endpoint"]["targets"]],
        "estimand": _estimand_identity(design),
        "endpoints": endpoints,
        "endpoint_sensitivity": {
            "point_difference_magnitude_range_pp":
                ep["endpoint_sensitivity"]["point_difference_magnitude_range_pp"],
            "interpretation_code": ep["endpoint_sensitivity"]["interpretation_code"],
        },
        "stability_audit": {
            "target": audit["target"],
            "n_runs": audit["n_runs"],
            "B_per_seed": audit["B_per_seed"],
            "canonical_B": audit["canonical_B"],
            "lower_monte_carlo_se_at_canonical_B_pp":
                audit["lower_monte_carlo_se_at_canonical_B_pp"],
            "upper_monte_carlo_se_at_canonical_B_pp":
                audit["upper_monte_carlo_se_at_canonical_B_pp"],
            "upper_bound_sign_is_stable": audit["upper_bound_sign_is_stable"],
        },
        "corpus": {
            "n_held_out_records": ep["corpus"]["n_held_out_records"],
            "n_observations": ep["corpus"]["n_observations"],
            "n_lookup_observations": ep["corpus"]["n_lookup_observations"],
            "manifest_sha256": ep["corpus"]["manifest_sha256"],
            "included_sample_ids_sha256": ep["corpus"]["included_sample_ids_sha256"],
        },
        "design_census": {
            name: {"n_clusters": design["schemes"][name]["n_clusters"],
                   "n_strata": design["schemes"][name]["n_strata"],
                   "cluster_size_distribution":
                       design["schemes"][name]["cluster_size_distribution"],
                   "membership_sha256": design["schemes"][name]["membership_sha256"]}
            for name in _SCHEMES},
        "comparator_loss": {
            ("alternative" if row["alt_loss"] else "primary"): {
                "pooled_model_mape": row["pooled_model_mape"],
                "pooled_const_mape": row["pooled_const_mape"],
                "paired_difference_pp": row["paired_difference_pp"],
                "n_model_worse_than_const": row["n_model_worse_than_const"],
                "n_points": row["n_points"],
                "interval": _interval(row),
            } for row in loss["rows"]},
        "corpus_contract": {
            arm: {"pooled_model_mape": corpus[arm]["pooled_model_mape"],
                  "pooled_const_mape": corpus[arm]["pooled_const_mape"],
                  "pooled_lookup_mape": corpus[arm]["pooled_lookup_mape"],
                  "paired_difference_pp": corpus[arm]["paired_difference_pp"],
                  "n_points": corpus[arm]["n_points"],
                  "n_model_worse_than_const": corpus[arm]["n_model_worse_than_const"],
                  "n_observations": corpus[arm]["corpus"]["n_observations"]}
            for arm in ("complete_corpus", "matched_on_grid")},
    }


def _diff(expected, found, path: str = "") -> list[str]:
    """Exact structural comparison. No tolerance: a wording remediation moves nothing."""
    if isinstance(expected, dict) and isinstance(found, dict):
        out = []
        for key in sorted(set(expected) | set(found)):
            if key.startswith("_"):
                continue
            if key not in expected:
                out.append("%s.%s: not in the frozen invariants (found %r)" % (path, key, found[key]))
            elif key not in found:
                out.append("%s.%s: frozen invariant %r is no longer produced"
                           % (path, key, expected[key]))
            else:
                out += _diff(expected[key], found[key], "%s.%s" % (path, key))
        return out
    if isinstance(expected, list) and isinstance(found, list):
        if len(expected) != len(found):
            return ["%s: length %d, frozen invariant has %d" % (path, len(found), len(expected))]
        out = []
        for i, (e, f) in enumerate(zip(expected, found)):
            out += _diff(e, f, "%s[%d]" % (path, i))
        return out
    if isinstance(expected, float) or isinstance(found, float):
        # `==` on floats is deliberate: both sides are read from JSON with the same repr, so a
        # deterministic pipeline reproduces them bit for bit. A tolerance here would silently admit
        # exactly the small drift this file exists to catch.
        if float(expected) != float(found):
            return ["%s: %r, frozen invariant is %r (difference %.3g)"
                    % (path, found, expected, float(found) - float(expected))]
        return []
    if expected != found:
        return ["%s: %r, frozen invariant is %r" % (path, found, expected)]
    return []


def check() -> list[str]:
    if not INVARIANTS.exists():
        return ["no frozen numerical invariants at %s; write them with --write"
                % INVARIANTS.relative_to(_REPO)]
    problems = _diff(_load(INVARIANTS), extract(), "invariants")
    if problems:
        problems.append(
            "A protected Paper A value moved. If this is deliberate numerical work, enumerate the "
            "moved values in the commit message and rerun with --write; if it is not, the "
            "remediation has changed a result it was only supposed to describe.")
    return problems


def write() -> None:
    INVARIANTS.write_text(json.dumps(extract(), indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    print("wrote %s" % INVARIANTS.relative_to(_REPO))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    if args.write:
        write()
        return 0
    problems = check()
    if problems:
        print("Paper A numerical invariants FAILED:", file=sys.stderr)
        for p in problems:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("Paper A numerical invariants OK (every protected value unchanged).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
