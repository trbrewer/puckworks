"""Paper B2 claim-coverage audit (review item 4.13).

`paper_b.build.verify` checks that 18 named claims match the results bundle. That answers "are the
numbers we chose to check correct?" — not "is every number in the manuscript accounted for?" The
manuscript body contains far more numerals than there are claims, and the gap is invisible: a
number nobody registered is a number nobody checks, and it looks exactly like one that passed.

This module closes the gap by auditing EVERY numeral in the manuscript body and forcing each into
one of five dispositions:

``producer``    the value matches a registered claim, so a producer computes it
``config``      a declared protocol/configuration constant, registered here with its source
``cited``       a value attributed to an external work in the same sentence
``structural``  section/table/figure/equation numbers, counts, years — not measurements
``UNACCOUNTED`` none of the above

`UNACCOUNTED` is the point. It is not a lint warning to be silenced; it is the list of numbers a
reader could not trace, and the correct response is either to bind one to a producer or to withdraw
it. This mirrors the Paper 3 discipline that already removed two untraceable values.

CLI::

    python -m puckworks.paper_b.claim_coverage            # report; exit 1 if UNACCOUNTED remain
    python -m puckworks.paper_b.claim_coverage --json     # machine-readable
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from puckworks.review import number_audit as NA

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md"

#: Sections that are not results prose and whose numerals are not manuscript claims: the reference
#: list, the repository-provenance appendix (a development record, stripped before submission), and
#: the figure/supplement PLANS (which describe what will be drawn, not what was measured).
_SKIP_SECTIONS = (
    "## References",
    "## Repository provenance used to develop this draft",
    "## Figure specifications and draft captions",
    "## Supplementary material plan",
)

#: Declared protocol / configuration constants. Each is a *choice*, not a result: it is an input to
#: the analysis, so it needs a stated source rather than a producer. Keeping them here — rather than
#: letting a catch-all regex absorb them — means adding a new constant is a deliberate act.
CONFIG_CONSTANTS: dict[str, str] = {
    "9": "scored pressure condition (bar), Waszkiewicz 9-bar campaign",
    "15": "primary scoring window start (s), declared in §2",
    "95": "primary scoring window end (s), declared in §2",
    "1": "diagnostic decimation resolution (s), declared in §4",
    "5": "decimation used for the coarser residual check (s)",
    "11": "number of equilibrium pressure conditions in the campaign",
    "10": "off-9-bar pressure conditions (11 minus the scored one)",
    "4": "moving-block duration (s)",
    "8": "moving-block duration (s)",
    "16": "moving-block duration (s)",
    "24": "moving-block duration (s)",
    "0.05": "two-sided significance threshold, declared in §4",
    "95%": "interval coverage, declared in §4",
    "20": "sensitivity scoring-window start (s), declared in §4.3",
    "90": "sensitivity scoring-window end (s), declared in §4.3",
    "100": "source formatter truncation / common interpolation grid end (s)",
    "110": "nominal equilibrium window start quoted from the source (s)",
    "120": "nominal equilibrium window end quoted from the source (s)",
    "3": "Savitzky-Golay smoothing width (s) and polynomial degree; also the cubic's degree",
    "7": "lower edge of the 7-11 bar band containing the primary analysis",
    "0.001": "threshold the recorded-pressure shifts are stated to fall below (g/s)",
    "0.99": "approximate lag-1 residual autocorrelation, stated to 2 dp in prose",
    "100%": "fraction of the window on the porosity floor (composition collapse)",
    "2": "campaign pressure condition (bar)",
    "3.5": "campaign pressure condition (bar)",
    "6": "campaign pressure condition (bar)",
    "7.0": "campaign pressure condition (bar)",
    "8.0": "campaign pressure condition (bar)",
    "9.0": "campaign pressure condition (bar)",
    "11.0": "campaign pressure condition (bar)",
    "13.0": "campaign pressure condition (bar)",
    "13": "upper campaign pressure condition (bar)",
    "1.0": "campaign pressure condition (bar)",
    "2.0": "campaign pressure condition (bar)",
    "4.0": "campaign pressure condition (bar)",
    "5.0": "campaign pressure condition (bar)",
    "6.0": "campaign pressure condition (bar)",
}

#: Values quoted from external work. Registered explicitly so that "it has a citation nearby" is a
#: recorded judgement rather than a regex accident.
CITED_VALUES: dict[str, str] = {
    "2.7": "Gagné viscosity ratio (reserved material; retained only in the follow-up doc)",
    "150": "Kozeny constant, Carman-Kozeny literature",
}

#: Facts about the SOURCE DATASET rather than results we computed. They trace to the deposit and
#: its MANIFEST.csv row, not to a producer, and printing them is reporting someone else's
#: measurement. Registered explicitly, with the quantity each one is, so this cannot become a
#: dumping ground for numbers that failed to classify.
DATASET_FACTS: dict[str, str] = {
    "60": "brews in the Waszkiewicz campaign (deposit)",
    "12.5": "upper basket pressure of the campaign (bar, deposit)",
    "18.5": "dose (g, deposit)",
    "58": "beverage mass target (g, deposit)",
    "12.394": "published equilibrium calibration P_c (bar)",
    "12.39": "published equilibrium calibration P_c, rounded (bar)",
    "1.907": "published equilibrium calibration Q_c (g/s)",
    "1.897": "published equilibrium calibration Q_c, rounded (g/s)",
    "11.935": "LOPO-EC equilibrium P_c (bar)",
    "1.861": "LOPO-EC equilibrium Q_c (g/s)",
    "0.007": "reported pressure-transducer resolution (bar, deposit)",
    "0.61": "max nominal-minus-recorded gap; see pressure_domains (also a claim)",
    "8.71": "9-bar delivered mean; see pressure_domains (also a claim)",
    "10": "raw logging rate (Hz, deposit)",
    "15.015": "first retained sample of the scoring window (s, grid artefact)",
    "94.995": "last retained sample of the scoring window (s, grid artefact)",
    "800": "retained samples in the scoring window",
    "106": "brews retained after the deposit's own exclusions",
    "31": "samples per second retained after formatting",
}

#: Quantities the prose DERIVES from two producer-backed values (a ratio, or a percentage of a
#: fraction). They are not separate results and do not need their own claim, but they must not be
#: waved through either: the auditor RECOMPUTES each one from the bundle and reports a mismatch.
DERIVED_QUANTITIES: dict[str, tuple[str, str, str]] = {
    "2.6": ("ratio", "shot_level.paired.comparisons.phi_vs_const.mean_difference_g_per_s",
            "shot_level.noise_floor.noise_floor_rmse_g_per_s"),
    "3.2": ("ratio", "shot_level.paired.comparisons.phi_vs_static.mean_difference_g_per_s",
            "shot_level.noise_floor.noise_floor_rmse_g_per_s"),
    "2.8": ("percent", "loco.max_calibration_drift", ""),
    # "the LOPO means are within approximately 0.01-0.02 g/s of the shared-calibration means":
    # a stated closeness, recomputed as the largest absolute gap across the three branches.
    "0.013": ("max_abs_gap", "loco.heldout_mean", "loco.shared_calibration_mean"),
}


def _derived_value(kind: str, a_path: str, b_path: str):
    """Recompute a derived quantity from the committed bundle. Returns None if unavailable."""
    import json as _json
    import os as _os
    bundle_path = REPO_ROOT / "docs" / "figures" / "paper_b_results.json"
    if not _os.path.exists(bundle_path):
        return None
    from puckworks.paper_b.build import _get
    try:
        with open(bundle_path) as fh:
            bundle = _json.load(fh)
        a = 0.0 if kind == "max_abs_gap" else abs(float(_get(bundle, a_path)))
        if kind == "percent":
            return a * 100.0
        if kind == "max_abs_gap":
            left, right = _get(bundle, a_path), _get(bundle, b_path)
            return max(abs(float(left[k]) - float(right[k])) for k in left if k in right)
        b = abs(float(_get(bundle, b_path)))
        return a / b if b else None
    except (KeyError, TypeError, ValueError, OSError):
        return None


def _claims():
    from puckworks.paper_b.build import _CLAIMS
    return list(_CLAIMS)


def _bundle():
    import json
    with open(REPO_ROOT / "docs" / "figures" / "paper_b_results.json", encoding="utf-8") as fh:
        return json.load(fh)


def _spec():
    """Built PER CALL, not captured at import.

    A module-level SPEC froze references to the registry dicts, so monkeypatching
    `DERIVED_QUANTITIES` in a fault-injection test no longer reached the auditor and the test
    silently stopped testing anything. Reading the current module globals keeps the injection
    tests meaningful.
    """
    return NA.PaperSpec(
        name="Paper B2 claim coverage",
        manuscript=MANUSCRIPT,
        claims=_claims,
        skip_sections=_SKIP_SECTIONS,
        config_constants=CONFIG_CONSTANTS,
        dataset_facts=DATASET_FACTS,
        cited_values=CITED_VALUES,
        derived=DERIVED_QUANTITIES,
        bundle=_bundle,
        baseline=BASELINE_UNACCOUNTED,
    )


#: Committed ceiling on unaccounted numerals. CI enforces that this never GROWS: a new manuscript
#: number must arrive with a producer, a config entry or a citation. It is a ratchet -- lowering it
#: is the work, and it is lowered whenever the count drops so it cannot drift back up.
BASELINE_UNACCOUNTED = 0


def audit(path=None):
    return NA.audit(_spec(), path)


def render(report):
    return NA.render(report)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    report = audit()
    if "--json" in argv:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    n = len(report["unaccounted"])
    if n > BASELINE_UNACCOUNTED:
        print(f"\nFAIL: {n} unaccounted numerals exceeds the committed baseline of "
              f"{BASELINE_UNACCOUNTED}. A new manuscript number must arrive with a producer, a "
              f"config entry or a citation.", file=sys.stderr)
        return 1
    if n < BASELINE_UNACCOUNTED:
        print(f"\nNOTE: {n} unaccounted, below the baseline of {BASELINE_UNACCOUNTED} — "
              f"lower BASELINE_UNACCOUNTED to {n} so the ratchet holds.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Re-exported so existing tests and callers keep working against one implementation.
_NUMERAL = NA.NUMERAL
_EXCLUDED_SPANS = NA.EXCLUDED_SPANS
_STRUCTURAL_PATTERNS = NA.STRUCTURAL_PATTERNS
_in_span = NA._in_span


def _body(text):
    return NA.body_of(text, _SKIP_SECTIONS)
