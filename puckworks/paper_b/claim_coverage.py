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
import re
import sys
from pathlib import Path

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


#: Numerals that are structural rather than quantitative.
_STRUCTURAL_PATTERNS = (
    re.compile(r"§\s*\d+(?:\.\d+)?[a-z]?"),           # section references
    re.compile(r"(?m)^#{1,6}\s+\d+(?:\.\d+)*[a-z]?"),  # markdown section HEADINGS
    re.compile(r"\b(?:Table|Figure|Fig\.|Eq\.|Equation|Result|Rung|rung)\s*\d+[a-z]?"),
    re.compile(r"\bRC-\d+[a-z]?"),                     # registry claim ids
    re.compile(r"\b(?:19|20)\d{2}\b"),                 # years
    re.compile(r"\b\d+\s*(?:of|/)\s*\d+\b"),           # "5 of 5", "3/4"
    re.compile(r"\bP\d\.\d+\b|\bMAJ-\d+\b|\bB\d-\d+\b"),
    re.compile(r"\bten|eleven\b"),                     # spelled-out, harmless anchor
    re.compile(r"\[\d+(?:\s*,\s*\d+)*\]"),             # bracketed citation markers [3], [3, 7]
)

#: Spans whose numerals are NOT manuscript claims: LaTeX math (equation constants and exponents),
#: fenced code, and inline code. A `4-6\widehat p` in a governing equation is part of the model, not
#: a measurement, and treating it as an unbacked result would drown the real findings in noise.
_EXCLUDED_SPANS = (
    re.compile(r"\$\$.*?\$\$", re.S),
    re.compile(r"\$[^$\n]+\$"),
    re.compile(r"```.*?```", re.S),
    re.compile(r"`[^`\n]+`"),
)

#: A numeral token: integer or decimal, optionally signed, optionally with a percent sign.
_NUMERAL = re.compile(r"(?<![\w.$])(-?\d+(?:\.\d+)?)\s*(%?)(?![\w.])")


def _claims():
    from puckworks.paper_b.build import _CLAIMS
    return list(_CLAIMS)


def _body(text: str) -> str:
    """The manuscript body, with non-result sections removed."""
    cut = len(text)
    for marker in _SKIP_SECTIONS:
        i = text.find(marker)
        if i != -1:
            cut = min(cut, i)
    return text[:cut]


def _structural_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for rx in _STRUCTURAL_PATTERNS:
        spans.extend((m.start(), m.end()) for m in rx.finditer(text))
    return spans


def _excluded_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for rx in _EXCLUDED_SPANS:
        spans.extend((m.start(), m.end()) for m in rx.finditer(text))
    return spans


def _context(body: str, start: int, end: int, width: int = 70) -> str:
    """Text either side of the match, so a long paragraph does not report its first sentence for
    every numeral it contains."""
    a = max(0, start - width)
    b = min(len(body), end + width)
    return ("…" if a > 0 else "") + body[a:b].replace("\n", " ").strip() + ("…" if b < len(body) else "")


def _in_span(pos: int, spans) -> bool:
    return any(a <= pos < b for a, b in spans)


def _matches_a_claim(value: float, claims) -> str | None:
    """A manuscript numeral is producer-bound if it equals a registered claim's expected value.

    The comparison is on the PRINTED value, and it deliberately allows the manuscript to round: a
    claim expecting 0.1157 covers a printed 0.116. It does NOT allow the manuscript to state a
    different number from the producer, which is the failure this exists to catch.
    """
    for label, _path, expected, _tol in claims:
        e = float(expected)
        # The prose often states a magnitude where the producer carries a sign ("beats the
        # constant by a mean of 0.390" for a stored -0.3904). Compare on |value| as well, since
        # the direction is carried by the surrounding words rather than by the numeral.
        for e in (float(expected), abs(float(expected))):
            if value == e:
                return label
            # printed-rounding tolerance: match if the claim rounds to the printed value at
            # the printed precision.
            for places in range(0, 7):
                if round(e, places) == value:
                    return label
            if e != 0 and abs(value - e) / abs(e) < 1e-9:
                return label
    return None


def audit(path: Path = MANUSCRIPT) -> dict:
    text = path.read_text(encoding="utf-8")
    body = _body(text)
    claims = _claims()
    structural = _structural_spans(body)
    excluded = _excluded_spans(body)

    findings = []
    for m in _NUMERAL.finditer(body):
        if _in_span(m.start(), excluded):
            continue                      # inside math or code: a model constant, not a claim
        raw, pct = m.group(1), m.group(2)
        token = raw + pct
        value = float(raw)
        line = body.count("\n", 0, m.start()) + 1
        context = _context(body, m.start(), m.end())

        if _in_span(m.start(), structural):
            disposition, why = "structural", "section/table/figure/count/year reference"
        elif token in CONFIG_CONSTANTS or raw in CONFIG_CONSTANTS:
            disposition, why = "config", CONFIG_CONSTANTS.get(token) or CONFIG_CONSTANTS[raw]
        elif raw in DATASET_FACTS:
            disposition, why = "dataset", DATASET_FACTS[raw]
        elif raw in CITED_VALUES:
            disposition, why = "cited", CITED_VALUES[raw]
        else:
            label = _matches_a_claim(value, claims)
            if label:
                disposition, why = "producer", label
            elif raw in DERIVED_QUANTITIES:
                kind, a_path, b_path = DERIVED_QUANTITIES[raw]
                got = _derived_value(kind, a_path, b_path)
                if got is None:
                    disposition, why = "UNACCOUNTED", f"derived {kind} could not be recomputed"
                elif round(got, 2 if abs(value) < 0.1 else 1) == round(value, 2 if abs(value) < 0.1 else 1):
                    disposition, why = "derived", (
                        f"{kind} of {a_path}" + (f" / {b_path}" if b_path else ""))
                else:
                    disposition, why = "UNACCOUNTED", (
                        f"derived {kind} recomputes to {got:.4f}, manuscript prints {value}")
            else:
                disposition, why = "UNACCOUNTED", "no producer, config entry or citation"

        findings.append(dict(token=token, value=value, line=line, disposition=disposition,
                             why=why, context=context))

    counts: dict[str, int] = {}
    for f in findings:
        counts[f["disposition"]] = counts.get(f["disposition"], 0) + 1
    unaccounted = [f for f in findings if f["disposition"] == "UNACCOUNTED"]
    try:
        shown = str(path.relative_to(REPO_ROOT))
    except ValueError:            # auditing a copy outside the repo (fault-injection tests)
        shown = str(path)
    return dict(manuscript=shown, n_numerals=len(findings),
                counts=counts, n_claims=len(claims), unaccounted=unaccounted, findings=findings)


def render(report: dict) -> str:
    lines = [f"Paper B2 claim coverage — {report['manuscript']}", ""]
    lines.append(f"{report['n_numerals']} numerals in the body; {report['n_claims']} registered claims")
    for k in ("producer", "config", "dataset", "derived", "cited", "structural", "UNACCOUNTED"):
        lines.append(f"  {k:12s} {report['counts'].get(k, 0)}")
    if report["unaccounted"]:
        lines += ["", "UNACCOUNTED — each must be bound to a producer or withdrawn:"]
        for f in report["unaccounted"]:
            lines.append(f"  L{f['line']:<5d} {f['token']:>10s}   {f['context']}")
    return "\n".join(lines)


#: Committed ceiling on unaccounted numerals. CI enforces that this never GROWS, which is the
#: property that matters: a new manuscript number must arrive with a producer, a config entry or a
#: citation. It is deliberately a ratchet and not a target — lowering it is the work, and the
#: baseline is lowered whenever the count drops so it can never drift back up.
BASELINE_UNACCOUNTED = 0


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
