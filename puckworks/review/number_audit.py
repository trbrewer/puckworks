"""Paper-agnostic numeral audit: every number in a manuscript body must be accounted for.

This is the engine extracted from `paper_b.claim_coverage`, which closed Paper 2 from 150
unaccounted numerals to zero and found three unbacked values on the way — including two that had
been transcribed from a reviewer's own table with no producer in this repository behind them.
Papers 1 and 3 had no equivalent: Paper 1 prints ~563 numerals against 27 registered claims, and
Paper 3 ~404. An unregistered number is an unchecked number, and it looks exactly like a checked
one.

Each numeral in the audited body is forced into one disposition. `producer`, `archive` and `code`
are all VERIFIED -- the manuscript's value is compared against something that computed it. `config`,
`dataset` and `cited` are documented EXEMPTIONS: a human explanation, checked by nothing. The
distinction is the point of the audit, so the two groups are counted separately:

``producer``    matches a registered claim, so a producer computes it
``config``      a declared protocol/configuration constant, registered with its source
``dataset``     a fact about a source dataset, traceable to the deposit and the manifest
``derived``     a ratio or percentage of producer-backed values, RECOMPUTED here, not assumed
``cited``       attributed to an external work
``structural``  section/table/figure numbers, counts, years — not measurements
``UNACCOUNTED`` none of the above

`UNACCOUNTED` is the output that matters. It is not a lint warning to be silenced: it is the list
of numbers a reader cannot trace, and the response is to bind one to a producer or withdraw it.

A `PaperSpec` supplies the per-paper registries; the classification logic is shared so the three
papers cannot drift apart in how they decide what "accounted for" means.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A numeral token: integer or decimal, optionally signed, optionally with a percent sign.
NUMERAL = re.compile(r"(?<![\w.$])(-?\d+(?:\.\d+)?)\s*(%?)(?![\w.])")

#: Numerals that are structural rather than quantitative.
STRUCTURAL_PATTERNS = (
    re.compile(r"§\s*\d+(?:\.\d+)?[a-z]?"),
    re.compile(r"(?m)^#{1,6}\s+\d+(?:\.\d+)*[a-z]?"),
    re.compile(r"\b(?:Table|Figure|Fig\.|Eq\.|Equation|Result|Rung|rung|Appendix)\s*\d+[a-z]?"),
    re.compile(r"\bRC-\d+[a-z]?"),
    re.compile(r"\b(?:19|20)\d{2}\b"),
    re.compile(r"\b\d+\s*(?:of|/)\s*\d+\b"),
    re.compile(r"\bP\d\.\d+\b|\bMAJ-\d+\b|\bB\d-\d+\b|\bMC\d+\b|\bU\d+\b|\bA\d+\b"),
    re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]"),          # bracketed citation markers
    re.compile(r"\bdoi:\S+|10\.\d{4,}/\S+"),            # DOIs carry digits that are not results
    re.compile(r"\bv?\d+\.\d+\.\d+(?:\.dev\d+)?\b"),    # version strings
    re.compile(r"\bPython\s*3\.\d+\b|\bschema\s*\d+(?:\.\d+)?\b|\bSCHEMA_VERSION\b"),
    re.compile(r"\bissue\s*#\d+|#\d{2,}"),
)

#: Spans whose numerals are NOT manuscript claims: LaTeX math, fenced code, inline code, HTML
#: comments (the inline section-reference labels), and markdown links.
EXCLUDED_SPANS = (
    re.compile(r"\$\$.*?\$\$", re.S),
    re.compile(r"\$[^$\n]+\$"),
    re.compile(r"\\\(.*?\\\)", re.S),        # inline LaTeX \( ... \): equation constants
    re.compile(r"\\\[.*?\\\]", re.S),        # display LaTeX
    re.compile(r"```.*?```", re.S),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"\]\([^)]*\)"),
)


@dataclass
class PaperSpec:
    """Everything paper-specific the shared engine needs."""

    name: str
    manuscript: Path
    #: () -> list of (label, bundle_path, expected, tol) — the registered claim map.
    claims: object
    #: Sections whose numerals are not manuscript results (references, appendices of provenance).
    skip_sections: tuple = ()
    config_constants: dict = field(default_factory=dict)
    dataset_facts: dict = field(default_factory=dict)
    cited_values: dict = field(default_factory=dict)
    #: token -> (kind, path_a, path_b); recomputed from the bundle, never assumed.
    derived: dict = field(default_factory=dict)
    #: () -> the results bundle, for recomputing `derived`.
    bundle: object = None
    #: Committed ceiling on unaccounted numerals. A ratchet: it may fall, never rise.
    baseline: int = 0


def _spans(text, patterns):
    out = []
    for rx in patterns:
        out.extend((m.start(), m.end()) for m in rx.finditer(text))
    return out


def _in_span(pos, spans):
    return any(a <= pos < b for a, b in spans)


def body_of(text: str, skip_sections=()) -> str:
    """The manuscript body, ending at the EARLIEST non-results section.

    The boundary matters: appending a fault after `## References` puts it where the audit
    deliberately does not look, which would make a fault-injection test pass for the wrong reason.
    """
    cut = len(text)
    for marker in skip_sections:
        i = text.find(marker)
        if i != -1:
            cut = min(cut, i)
    return text[:cut]


def context(body: str, start: int, end: int, width: int = 70) -> str:
    a, b = max(0, start - width), min(len(body), end + width)
    return ("…" if a > 0 else "") + " ".join(body[a:b].split()) + ("…" if b < len(body) else "")


def _half_up(x: float, places: int) -> float:
    """Round half AWAY FROM ZERO, the convention prose uses.

    Python rounds half to even, so round(5.05, 1) is 5.0 while a manuscript writes 5.1. Matching on
    the banker's result reported correct numbers as unaccounted.
    """
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(1).scaleb(-places)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


def _sig_figs(token: str) -> int:
    """Significant digits the PRINTED token carries.

    An integer written with trailing zeros ("3600", "1900") is prose rounding to significant
    figures, not an exact count, so those zeros do not count as significant.
    """
    s = token.lstrip("-")
    if "." in s:
        return len(s.replace(".", "").lstrip("0")) or 1
    return len(s.rstrip("0").lstrip("0")) or 1


def _round_sig(x: float, sig: int) -> float:
    import math
    if x == 0 or sig < 1:
        return x
    return round(x, -int(math.floor(math.log10(abs(x)))) + (sig - 1))


def matches_a_claim(value: float, claims, is_percent: bool = False,
                    token: str | None = None) -> str | None:
    """A numeral is producer-bound if it equals a registered claim's expected value.

    Rounding is allowed in the manuscript's favour (a claim of 0.1157 covers a printed 0.116), and
    magnitudes match signed claims, because prose carries direction in words ("beats it by 0.390")
    while the producer carries a sign. A DIFFERENT number never matches — that is the failure this
    exists to catch.
    """
    for entry in claims:
        expected = entry[2]
        try:
            e0 = float(expected)
        except (TypeError, ValueError):
            continue
        # A percent token may be printed against a claim stored as a FRACTION ("76 %" for 0.76).
        # Applied only when the token actually carries '%', so it cannot silently match unrelated
        # values that happen to differ by 100x.
        candidates = [e0, abs(e0)]
        if is_percent:
            candidates += [e0 * 100.0, abs(e0) * 100.0]
        for e in candidates:
            if value == e:
                return entry[0]
            for places in range(0, 7):
                if round(e, places) == value or _half_up(e, places) == value:
                    return entry[0]
            if e != 0 and abs(value - e) / abs(e) < 1e-9:
                return entry[0]
            # Prose also rounds to SIGNIFICANT FIGURES ("condition number ~= 3600" for 3619.2).
            # Only applied when the printed token itself looks sig-fig rounded -- an integer whose
            # trailing zeros are not significant -- so it cannot loosen ordinary decimals.
            if token is not None and "." not in token.rstrip("%") and abs(value) >= 100:
                sig = _sig_figs(token.rstrip("%"))
                if sig < len(str(int(abs(value)))) and _round_sig(e, sig) == value:
                    return entry[0]
    return None


def _get(bundle, path):
    """Dotted-path lookup tolerating keys that themselves contain dots, and list indices."""
    cur = bundle
    parts = path.split(".")
    i = 0
    while i < len(parts):
        if isinstance(cur, dict):
            for take in range(len(parts) - i, 0, -1):
                key = ".".join(parts[i:i + take])
                if key in cur:
                    cur = cur[key]
                    i += take
                    break
            else:
                raise KeyError(parts[i])
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(parts[i])]
            i += 1
        else:
            cur = cur[parts[i]]
            i += 1
    return cur


def derived_value(spec: PaperSpec, kind: str, a_path: str, b_path: str):
    """Recompute a derived quantity from the bundle. None when unavailable."""
    if spec.bundle is None:
        return None
    try:
        bundle = spec.bundle()
    except Exception:
        return None
    try:
        if kind == "max_abs_gap":
            left, right = _get(bundle, a_path), _get(bundle, b_path)
            return max(abs(float(left[k]) - float(right[k])) for k in left if k in right)
        a = abs(float(_get(bundle, a_path)))
        if kind == "percent":
            return a * 100.0
        b = abs(float(_get(bundle, b_path)))
        return a / b if b else None
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def audit(spec: PaperSpec, path: Path | None = None) -> dict:
    src = (path or spec.manuscript).read_text(encoding="utf-8")
    body = body_of(src, spec.skip_sections)
    claims = list(spec.claims())
    structural = _spans(body, STRUCTURAL_PATTERNS)
    excluded = _spans(body, EXCLUDED_SPANS)

    findings = []
    for m in NUMERAL.finditer(body):
        if _in_span(m.start(), excluded):
            continue
        raw, pct = m.group(1), m.group(2)
        token, value = raw + pct, float(raw)
        line = body.count("\n", 0, m.start()) + 1

        if _in_span(m.start(), structural):
            disposition, why = "structural", "section/table/figure/count/year/DOI reference"
        elif token in spec.config_constants or raw in spec.config_constants:
            why = spec.config_constants.get(token) or spec.config_constants[raw]
            # A value that is CHECKED against the record which produced it is not a config
            # exemption, and must not be counted as one. Before this, binding a number changed its
            # explanation but not its disposition, so the headline "producer-bound" figure did not
            # move when the binding work was done -- a progress metric that cannot show progress,
            # which is the same class of defect this audit exists to catch.
            if why.startswith("ARCHIVE-BOUND"):
                disposition = "archive"
            elif why.startswith("CODE-BOUND"):
                disposition = "code"
            else:
                disposition = "config"
        elif raw in spec.dataset_facts:
            disposition, why = "dataset", spec.dataset_facts[raw]
        elif raw in spec.cited_values:
            disposition, why = "cited", spec.cited_values[raw]
        else:
            label = matches_a_claim(value, claims, is_percent=bool(pct), token=token)
            if label:
                disposition, why = "producer", label
            elif raw in spec.derived:
                kind, a_path, b_path = spec.derived[raw]
                got = derived_value(spec, kind, a_path, b_path)
                places = 2 if abs(value) < 0.1 else 1
                if got is None:
                    disposition, why = "UNACCOUNTED", f"derived {kind} could not be recomputed"
                elif round(got, places) == round(value, places):
                    disposition = "derived"
                    why = f"{kind} of {a_path}" + (f" / {b_path}" if b_path else "")
                else:
                    disposition, why = "UNACCOUNTED", (
                        f"derived {kind} recomputes to {got:.4f}, manuscript prints {value}")
            else:
                disposition, why = "UNACCOUNTED", "no producer, config entry or citation"

        findings.append(dict(token=token, value=value, line=line, disposition=disposition,
                             why=why, context=context(body, m.start(), m.end())))

    counts: dict[str, int] = {}
    for f in findings:
        counts[f["disposition"]] = counts.get(f["disposition"], 0) + 1
    return dict(paper=spec.name, n_numerals=len(findings), n_claims=len(claims), counts=counts,
                unaccounted=[f for f in findings if f["disposition"] == "UNACCOUNTED"],
                findings=findings)


ORDER = ("producer", "config", "dataset", "derived", "cited", "structural", "UNACCOUNTED")


def render(report: dict) -> str:
    lines = [f"{report['paper']} — numeral audit", "",
             f"{report['n_numerals']} numerals in the body; {report['n_claims']} registered claims"]
    for k in ORDER:
        lines.append(f"  {k:12s} {report['counts'].get(k, 0)}")
    if report["unaccounted"]:
        lines += ["", "UNACCOUNTED — bind to a producer or withdraw:"]
        for f in report["unaccounted"]:
            lines.append(f"  L{f['line']:<5d} {f['token']:>10s}   {f['context'][:120]}")
    return "\n".join(lines)
