"""Paper 3 numeral audit — every number in the PROSE must be accounted for.

Paper 3 differs from the other two. It has no `_CLAIMS` table: most of its quantitative content is
spliced in as GENERATED BLOCKS (the corpus denominators, the availability matrix, the
implementation-status table, the named-shot scorecard, Appendix B), and numbers inside those are
producer-backed by construction — regenerating them is what `paper3.build verify` checks.

The exposure is therefore the PROSE: sentences that quote a count, a fraction or a measurement in
the author's own words, outside any generated block. Those are exactly the numbers that go stale
when the registry changes, and nothing regenerates them. This audit excludes the generated spans
and reports what is left.

Registry-derived counts are checked live rather than listed: a prose claim of "27 components" is
matched against `len(registry.components())`, so it fails when the registry grows.

CLI::

    python -m puckworks.paper3.claim_coverage
    python -m puckworks.paper3.claim_coverage --json
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from puckworks.review import number_audit as NA

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"

#: Not results prose: the reference list and the development-provenance appendix, which is
#: explicitly strip-before-submission scaffolding.
SKIP_SECTIONS = (
    "## References",
    "## Repository provenance used to develop this draft",
)

#: Spliced generated blocks. Numbers inside are regenerated and checked by `paper3.build verify`;
#: auditing them here would double-count machinery that already exists.
GENERATED_BLOCKS = (
    ("<!-- corpus:begin -->", "<!-- corpus:end -->"),
    ("<!-- availability:begin -->", "<!-- availability:end -->"),
    ("<!-- implstatus:begin -->", "<!-- implstatus:end -->"),
    ("<!-- scorecard:begin -->", "<!-- scorecard:end -->"),
    ("<!-- appendix-b:begin -->", "<!-- appendix-b:end -->"),
)

CONFIG_CONSTANTS: dict[str, str] = {
    "0.05": "significance threshold where quoted",
    "95": "interval coverage (%)",
    "9": "scored pressure condition (bar) in the borrowed temporal example",
    "15": "scoring-window start (s) in the borrowed temporal example",
    "400": "integration horizon (s) for the timescale comparison, declared in §2.2a",
    "0": "tau=0 initial condition, declared in §2.2a",
    "1.4": "grinder dial setting in the Schmieder design (non-portable coordinate)",
    "1.7": "grinder dial setting in the Schmieder design (non-portable coordinate)",
    "2.0": "grinder dial setting in the Schmieder design (non-portable coordinate)",
    "25": "draft date (25 July 2026)",
    "30": "Cameron's validated recipe horizon (s), stated on its model card",
    "0.17": "bed porosity recorded on the source card (the defect-injection baseline)",
    "0.35": "physically wrong but dimensionally valid porosity used as an injected defect",
    "13": "lower end of the permeability-closure disagreement (x), Wadsworth vs modified-Kozeny",
    "31": "upper end of the permeability-closure disagreement (x)",
    "20": "selected fine-particle class radius (um) declared in §2.2a; also the median permeability-closure disagreement (x)",
    "80": "lower end of the Schmieder-Pannusch temperature range (degC)",
    "98": "upper end of the Schmieder-Pannusch temperature range (degC)",
    "256": "SHA-256 digest width, not a measurement",
    "0.7": "public contract schema version",
}

DATASET_FACTS: dict[str, str] = {}
CITED_VALUES: dict[str, str] = {}
DERIVED_QUANTITIES: dict[str, tuple[str, str, str]] = {}

#: Ratchet.
BASELINE_UNACCOUNTED = 0


def _live_counts() -> dict[str, float]:
    """Counts the manuscript may legitimately quote, taken from the LIVE registry and manifest.

    Checking these live is the point: a prose sentence saying "27 components" must fail when a
    28th is registered, which is precisely the drift MC2 was raised about.
    """
    import puckworks.models  # noqa: F401  (registers components)
    from puckworks import registry as R
    from puckworks.paper3 import corpus as C

    comps = list(R.components())
    d = C.denominators()
    rows = list(csv.DictReader((REPO_ROOT / "puckworks/data/MANIFEST.csv").open(encoding="utf-8")))
    out = {
        "n_components": len(comps),
        "n_gates": sum(len(getattr(c, "gates", ()) or ()) for c in comps),
        "n_manifest_rows": len(rows),
        "n_cards": len(list((REPO_ROOT / "docs/cards").glob("*.md"))),
        "n_publications": d["n_unique_source_publications"],
        "n_dois": d["n_unique_dois"],
        "n_dataset_sources": d["n_unique_dataset_sources"],
        "n_independent": d["n_components_with_independent_evidence"],
        "n_stages": len({c.stage for c in comps}),
    }
    for k, v in list(d["components_by_provenance_class"].items()):
        out["provenance:" + k] = v
    for k, v in list(d["components_by_execution_role"].items()):
        out["role:" + k] = v

    # Per-stage counts: Table 1 quotes one per stage, and a hand-written table is exactly what
    # goes stale when a component is registered.
    import collections
    for stage, n in collections.Counter(c.stage for c in comps).items():
        out["stage:" + stage] = n

    # Public-claim dependency counts quoted in section 5.2.
    from puckworks.public.claims import PUBLIC_CLAIMS
    deps = [dep for c in PUBLIC_CLAIMS for dep in c.dependencies]
    for kind in ("component", "producer", "dataset"):
        out["dependency:" + kind] = sum(1 for dep in deps if dep.kind == kind)
    pv05 = next((c for c in PUBLIC_CLAIMS if c.claim_id == "PV-05"), None)
    if pv05 is not None:
        prof = pv05.evidence_profile()
        out["pv05_records"] = len(prof)
        out["pv05_relations"] = len({r["relation"] for r in prof})
        out["pv05_observables"] = len({r["scope"] for r in prof})

    # Values BORROWED from the companion temporal paper. Bound to that paper's producers so the
    # two manuscripts cannot disagree, which is the failure mode this whole paper is about.
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    out["borrowed_extraction_only_rmse"] = round(float(ck.degeneracy_rmse()), 4)
    out["borrowed_composite_rmse"] = round(ck.composition_residual()["rmse"], 4)

    # The Schmieder worked example of section 7.2 quotes the companion paper's RSM numbers. Bind
    # them to the SAME producers that paper uses, so the two manuscripts cannot diverge -- the
    # structure that produced the stale Table 3 rc3b column.
    pv04 = next((c for c in PUBLIC_CLAIMS if c.claim_id == "PV-04"), None)
    if pv04 is not None and getattr(pv04, "numeric_result", None):
        for k, v in pv04.numeric_result.items():
            if isinstance(v, (int, float)):
                out["pv04:" + k] = float(v)
    from puckworks import harness as _h
    rsm = _h.schmieder_rsm_refit("tds", "1/2", predictors="achieved")
    out["rsm_adj_r2"] = rsm["adj_r2"]
    out["rsm_vertex_g"] = rsm["vertex_g"]

    # Maille's pooled timescale bands, and the defect-injection benchmark.
    from puckworks.models.maille2024 import two_regime as _m
    out["maille_fast_lo"], out["maille_fast_hi"] = _m.LAM_FAST_RANGE
    out["maille_slow_lo"], out["maille_slow_hi"] = _m.LAM_SLOW_RANGE
    from puckworks.paper3 import defect_injection as _di
    bench = _di.run_benchmark()
    for k in ("n_defects", "n_detected", "n_undetected", "detection_rate"):
        out["defect:" + k] = float(bench[k])

    # Section 7.5 quotes the cross-model timescale comparison. Bind every quoted constant to the
    # producer that computes it, so a refit cannot leave the prose behind.
    from puckworks.analysis import maille2024 as _ma
    def _leaves(d, pre=""):
        if isinstance(d, dict):
            for k, v in d.items():
                yield from _leaves(v, f"{pre}.{k}" if pre else k)
        elif isinstance(d, (list, tuple)):
            for i, v in enumerate(d):
                yield from _leaves(v, f"{pre}[{i}]")
        elif isinstance(d, (int, float)) and not isinstance(d, bool):
            yield pre, float(d)
    for prefix, payload in (("timescale", _ma.timescale_semantics_bundle()),
                            ("roman_sens", _ma.roman_protocol_sensitivity()),
                            ("cameron_ts", _ma.cross_model_timescale_cameron()),
                            ("roman_ts", _ma.cross_model_timescale_roman())):
        for k, v in _leaves(payload):
            out[f"{prefix}.{k}"] = v

    # The across-grind spread of the absolute constants is a RATIO the prose quotes; compute it
    # rather than listing it, so it tracks a refit.
    _pg = _ma.cross_model_timescale_roman()["per_grind"]
    _fast = [g["lambda_fast_s"] for g in _pg if isinstance(g.get("lambda_fast_s"), (int, float))]
    if _fast and min(_fast) > 0:
        out["roman_absolute_constant_spread"] = max(_fast) / min(_fast)

    # Ladder values borrowed from the companion temporal paper's committed bundle.
    import json as _json
    bpath = REPO_ROOT / "docs" / "figures" / "paper_b_results.json"
    if bpath.exists():
        pb = _json.loads(bpath.read_text(encoding="utf-8"))
        lad, lo = pb["ladder"], pb["loco"]
        out["borrowed_best_const"] = lad["rung1_const_kappa"]
        out["borrowed_static"] = lad["rung3_static_kappaP"]
        out["borrowed_phi"] = lad["rung4_phi_of_t"]
        out["borrowed_cubic"] = lad["flexible_cubic_null"]
        for k, v in lo["heldout_mean"].items():
            out["borrowed_heldout:" + k] = v

    # The saturation-concentration conflict is the paper's own worked example; take the values
    # from the registry of conflicts rather than from prose.
    from puckworks.paper3 import evidence_graph as EG
    for i, val in enumerate(sorted(_conflict_values(EG.CONSTANT_CONFLICTS))):
        out[f"c_sat_conflict_{i}"] = val
    return out


def _conflict_values(conflicts):
    """Numeric saturation-concentration values recorded in CONSTANT_CONFLICTS."""
    found = set()
    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            found.add(float(o))
        elif isinstance(o, str):
            for m in re.finditer(r"\b\d+(?:\.\d+)?\b", o):
                found.add(float(m.group(0)))
    walk(conflicts)
    return {v for v in found if 100.0 <= v <= 300.0}


def _claims():
    """Registry counts, shaped like a claim map so the shared engine can match them."""
    return [(f"live registry count: {k}", k, float(v), 0.0) for k, v in _live_counts().items()]


def _generated_spans(text: str):
    spans = []
    for begin, end in GENERATED_BLOCKS:
        i = text.find(begin)
        j = text.find(end)
        if i != -1 and j != -1 and j > i:
            spans.append((i, j + len(end)))
    return spans


def _spec(manuscript=None):
    return NA.PaperSpec(
        name="Paper 3 prose numeral audit",
        manuscript=manuscript or MANUSCRIPT,
        claims=_claims,
        skip_sections=SKIP_SECTIONS,
        config_constants=CONFIG_CONSTANTS,
        dataset_facts=DATASET_FACTS,
        cited_values=CITED_VALUES,
        derived=DERIVED_QUANTITIES,
        bundle=None,
        baseline=BASELINE_UNACCOUNTED,
    )


def audit(path=None):
    """Audit the prose, with generated blocks removed first."""
    target = path or MANUSCRIPT
    text = target.read_text(encoding="utf-8")
    spans = _generated_spans(text)
    # blank the generated regions, preserving offsets so reported line numbers stay true
    chars = list(text)
    for a, b in spans:
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = " "
    stripped = "".join(chars)

    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(stripped)
        tmp = Path(fh.name)
    try:
        report = NA.audit(_spec(tmp), tmp)
    finally:
        tmp.unlink(missing_ok=True)
    report["paper"] = "Paper 3 prose numeral audit"
    report["n_generated_blocks_excluded"] = len(spans)
    return report


def render(report):
    return NA.render(report)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    report = audit()
    if "--json" in argv:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
        print(f"\n({report['n_generated_blocks_excluded']} generated blocks excluded; "
              f"their numbers are checked by `paper3.build verify`)")
    n = len(report["unaccounted"])
    if n > BASELINE_UNACCOUNTED:
        print(f"\nFAIL: {n} unaccounted exceeds the baseline of {BASELINE_UNACCOUNTED}.",
              file=sys.stderr)
        return 1
    if n < BASELINE_UNACCOUNTED:
        print(f"\nNOTE: {n} unaccounted, below the baseline of {BASELINE_UNACCOUNTED} — "
              f"lower BASELINE_UNACCOUNTED to {n}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
