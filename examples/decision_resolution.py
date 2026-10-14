"""SYNTHETIC decision-policy demonstration: python -m examples.decision_resolution.

No real observations, espresso thresholds, source access or scientific scoring.
Only --output writes a file; otherwise the deterministic report goes to stdout.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal as D
import json
from pathlib import Path
from typing import Literal, cast

from puckworks.validation.decision_resolution import (
    Assessment, Basis, Counts, DecisionBasis, Evidence, Interval, Operator, Quality, Requirement,
    Role, Scope, assess,
)

POLICY = "DECISION_RESOLUTION_POLICY/v1-proposed"
QUALITY = Quality(True, True, True, True, "First-party synthetic mathematical fixture; no source payload.")


def scope(n: int = 1, observable: str = "synthetic error") -> Scope:
    return Scope(observable, "kg", "SYNTHETIC bounded scalar fixture", "declared finite-cohort metric",
                 "equal physical-unit mean", "fixed synthetic predictor; no target access",
                 tuple((f"SYNTHETIC-UNIT-{i}", f"SYNTHETIC-UNIT-{i}") for i in range(n)),
                 "all named synthetic units eligible")


def requirement(identity: str, operator: Operator, threshold: str, *, role: Role = "adequacy",
                decision_basis: DecisionBasis = "point", support: Scope | None = None,
                controlling: bool = True) -> Requirement:
    return Requirement(identity, controlling, role, support or scope(), operator, D(threshold),
                       "Illustrative synthetic requirement, never an espresso default",
                       "Synthetic test design only; no intended-use loss established", "proposed",
                       decision_basis, ("synthetic input",), ("SYNTHETIC_VERIFICATION_ONLY",),
                       comparator="SYNTHETIC-CONTROL" if role == "increment" else None)


def bound(r: Requirement, point: str | None, lower: str, upper: str) -> Evidence:
    lo, hi = D(lower), D(upper)
    center, radius = (lo + hi) / 2, (hi - lo) / 2
    basis = Basis("analytic", r.scope,
                  f"Synthetic q={center}+({radius})*x, -1<=x<=1. Multiplying by nonnegative "
                  f"{radius} and adding {center} proves [{lo},{hi}].",
                  ("synthetic input",), ("The defined affine scalar is the assessed quantity.",))
    return Evidence("bound", r.scope, basis, r.scope.members, QUALITY,
                    ("measurement", "training", "population", "cross-source"),
                    D(point) if point is not None else None, Interval(lo, hi))


def sensitivity(r: Requirement, point: str, lower: str, upper: str) -> Evidence:
    basis = Basis("sensitivity", r.scope, "Min/max of three named finite synthetic evaluations.",
                  ("tested numerical changes",), ("Only these finite settings were tested.",),
                  ("SYNTHETIC-setting-a", "SYNTHETIC-setting-b", "SYNTHETIC-setting-c"))
    return Evidence("sensitivity", r.scope, basis, r.scope.members, QUALITY,
                    ("continuum numerical error", "measurement", "training", "population"),
                    D(point), Interval(D(lower), D(upper)))


def point(r: Requirement, value: str) -> Evidence:
    return Evidence("point", r.scope, Basis("descriptive", r.scope, "Reported synthetic scalar.", (), ()),
                    r.scope.members, QUALITY, ("measurement",), D(value))


def synthetic_cases() -> dict[str, Assessment]:
    cases: dict[str, Assessment] = {}

    def add(name: str, *pairs: tuple[Requirement, Evidence]) -> None:
        cases[name] = assess(tuple(r for r, _ in pairs), {r.identity: e for r, e in pairs}, policy_version=POLICY)

    for name, op, value, lo, hi in (
        ("A-upper-satisfies", "<=", "4", "3", "5"),
        ("B-upper-violates", "<=", "7", "6", "8"),
        ("C-upper-overlaps", "<=", "5", "4", "6"),
        ("A-lower-satisfies", ">=", "7", "6", "8"),
        ("B-lower-violates", ">=", "3", "2", "4"),
        ("C-lower-overlaps", ">=", "5", "4", "6"),
    ):
        r = requirement("metric", cast(Operator, op), "5", decision_basis="applicable_bound")
        add(name, (r, bound(r, value, lo, hi)))
    for op in ("<=", "<", ">=", ">"):
        r = requirement("equality", cast(Operator, op), "5", decision_basis="applicable_bound")
        add("D-equality-" + op, (r, bound(r, "5", "5", "5")))
    r = requirement("same-values", ">=", "0.10")
    add("E-bound", (r, bound(r, "2.0", "1.97", "2.03")))
    add("E-sensitivity", (r, sensitivity(r, "2.0", "1.97", "2.03")))
    precision = requirement("precision", "<=", "0.02", role="precision")
    add("F-stable-effect-precision-fails", (r, sensitivity(r, "2.0", "1.97", "2.03")),
        (precision, point(precision, "0.03")))
    add("G-overlap-precision-fails", (r, sensitivity(r, "0.10", "0.07", "0.13")),
        (precision, point(precision, "0.03")))
    adequate = requirement("adequacy", "<=", "5.0", decision_basis="applicable_bound")
    gain = requirement("increment", ">=", "0.50", role="increment", decision_basis="applicable_bound",
                       support=scope(observable="control error minus candidate error"))
    # Lower-is-better gain = 4.25 - 4.0 = 0.25, against the declared control.
    add("H-adequate-insufficient-increment", (adequate, bound(adequate, "4.0", "3.9", "4.1")),
        (gain, bound(gain, str(D("4.25") - D("4.0")), "0.20", "0.30")))
    for name, definite, possible, missing in (("fails", 5, 5, 0), ("unresolved", 5, 7, 2),
                                             ("satisfied-incomplete", 6, 8, 2), ("satisfied", 6, 8, 0)):
        s = scope(8)
        count_rule = Requirement("count", True, "count", s, ">=", 6, "Synthetic six-of-eight rule",
                                 "Explicit illustrative k, not a reliability estimate", "proposed", "finite_count",
                                 ("synthetic input",), ("No population reliability or independence claim.",),
                                 count_meaning="applicable_bound")
        states = cast(list[Literal["definite", "possible", "missing", "failure"]], (
                  ["definite"] * definite + ["possible"] * (possible - definite - missing)
                  + ["missing"] * missing + ["failure"] * (8 - possible)))
        counts = Counts(8, definite, possible, tuple(zip(s.members, states)), "applicable_bound",
                        "Definite: synthetic member bound entirely satisfies its declared requirement; "
                        "failure: entirely violates; possible/missing: not resolved.")
        basis = Basis("analytic", s, "Each definite member has q=0+x/4 in [-.25,.25] <=1; "
                      "each failure has q=2+x/4 in [1.75,2.25] >1; possible q=1+x spans the limit.",
                      ("synthetic input",), ("Each x lies in [-1,1]; missing members unrestricted.",))
        e = Evidence("count", s, basis, tuple(key for key, state in counts.members if state != "missing"),
                     QUALITY, ("population",), counts=counts)
        continuous = (adequate, bound(adequate, "4", "3.9", "4.1"))
        add("I-count-" + name, continuous, (count_rule, e))
        if missing and definite == 6:
            coverage = replace(count_rule, identity="coverage", role="coverage", threshold=8,
                               decision_basis="complete_support", count_meaning=None)
            add("I-separate-complete-support-fails", continuous, (count_rule, e),
                (coverage, replace(e, kind="coverage", counts=None)))
        if definite == possible == 5:
            add("I-adverse-diagnostic-not-a-gate", continuous, (replace(count_rule, controlling=False), e))
    r = requirement("point-contract", "<=", "10")
    add("J-contract-fail-resolution-overlap", (r, bound(r, "11", "9", "12")))
    add("J-point-only-pass", (r, point(r, "9")))
    r = requirement("full-metric", "<=", "5", decision_basis="applicable_bound", support=scope(2))
    e = bound(r, None, "6", "7")
    e = replace(e, observed_support=(r.scope.members[0],), basis=replace(e.basis,
                argument="Synthetic q=(12+x)/2, 0<=x<=2; therefore 6<=q<=7 despite missing x.",
                full_support_justification="Fixed denominator 2; known first value 12 and declared x in [0,2]."))
    add("K-full-scope-failure-incomplete", (r, e))
    subset = scope()
    add("K-incompatible-subset", (r, replace(e, scope=subset, basis=replace(e.basis, scope=subset))))
    r = requirement("large-margin", ">=", "0.1")
    for name, quality in (("source-identity", replace(QUALITY, source_identity=False)),
                          ("payload-integrity", replace(QUALITY, payload_integrity=False))):
        add("L-" + name, (r, replace(sensitivity(r, "20", "19", "21"), quality=quality)))
    return dict(sorted(cases.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write only this requested JSON output (exclusive creation).")
    args = parser.parse_args()
    output = json.dumps({
        "classification": "SYNTHETIC_VERIFICATION_ONLY",
        "SCIENTIFIC_RESULT_DISPOSITION": "No empirical scientific adjudication performed.",
        "VALIDATION_FRAMEWORK_DISPOSITION": "Synthetic comparisons evaluated; acceptance/review is separate.",
        "CLAIM_CEILING": "Declared synthetic relations only; PHYSICAL_VALIDATION=NOT_ESTABLISHED; no adoption.",
        "cases": {name: json.loads(result.to_json()) for name, result in synthetic_cases().items()},
    }, sort_keys=True, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(output)
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
