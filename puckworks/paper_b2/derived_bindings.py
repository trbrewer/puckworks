"""Bind Paper B2's DERIVED manuscript numbers to the bundle fields they are computed from.

Paper 1's sweep bound values that were archived but unchecked. B2's remaining unbound results are
a different shape: they are *derived* — ratios, gaps and maxima over bundle fields — and their
`CONFIG_CONSTANTS` explanations already name the arithmetic ("ratio of
`shot_level.paired.comparisons.phi_vs_const.mean_difference_g_per_s` / ..."). Naming the
arithmetic in a docstring is not performing it: nothing recomputed the ratio, so either operand
could move and the printed quotient would stand.

Each binding below RECOMPUTES the quantity from the committed bundle. `verify()` compares and
fails on drift. Recomputation matters more here than for a stored value: a derived number can be
wrong while every input it derives from is right, which is invisible to a value-matching check on
the inputs.

    python -m puckworks.paper_b2.derived_bindings
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
BUNDLE = REPO / "docs" / "figures" / "paper_b_results.json"


def _bundle() -> dict:
    return json.loads(BUNDLE.read_text(encoding="utf-8"))


def _ratio(comparison: str):
    """|mean paired difference| / the OTHER-FOUR TEMPLATE rmse.

    The denominator is the held-out empirical template's error, NOT the leave-in dispersion. I
    assumed the latter when writing this and produced two mismatches that read like stale
    manuscript numbers; the declared arithmetic in `CONFIG_CONSTANTS` names
    `shot_level.dispersion.other_four_template_rmse_g_per_s` explicitly, and with it the values
    reproduce (2.094 -> 2.1, 2.531 -> 2.5). Worth recording: a binding written against the wrong
    operand accuses correct prose, which is a more damaging failure than leaving it unbound.
    """
    def f(d):
        num = abs(d["shot_level"]["paired"]["comparisons"][comparison]
                  ["mean_difference_g_per_s"])
        den = d["shot_level"]["dispersion"]["other_four_template_rmse_g_per_s"]
        return num / den
    return f


def _max_abs_gap(d):
    """Largest |LOPO-EC mean - shared-calibration mean| across the three branches."""
    a = d["loco"]["heldout_mean"]
    b = d["loco"]["shared_calibration_mean"]
    return max(abs(a[k] - b[k]) for k in a)


#: manuscript token -> (callable over the bundle, absolute tolerance)
#:
#: Tolerances are half a unit in the last displayed place: a value printed to 2 dp is checked to
#: 2 dp, not to "close enough".
DERIVED: dict[str, tuple] = {
    "2.1": (_ratio("phi_vs_const"), 5e-2),
    "2.5": (_ratio("phi_vs_static"), 5e-2),
    "0.013": (_max_abs_gap, 5e-4),
    "2.8": (lambda d: d["loco"]["max_calibration_drift"] * 100.0, 5e-2),
}

#: Values that are SOURCE quantities, not results of ours. They need provenance, not
#: recomputation: reproducing them is the verification, and that is a gate's job, not a binding's.
SOURCE_VALUES: dict[str, str] = {
    "12.39": "published equilibrium calibration P_c (bar), as printed by Waszkiewicz et al.",
    "1.897": "published equilibrium calibration Q_c (g/s), as printed by the source",
    "12.394": "P_c recovered by our refit of the source's own static model; the agreement with "
              "12.39 IS the reproduction claim, so binding it to our own refit would be circular",
    "1.907": "Q_c recovered by our refit; see 12.394",
}


def verify() -> dict:
    d = _bundle()
    ok, mismatched, unresolvable = [], [], []
    for token, (fn, tol) in sorted(DERIVED.items()):
        try:
            value = float(fn(d))
        except Exception as exc:                                     # noqa: BLE001
            unresolvable.append((token, f"{type(exc).__name__}: {exc}"))
            continue
        if abs(float(token) - value) <= tol:
            ok.append((token, value))
        else:
            mismatched.append((token, value, float(token) - value))
    return dict(n_bound=len(DERIVED), n_ok=len(ok), n_mismatched=len(mismatched),
                n_unresolvable=len(unresolvable), n_source_values=len(SOURCE_VALUES),
                ok=ok, mismatched=mismatched, unresolvable=unresolvable)


def main(argv=None) -> int:                                          # pragma: no cover
    r = verify()
    print(f"B2 derived bindings: {r['n_ok']}/{r['n_bound']} recompute and match; "
          f"{r['n_mismatched']} mismatched; {r['n_unresolvable']} unresolvable; "
          f"{r['n_source_values']} source values (provenance, not recomputation)")
    for token, value, delta in r["mismatched"]:
        print(f"  MISMATCH {token:>8}  recomputed {value!r}  delta {delta:+.6g}")
    for token, why in r["unresolvable"]:
        print(f"  UNRESOLVABLE {token:>8}  {why}")
    return 1 if (r["n_mismatched"] or r["n_unresolvable"]) else 0


if __name__ == "__main__":                                           # pragma: no cover
    raise SystemExit(main())
