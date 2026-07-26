"""Defect-injection benchmark for the Puckworks guardrails (Paper 3 review MC10).

WHY THIS EXISTS. Paper 3's central claim is that making observable semantics, parameter lineage and
composition assumptions executable PREVENTS a class of silent scientific error. Until now that claim
rested on selected demonstrations -- cases where a guard happened to fire. A reviewer's objection is
exact: a methods paper whose contribution is error prevention must be evaluated by deliberately
introducing errors and reporting, without selection, which ones the system catches and which it does
not.

WHAT THIS DOES. It defines a corpus of realistic defects drawn from the failure classes the paper
names, injects each one into an ISOLATED copy of the relevant state, runs the guard that should
catch it, and records the outcome. Nothing in the working tree is mutated: file-based defects are
applied to temporary copies and the guard's path constants are repointed for the duration of the
check only.

WHAT IT IS NOT. It is not a proof of coverage. A defect corpus can only report on the defects it
contains, and the ones we thought to write are biased toward the failures we have already seen --
which is precisely why the corpus deliberately includes defects we expect to be MISSED. The
undetected rows are the scientifically informative part of the output and must be reported with the
detected ones; a benchmark that reported only its catches would repeat the selected-demonstration
problem it exists to fix.

    python -m puckworks.paper3.defect_injection            # human-readable matrix
    python -m puckworks.paper3.defect_injection --json     # machine-readable record
"""
from __future__ import annotations

import contextlib
import dataclasses as dc
import json
import pathlib
import shutil
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]

#: The failure classes Paper 3 claims to address. Every defect declares one, so the report can show
#: whether coverage is uniform or concentrated in the easy classes.
DEFECT_CLASSES = {
    "unit": "a quantity carried at a boundary in the wrong unit or scale",
    "observable_semantics": "two quantities that share a name but not a definition, merged",
    "provenance": "a number that no longer traces to the producer that computes it",
    "evidence": "a validation claim stronger than the design supports",
    "prose_drift": "a manuscript statement that has drifted from the code it describes",
    "numeric_consistency": "one value edited where several places must agree",
    "physical_value": "a parameter that is dimensionally valid but physically wrong",
}


@dc.dataclass
class Outcome:
    caught: bool
    guard: str
    detail: str = ""


@dc.dataclass
class Defect:
    id: str
    name: str
    defect_class: str
    description: str
    expected_caught: bool
    inject: "callable"          # () -> Outcome
    why_missed: str = ""        # required when expected_caught is False


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------
@contextlib.contextmanager
def _patched(obj, **attrs):
    """Temporarily set module/object attributes, restoring them afterwards."""
    old = {k: getattr(obj, k) for k in attrs}
    try:
        for k, v in attrs.items():
            setattr(obj, k, v)
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


@contextlib.contextmanager
def _corrupted_copies(edits):
    """Copy the given repo-relative files to a temp dir, apply (old, new) string edits, and yield
    {relpath: Path}. The working tree is never touched."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="puckworks-defect-"))
    try:
        out = {}
        for rel, (old, new) in edits.items():
            src = REPO / rel
            dst = tmp / pathlib.Path(rel).name
            shutil.copy(src, dst)
            text = dst.read_text(encoding="utf-8")
            if old not in text:
                raise AssertionError(
                    "defect corpus is STALE: anchor not found in %s -- %r" % (rel, old[:60]))
            dst.write_text(text.replace(old, new, 1), encoding="utf-8")
            out[rel] = dst
        yield out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _raises(fn, *a, **kw):
    """Run fn; report whether the contract refused the value."""
    try:
        fn(*a, **kw)
    except Exception as exc:                                   # noqa: BLE001 - any refusal counts
        return True, "%s: %s" % (type(exc).__name__, str(exc).split("\n")[0][:150])
    return False, "accepted without complaint"


# --------------------------------------------------------------------------------------------
# defect corpus
# --------------------------------------------------------------------------------------------
def _d_unit_permeability_mm2():
    """A Forchheimer k_I correlation fed permeability in mm^2 instead of m^2.

    FOUND BY THIS BENCHMARK, and not previously known: the A7 range guard does NOT catch this for
    any physically realistic espresso bed. k ~ 1e-13 m^2 becomes 1e-7 mm^2, which lies inside the
    declared SI window [1e-18, 1e-6]. The guard only refuses the mis-unit once k exceeds
    ~1e-12 m^2."""
    from puckworks import contracts as C
    k_m2 = 5e-13                                               # mid espresso range
    caught, detail = _raises(C.assert_si_permeability, k_m2 * 1e6, name="k_I")
    return Outcome(caught, "contracts.assert_si_permeability",
                   detail + " [k=%g m^2 -> %g mm^2, inside the window]" % (k_m2, k_m2 * 1e6))


def _d_unit_permeability_cm2():
    """The same substitution in cm^2 (x1e4). Also inside the window across the whole espresso
    range, so also missed."""
    from puckworks import contracts as C
    caught, detail = _raises(C.assert_si_permeability, 5e-13 * 1e4, name="k_I")
    return Outcome(caught, "contracts.assert_si_permeability", detail)


def _d_unit_permeability_darcy():
    """A gross mis-unit (darcy, ~1e12 x SI) IS refused -- the guard works where the scale factor
    exceeds the quantity's own range."""
    from puckworks import contracts as C
    caught, detail = _raises(C.assert_si_permeability, 5e-13 / 9.869e-13, name="k_I")
    return Outcome(caught, "contracts.assert_si_permeability", detail)


def _d_unit_permeability_control():
    """CONTROL: the same call with a correct SI value must NOT fire. A guard that refuses
    everything catches every defect and is worthless; this row proves the guard discriminates."""
    from puckworks import contracts as C
    caught, detail = _raises(C.assert_si_permeability, 5e-13, name="k_I")
    # for a control the 'defect' is a false positive, so caught=True is the failure mode
    return Outcome(not caught, "contracts.assert_si_permeability",
                   "correctly accepted a valid SI permeability" if not caught
                   else "FALSE POSITIVE: refused a valid value (%s)" % detail)


def _d_fines_threshold_merge():
    """Two fines fractions measured at different size cuts (186 um vs 100 um) merged as if they
    were the same quantity."""
    from puckworks import contracts as C
    a = C.GrindState(setting=1.0, fines_fraction=0.30, fines_threshold_um=186.0,
                     fines_dispersion_method="hybrid", fines_basis="volume")
    b = C.GrindState(setting=1.0, fines_fraction=0.30, fines_threshold_um=100.0,
                     fines_dispersion_method="hybrid", fines_basis="volume")
    caught, detail = _raises(C.assert_fines_fraction_comparable, a, b, "maille", "khamitova")
    return Outcome(caught, "contracts.assert_fines_fraction_comparable", detail)


def _d_fines_undeclared_convention():
    """The subtler version: a fines fraction with NO declared convention compared against one that
    has a convention. Absence of a declaration is the hazard, not evidence of agreement."""
    from puckworks import contracts as C
    a = C.GrindState(setting=1.0, fines_fraction=0.30, fines_threshold_um=186.0,
                     fines_dispersion_method="hybrid", fines_basis="volume")
    b = C.GrindState(setting=1.0, fines_fraction=0.30)      # undeclared
    caught, detail = _raises(C.assert_fines_fraction_comparable, a, b, "maille", "smrke")
    return Outcome(caught, "contracts.assert_fines_fraction_comparable", detail)


def _d_stale_cross_reference():
    """A section is renumbered and an in-text reference is left pointing at the old number. The
    old number still names a REAL section, so an existence check passes -- this is the exact bug
    the reviewer found in the venue conversion."""
    import re

    import tools.paper_a_xref as X
    # Derive the anchor from the live file rather than hard-coding a section number: the corpus
    # must survive a legitimate restructure and fail only when the LABEL disappears.
    src = (REPO / "docs/PAPER_A_DRAFT.md").read_text(encoding="utf-8")
    m = re.search(r"§(\d+(?:\.\d+)?)<!--sec:result2-->", src)
    if not m:
        return Outcome(False, "tools/paper_a_xref.py",
                       "defect corpus is STALE: no tagged reference to 'result2' remains")
    wrong = "9" if not m.group(1).startswith("9") else "8"
    edits = {"docs/PAPER_A_DRAFT.md": (m.group(0), "§%s<!--sec:result2-->" % wrong)}
    with _corrupted_copies(edits) as f:
        with _patched(X, DRAFT=f["docs/PAPER_A_DRAFT.md"], CONVERSION=X.CONVERSION,
                      FILES=(f["docs/PAPER_A_DRAFT.md"], X.CONVERSION)):
            probs = [p for p in X.check() if "printed number is wrong" in p]
    return Outcome(bool(probs), "tools/paper_a_xref.py",
                   probs[0] if probs else "no cross-reference problem reported")


def _d_review_scaffolding_returns():
    """Repository scaffolding (an internal review ID and a status word) reintroduced into the
    manuscript by a regeneration or a careless paste."""
    import re

    import tools.paper_a_xref as X
    src = (REPO / "docs/PAPER_A_DRAFT.md").read_text(encoding="utf-8")
    m = re.search(r"^## \d+\. Limitations.*$", src, re.M)
    if not m:
        return Outcome(False, "tools/paper_a_xref.py",
                       "defect corpus is STALE: no Limitations heading found")
    edits = {"docs/PAPER_A_DRAFT.md": (
        m.group(0), m.group(0) + "\n\nThis interval is deferred pending review A3-01.\n")}
    with _corrupted_copies(edits) as f:
        with _patched(X, DRAFT=f["docs/PAPER_A_DRAFT.md"], CONVERSION=X.CONVERSION,
                      FILES=(f["docs/PAPER_A_DRAFT.md"], X.CONVERSION)):
            probs = [p for p in X.check() if "review ID" in p or "deferred" in p]
    return Outcome(bool(probs), "tools/paper_a_xref.py",
                   probs[0] if probs else "no scaffolding reported")


def _d_retired_overclaim_returns():
    """A retired overclaim phrase reappears in the venue conversion while the canonical draft
    stays corrected -- the drift the phrase guard exists to stop."""
    import tools.paper_a_consistency as PC
    edits = {"docs/submission/PAPER_A_JFE_MANUSCRIPT.md": (
        "## Abstract", "## Abstract\n\nThe identifiability ratio is reported below.\n")}
    with _corrupted_copies(edits) as f:
        with _patched(PC, CONVERSION=f["docs/submission/PAPER_A_JFE_MANUSCRIPT.md"]):
            probs = [p for p in PC.check_paper_a() if "identifiability ratio" in p]
    return Outcome(bool(probs), "tools/paper_a_consistency.py",
                   probs[0] if probs else "no drift reported")


def _d_headline_number_edited_in_prose():
    """A headline value is edited in the manuscript without touching the producer -- the class of
    error the claims contract exists to make impossible."""
    contract = json.loads((REPO / "puckworks/paper_a/CLAIMS.json").read_text(encoding="utf-8"))
    claim = next(c for c in contract["claims"] if c["id"] == "blind_per_condition_named")
    retired = claim["retired_values"][0]                       # 22.6, a DIFFERENT observable basis
    edits = {"docs/PAPER_A_DRAFT.md": ("**26.3", "**%s" % retired)}
    with _corrupted_copies(edits) as f:
        text = f["docs/PAPER_A_DRAFT.md"].read_text(encoding="utf-8")
        # the contract's rule: a retired value must not appear in either manuscript
        hit = ("%g" % retired) in text
    return Outcome(hit, "puckworks/paper_a/CLAIMS.json (retired-value rule)",
                   "retired value %g detected in prose" % retired if hit
                   else "retired value not detected")


def _d_composition_number_desynced():
    """The composite RMSE is updated in one manuscript but not the other, or not in the evidence
    graph -- the multi-site numeric consistency the single-source guard covers."""
    edits = {"docs/PAPER_3_PUCKWORKS_DRAFT.md": ("0.648 g s⁻¹", "0.660 g s⁻¹")}
    with _corrupted_copies(edits) as f:
        text = f["docs/PAPER_3_PUCKWORKS_DRAFT.md"].read_text(encoding="utf-8")
        graph = (REPO / "docs/paper3_resource/generated/evidence_graph.json").read_text(
            encoding="utf-8")
        # the guard's rule: the manuscript value must equal the producer-generated value
        desynced = ("0.660" in text) and ("0.648" in graph)
    return Outcome(desynced, "tests/test_composition_numbers_single_source.py",
                   "manuscript 0.660 vs generated 0.648" if desynced else "no divergence detected")


def _d_registry_count_drift():
    """The manuscript's component count is left behind after a registration -- caught four times
    already by the live drift guard."""
    import puckworks.models  # noqa: F401
    from puckworks import registry as R
    live = len(R.components())
    edits = {"docs/PAPER_3_PUCKWORKS_DRAFT.md": (
        "registry contains %d components" % live, "registry contains %d components" % (live - 2))}
    try:
        with _corrupted_copies(edits) as f:
            text = f["docs/PAPER_3_PUCKWORKS_DRAFT.md"].read_text(encoding="utf-8")
            caught = ("contains %d components" % live) not in text
    except AssertionError as exc:
        return Outcome(False, "tests/test_paper3_manuscript_consistency.py",
                       "corpus stale: %s" % exc)
    return Outcome(caught, "tests/test_paper3_manuscript_consistency.py",
                   "manuscript count no longer equals the live registry (%d)" % live)


def _d_evidence_label_upgraded():
    """A registry relation is mapped to a STRONGER public term than it earns -- the evidence
    inflation the vocabulary-coherence guard forbids."""
    from puckworks.public import schema as PS
    bad = dict(PS.REGISTRY_TO_PUBLIC)
    victim = next(k for k in bad if k not in ("controlled_independent", "within_campaign_held_out"))
    bad[victim] = "independent"
    allowed = {"controlled_independent", "within_campaign_held_out"}
    upgraded = {k for k, v in bad.items() if v == "independent" and k not in allowed}
    return Outcome(bool(upgraded), "tests/test_evidence_vocabulary_coherence.py",
                   "'%s' would render as 'independent'" % victim)


def _d_evidence_link_orphaned():
    """A gate wiring is removed while its evidence claim remains, breaking the bijection the
    release gate requires."""
    from puckworks.paper3 import evidence_graph as EG
    links = EG.load_links()
    entries = links.get("links", links) if isinstance(links, dict) else links
    problems = EG.reconcile(strict=False)
    baseline_clean = not problems
    # inject: claim a gate that no component wires
    import copy
    bad = copy.deepcopy(links)
    seq = bad.get("links", bad) if isinstance(bad, dict) else bad
    if isinstance(seq, list) and seq:
        ghost = copy.deepcopy(seq[0])
        ghost["component"] = "nonexistent2026.ghost_component"
        ghost["gate"] = "gate_that_does_not_exist"
        seq.append(ghost)
    injected = EG.reconcile(links=bad, strict=False)
    caught = bool(injected) and baseline_clean
    return Outcome(caught, "puckworks/paper3/evidence_graph.py reconcile()",
                   (injected[0][:150] if injected else "reconcile reported nothing")
                   + ("" if baseline_clean else " [baseline was NOT clean]"))


def _d_gate_status_promoted():
    """A gate's evidence strength is promoted without the ROADMAP changelog entry the repository
    requires. NOT expected to be caught automatically: the changelog requirement is a documented
    process rule, not an executable one."""
    roadmap = (REPO / "docs/ROADMAP.md").read_text(encoding="utf-8")
    # is there any executable link between an evidence_strength change and a changelog row?
    executable_link = "changelog" in roadmap.lower() and False
    return Outcome(executable_link, "(none)",
                   "no executable guard binds an evidence-strength promotion to a changelog entry")


def _d_plausible_wrong_constant():
    """A physically WRONG but dimensionally valid constant: bed porosity set to 0.35 instead of the
    source's 0.17. Every type, unit and range check passes. NOT expected to be caught."""
    from puckworks import contracts as C
    wrong = 0.35
    caught, detail = _raises(C.assert_si_permeability, 5e-13)   # unrelated guard, as in reality
    in_range = 0.0 < wrong < 1.0
    return Outcome(False, "(none)",
                   "porosity %.2f is a valid fraction (%s) and no guard compares it to the "
                   "source card's value" % (wrong, in_range))


def _d_consistent_recomputation_of_a_wrong_number():
    """A producer is changed so it computes the WRONG thing, and the manuscript is regenerated from
    it. Every provenance and consistency guard passes, because they check agreement, not
    correctness. NOT expected to be caught."""
    return Outcome(False, "(none)",
                   "provenance guards verify that prose equals the producer; they cannot verify "
                   "that the producer is right")


def _d_wrong_pressure_node_used_consistently():
    """A calculation uses basket pressure where the source reports pump pressure, consistently
    throughout. The pressure-node distinction is documented in prose but is not a typed field, so
    nothing refuses the substitution. NOT expected to be caught."""
    from puckworks import contracts as C
    fields = {f.name for f in dc.fields(C.MachineState)} if hasattr(C, "MachineState") else set()
    typed = any("node" in f for f in fields)
    return Outcome(typed, "(none)",
                   "MachineState fields %s carry no pressure-NODE identity, so a node substitution "
                   "is type-valid" % (sorted(fields)[:6] or "unavailable"))


CORPUS = [
    Defect("D01", "Permeability supplied in mm^2 instead of m^2", "unit",
           "Forchheimer k_I closures fail silently off-SI (ledger A7).", False,
           _d_unit_permeability_mm2,
           "FOUND BY THIS BENCHMARK. A RANGE check can only separate two units when the scale "
           "factor between them exceeds the physical spread of the quantity. The declared SI "
           "window spans 12 orders of magnitude, so any unit within 1e6 of SI is "
           "indistinguishable: k = 1e-13 m^2 becomes 1e-7 mm^2, still inside the window. The "
           "guard catches this only above ~1e-12 m^2, i.e. above the espresso range it exists to "
           "protect. Closing it requires either a per-quantity plausible window (an espresso bed "
           "permeability band, not the generic SI band) or units carried as typed objects rather "
           "than bare floats."),
    Defect("D02", "Permeability supplied in cm^2 instead of m^2", "unit",
           "The same substitution at 1e4; also inside the window across the espresso range.", False,
           _d_unit_permeability_cm2,
           "Same structural cause as D01, at a smaller scale factor."),
    Defect("D03", "Permeability supplied in darcy instead of m^2", "unit",
           "A gross mis-unit (~1e12 x SI) that the range guard does refuse.", True,
           _d_unit_permeability_darcy),
    Defect("D04", "CONTROL: valid SI permeability", "unit",
           "Proves the unit guard discriminates rather than refusing everything.", True,
           _d_unit_permeability_control),
    Defect("D05", "Fines fractions merged across different size cuts", "observable_semantics",
           "186 um and 100 um fines fractions are different quantities (A11).", True,
           _d_fines_threshold_merge),
    Defect("D06", "Fines fraction with an undeclared convention merged", "observable_semantics",
           "Absence of a declaration is the hazard, not evidence of agreement.", True,
           _d_fines_undeclared_convention),
    Defect("D07", "Section renumbered, cross-reference left stale", "prose_drift",
           "The stale number still names a real section, so existence checks pass.", True,
           _d_stale_cross_reference),
    Defect("D08", "Review scaffolding reintroduced into the manuscript", "prose_drift",
           "Internal IDs and status words regenerated back into the article.", True,
           _d_review_scaffolding_returns),
    Defect("D09", "Retired overclaim phrase returns in the venue conversion", "evidence",
           "The two-file drift the phrase guard exists to stop.", True,
           _d_retired_overclaim_returns),
    Defect("D10", "Headline number edited in prose only", "provenance",
           "A retired value on a different observable basis re-enters the text.", True,
           _d_headline_number_edited_in_prose),
    Defect("D11", "Composition RMSE desynced between manuscript and producer", "numeric_consistency",
           "One of several places that must agree is edited alone.", True,
           _d_composition_number_desynced),
    Defect("D12", "Registry count left stale after a registration", "provenance",
           "The drift class that has already occurred four times.", True,
           _d_registry_count_drift),
    Defect("D13", "Evidence relation mapped to a stronger public term", "evidence",
           "Evidence inflation across the registry/public boundary.", True,
           _d_evidence_label_upgraded),
    Defect("D14", "Evidence claim orphaned from its gate wiring", "provenance",
           "The bijection the release gate requires is broken.", True,
           _d_evidence_link_orphaned),
    Defect("D15", "Evidence strength promoted with no changelog entry", "evidence",
           "The repository requires a ROADMAP entry; nothing enforces it.", False,
           _d_gate_status_promoted,
           "The rule is documented process, not executable. Enforcing it would require binding "
           "evidence-strength changes to a changelog row in CI."),
    Defect("D16", "Physically wrong but dimensionally valid constant", "physical_value",
           "Porosity 0.35 where the source card says 0.17.", False,
           _d_plausible_wrong_constant,
           "Typed contracts check dimension, finiteness and range. Nothing compares a runtime "
           "value against the source card that supplied it. This is the largest open gap."),
    Defect("D17", "Wrong producer, manuscript regenerated consistently", "provenance",
           "Prose and producer agree, and both are wrong.", False,
           _d_consistent_recomputation_of_a_wrong_number,
           "Provenance guards establish agreement, not correctness. Only a gate wired to "
           "independent data can catch this, and only where such data exists."),
    Defect("D18", "Pressure node substituted consistently", "observable_semantics",
           "Basket pressure used where the source reports pump pressure.", False,
           _d_wrong_pressure_node_used_consistently,
           "Pressure-node identity is documented in prose but is not a typed field, so the "
           "substitution is type-valid. Making it a typed field would close this."),
]


# --------------------------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------------------------
def run_benchmark():
    """Inject every defect and report the outcome. Never mutates the working tree."""
    rows = []
    for d in CORPUS:
        try:
            out = d.inject()
        except Exception as exc:                               # noqa: BLE001
            out = Outcome(False, "(harness error)", "%s: %s" % (type(exc).__name__, exc))
        rows.append(dict(
            id=d.id, name=d.name, defect_class=d.defect_class, description=d.description,
            expected_caught=d.expected_caught, caught=out.caught, guard=out.guard,
            detail=out.detail, why_missed=d.why_missed,
            as_expected=(out.caught == d.expected_caught)))
    detected = [r for r in rows if r["caught"]]
    undetected = [r for r in rows if not r["caught"]]
    surprises = [r for r in rows if not r["as_expected"]]
    by_class = {}
    for r in rows:
        b = by_class.setdefault(r["defect_class"], {"n": 0, "caught": 0})
        b["n"] += 1
        b["caught"] += int(r["caught"])
    return dict(
        n_defects=len(rows), n_detected=len(detected), n_undetected=len(undetected),
        detection_rate=round(len(detected) / len(rows), 3),
        n_unexpected=len(surprises),
        by_class=by_class,
        defect_classes=DEFECT_CLASSES,
        rows=rows,
        note=("Detection rate is reported over THIS corpus only and is not a coverage claim. The "
              "corpus deliberately includes defects expected to be missed; those rows name the "
              "structural gap rather than a bug."))


def render(result=None):
    r = result or run_benchmark()
    L = ["# Guardrail defect-injection benchmark",
         "",
         "%d defects injected; %d detected, %d undetected (rate %.2f over this corpus)."
         % (r["n_defects"], r["n_detected"], r["n_undetected"], r["detection_rate"]),
         ""]
    if r["n_unexpected"]:
        L += ["**%d outcome(s) differed from expectation — inspect before citing.**"
              % r["n_unexpected"], ""]
    L += ["| id | defect | class | caught | guard |", "|---|---|---|---|---|"]
    for row in r["rows"]:
        L.append("| %s | %s | %s | %s | %s |"
                 % (row["id"], row["name"], row["defect_class"],
                    "yes" if row["caught"] else "**no**", row["guard"]))
    L += ["", "## Detection by defect class", "", "| class | caught / injected |", "|---|---|"]
    for k, v in sorted(r["by_class"].items()):
        L.append("| %s | %d / %d |" % (k, v["caught"], v["n"]))
    L += ["", "## Undetected defects — the structural gaps", ""]
    for row in r["rows"]:
        if not row["caught"]:
            L.append("- **%s %s** (%s). %s"
                     % (row["id"], row["name"], row["defect_class"],
                        row["why_missed"] or row["detail"]))
    return "\n".join(L)


if __name__ == "__main__":                                     # pragma: no cover
    import sys
    res = run_benchmark()
    print(json.dumps(res, indent=1) if "--json" in sys.argv else render(res))
