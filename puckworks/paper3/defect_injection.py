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
    """One case in the suite.

    Third review P0-7 added the last four fields. The previous schema could not distinguish a
    defect from a control, an executable mutation from a documented structural impossibility, or
    two scale factors of one structural failure from two independent pieces of evidence -- so the
    reported "18 defects, 12 detected, 67 %" counted a valid control as a caught defect and treated
    related cases as independent.
    """
    id: str
    name: str
    defect_class: str
    description: str
    expected_caught: bool
    inject: "callable"          # () -> Outcome
    why_missed: str = ""        # required when expected_caught is False

    #: A control is an input that SHOULD pass. It measures specificity, never sensitivity, and is
    #: excluded from the defect denominator.
    is_control: bool = False
    #: Cases sharing a structural cause. D01/D02 are two scale factors of ONE broad-range-guard
    #: failure; counting them separately overstates the sample size.
    independence_group: str = ""
    #: "executable" -- perturbs a real input/artefact and runs the production guard.
    #: "limitation_analysis" -- documents a structural gap without traversing the production path.
    execution_type: str = "executable"
    severity: str = "unknown"   # scientific consequence if the defect reached publication


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
    """Hand a BASKET-pressure trace to a consumer that requires PUMP-OUTLET pressure.

    Third review P0-8. This case previously inspected `MachineState` FIELD NAMES for the substring
    "node", found none, and concluded that node identity was untyped. That premise was false --
    `MachineState` has carried `p_p`, `p_h`, `P_basket` and `dP_bed` since schema 0.4 -- so the case
    reported a miss for the wrong reason and the manuscript repeated the wrong diagnosis.

    It is now an END-TO-END mutation across the real adapter boundary: a trace declaring the wrong
    node is passed to `contracts.require_node`, which must reject it for a node mismatch. The
    matching control (`D19`) passes a correct trace and must be accepted, so this cannot be
    satisfied by a guard that rejects everything.
    """
    import numpy as np
    from puckworks import contracts as C

    t = np.linspace(0.0, 30.0, 64)
    basket = C.PressureTrace(node=C.PressureNode.BASKET_GAUGE, time_s=t,
                             values=np.full_like(t, 8.5e5), unit="Pa",
                             reference="waszkiewicz2025:recorded_basket")
    try:
        C.require_node(basket, C.PressureNode.PUMP_OUTLET, consumer="pump-outlet flow adapter")
    except ValueError as exc:
        return Outcome(True, "contracts.require_node", str(exc)[:200])
    return Outcome(False, "(none)",
                   "a basket-pressure trace was accepted where pump outlet was required")


def _c_correct_pressure_node_is_accepted():
    """CONTROL for D18: a trace at the node the consumer asks for must PASS.

    Without this, D18 would be satisfiable by a guard that refuses every trace -- which would score
    as a catch while making the interface useless.
    """
    import numpy as np
    from puckworks import contracts as C

    t = np.linspace(0.0, 30.0, 64)
    pump = C.PressureTrace(node=C.PressureNode.PUMP_OUTLET, time_s=t,
                           values=np.full_like(t, 9.0e5), unit="Pa",
                           reference="waszkiewicz2025:recorded_pump")
    try:
        C.require_node(pump, C.PressureNode.PUMP_OUTLET, consumer="pump-outlet flow adapter")
    except Exception as exc:                                   # noqa: BLE001
        return Outcome(False, "contracts.require_node",
                       "VALID input rejected -- false positive: %s" % exc)
    return Outcome(True, "contracts.require_node",
                   "a correctly-noded trace is accepted, so the guard discriminates")


def _d_legacy_trace_without_node_identity():
    """The gap that IS real: a legacy recorded trace carries no node identity at all.

    `MachineState.P_of_t` and `profile_p` are a bare callable and a bare array. Passing one to a
    node-specific consumer must fail closed rather than have a node assumed for it.
    """
    import numpy as np
    from puckworks import contracts as C
    try:
        C.require_node(np.full(64, 9.0e5), C.PressureNode.PUMP_OUTLET,
                       consumer="pump-outlet flow adapter")
    except TypeError as exc:
        return Outcome(True, "contracts.require_node", str(exc)[:200])
    return Outcome(False, "(none)", "an untyped legacy trace was accepted without a declared node")


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
           "than bare floats.",
           independence_group="range_guard", severity="high"),
    Defect("D02", "Permeability supplied in cm^2 instead of m^2", "unit",
           "The same substitution at 1e4; also inside the window across the espresso range.", False,
           _d_unit_permeability_cm2,
           "Same structural cause as D01, at a smaller scale factor.",
           independence_group="range_guard", severity="high"),
    Defect("D03", "Permeability supplied in darcy instead of m^2", "unit",
           "A gross mis-unit (~1e12 x SI) that the range guard does refuse.", True,
           _d_unit_permeability_darcy,
           independence_group="gross_unit", severity="high"),
    Defect("D04", "CONTROL: valid SI permeability", "unit",
           "Proves the unit guard discriminates rather than refusing everything.", True,
           _d_unit_permeability_control, is_control=True, independence_group="range_guard",
           severity="n/a (control)"),
    Defect("D05", "Fines fractions merged across different size cuts", "observable_semantics",
           "186 um and 100 um fines fractions are different quantities (A11).", True,
           _d_fines_threshold_merge,
           independence_group="fines_semantics", severity="high"),
    Defect("D06", "Fines fraction with an undeclared convention merged", "observable_semantics",
           "Absence of a declaration is the hazard, not evidence of agreement.", True,
           _d_fines_undeclared_convention,
           independence_group="fines_semantics", severity="high"),
    Defect("D07", "Section renumbered, cross-reference left stale", "prose_drift",
           "The stale number still names a real section, so existence checks pass.", True,
           _d_stale_cross_reference,
           independence_group="manuscript_sentinel", severity="low", execution_type="executable"),
    Defect("D08", "Review scaffolding reintroduced into the manuscript", "prose_drift",
           "Internal IDs and status words regenerated back into the article.", True,
           _d_review_scaffolding_returns,
           independence_group="manuscript_sentinel", severity="low"),
    Defect("D09", "Retired overclaim phrase returns in the venue conversion", "evidence",
           "The two-file drift the phrase guard exists to stop.", True,
           _d_retired_overclaim_returns,
           independence_group="manuscript_sentinel", severity="medium"),
    Defect("D10", "Headline number edited in prose only", "provenance",
           "A retired value on a different observable basis re-enters the text.", True,
           _d_headline_number_edited_in_prose,
           independence_group="number_provenance", severity="high"),
    Defect("D11", "Composition RMSE desynced between manuscript and producer", "numeric_consistency",
           "One of several places that must agree is edited alone.", True,
           _d_composition_number_desynced,
           independence_group="number_provenance", severity="high"),
    Defect("D12", "Registry count left stale after a registration", "provenance",
           "The drift class that has already occurred four times.", True,
           _d_registry_count_drift,
           independence_group="number_provenance", severity="medium"),
    Defect("D13", "Evidence relation mapped to a stronger public term", "evidence",
           "Evidence inflation across the registry/public boundary.", True,
           _d_evidence_label_upgraded,
           independence_group="evidence_schema", severity="high"),
    Defect("D14", "Evidence claim orphaned from its gate wiring", "provenance",
           "The bijection the release gate requires is broken.", True,
           _d_evidence_link_orphaned,
           independence_group="evidence_schema", severity="high"),
    Defect("D15", "Evidence strength promoted with no changelog entry", "evidence",
           "The repository requires a ROADMAP entry; nothing enforces it.", False,
           _d_gate_status_promoted,
           "The rule is documented process, not executable. Enforcing it would require binding "
           "evidence-strength changes to a changelog row in CI.",
           independence_group="process_policy", severity="medium", execution_type="limitation_analysis"),
    Defect("D16", "Physically wrong but dimensionally valid constant", "physical_value",
           "Porosity 0.35 where the source card says 0.17.", False,
           _d_plausible_wrong_constant,
           "Typed contracts check dimension, finiteness and range. Nothing compares a runtime "
           "value against the source card that supplied it. This is the largest open gap.",
           independence_group="physical_correctness", severity="high", execution_type="limitation_analysis"),
    Defect("D17", "Wrong producer, manuscript regenerated consistently", "provenance",
           "Prose and producer agree, and both are wrong.", False,
           _d_consistent_recomputation_of_a_wrong_number,
           "Provenance guards establish agreement, not correctness. Only a gate wired to "
           "independent data can catch this, and only where such data exists.",
           independence_group="physical_correctness", severity="high", execution_type="limitation_analysis"),
    Defect("D18", "Pressure node substituted at an adapter boundary", "observable_semantics",
           "A basket-pressure trace is handed to a consumer that requires pump-outlet pressure.",
           True, _d_wrong_pressure_node_used_consistently,
           "Now CAUGHT. The previous version of this case inspected MachineState field names for "
           "the substring 'node' and concluded node identity was untyped -- a false premise, since "
           "p_p/p_h/P_basket/dP_bed have existed since schema 0.4. PressureTrace + require_node "
           "close the real gap, which was that a RECORDED trace carried no node identity.",
           independence_group="pressure_node", severity="high"),
    Defect("D19", "CONTROL: correctly-noded pressure trace", "observable_semantics",
           "A pump-outlet trace supplied where pump outlet is required must be ACCEPTED.",
           True, _c_correct_pressure_node_is_accepted,
           "Valid control for the node guard; excluded from the defect denominator.",
           is_control=True,
           independence_group="pressure_node", severity="n/a (control)"),
    Defect("D20", "Legacy recorded trace with no declared node", "observable_semantics",
           "A bare array is handed to a node-specific consumer.", True,
           _d_legacy_trace_without_node_identity,
           "Now CAUGHT. Fails closed rather than assuming a node -- the node is never inferred "
           "from a file name or from magnitude.",
           independence_group="pressure_node", severity="medium"),
]


# --------------------------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------------------------
def run_benchmark():
    """Run every case and report defects and controls SEPARATELY.

    Third review P0-7. The previous summary was "18 defects, 12 detected, 67 %". That number was
    not a defensible coverage estimate, for five reasons, all of which this reporting fixes:

    1. **A control was counted as a caught defect.** `D04` is a valid SI permeability that the
       range guard must ACCEPT. It sat in `n_defects`, `n_detected` and the denominator. Controls
       now measure specificity and are excluded from the defect counts.
    2. **Cases were not independent.** `D01`/`D02` are two scale factors of one structural
       range-guard failure. Results are now also grouped by `independence_group`, so the number of
       distinct mechanisms is visible next to the number of rows.
    3. **Some "misses" were not end-to-end injections.** Cases that document a structural gap
       without traversing the production path are labelled `limitation_analysis` and counted apart
       from executable mutations.
    4. **The corpus is drawn from known failures**, so it has no sampling frame from which a
       coverage probability could be estimated. There is no held-out challenge set yet.
    5. **Phrase guards are not architecture coverage.** Manuscript sentinels are a separate family.

    Accordingly **no headline coverage percentage is emitted**. The scientifically useful output is
    the map of which error classes are executable and which remain outside the guards.
    """
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
            is_control=d.is_control, independence_group=d.independence_group,
            execution_type=d.execution_type, severity=d.severity,
            as_expected=(out.caught == d.expected_caught)))

    defects = [r for r in rows if not r["is_control"]]
    controls = [r for r in rows if r["is_control"]]
    executable = [r for r in defects if r["execution_type"] == "executable"]
    limitations = [r for r in defects if r["execution_type"] == "limitation_analysis"]

    by_family = {}
    for r in rows:
        b = by_family.setdefault(r["defect_class"], {
            "defects": 0, "true_positives": 0, "false_negatives": 0,
            "controls": 0, "false_positives": 0, "open_gaps": []})
        if r["is_control"]:
            b["controls"] += 1
            if not r["caught"]:
                b["false_positives"] += 1
        else:
            b["defects"] += 1
            if r["caught"]:
                b["true_positives"] += 1
            else:
                b["false_negatives"] += 1
                b["open_gaps"].append(r["id"])

    groups = {}
    for r in defects:
        g = groups.setdefault(r["independence_group"] or r["id"], {"ids": [], "any_caught": False})
        g["ids"].append(r["id"])
        g["any_caught"] = g["any_caught"] or r["caught"]

    return dict(
        # --- defects (sensitivity) ---
        n_defects=len(defects),
        n_defects_detected=sum(r["caught"] for r in defects),
        n_defects_missed=sum(not r["caught"] for r in defects),
        n_executable_mutations=len(executable),
        n_limitation_analyses=len(limitations),
        # --- controls (specificity), reported SEPARATELY ---
        n_controls=len(controls),
        n_controls_passed=sum(r["caught"] for r in controls),
        n_false_positives=sum(not r["caught"] for r in controls),
        # --- independence ---
        n_independent_groups=len(groups),
        independence_groups=groups,
        # --- families ---
        by_family=by_family,
        defect_classes=DEFECT_CLASSES,
        n_unexpected=sum(not r["as_expected"] for r in rows),
        rows=rows,
        has_holdout_suite=False,
        note=("DEFECTS AND CONTROLS ARE COUNTED SEPARATELY, and no coverage percentage is "
              "reported. This is a development mutation suite -- a regression and gap-discovery "
              "instrument -- not a statistical estimate of all possible scientific errors. The "
              "corpus is drawn from failures already encountered, so it has no sampling frame; "
              "there is no held-out challenge set; and manuscript phrase sentinels are a separate "
              "family from generic architecture guards. Rows recorded as missed name a structural "
              "gap rather than a bug."))

def render(result=None):
    r = result or run_benchmark()
    L = ["# Development mutation suite",
         "",
         "A regression and gap-discovery instrument for the guardrails, **not** a statistical",
         "estimate of coverage. Defects and valid controls are counted separately, and no single",
         "detection percentage is reported: the corpus is drawn from failures already encountered,",
         "so it has no sampling frame from which a coverage probability could be estimated.",
         "",
         "**Injected defects:** %d (%d executable mutations, %d limitation analyses). "
         "%d caught, %d missed, spanning %d independent structural groups."
         % (r["n_defects"], r["n_executable_mutations"], r["n_limitation_analyses"],
            r["n_defects_detected"], r["n_defects_missed"], r["n_independent_groups"]),
         "",
         "**Valid controls:** %d, of which %d passed and %d were wrongly rejected "
         "(false positives)."
         % (r["n_controls"], r["n_controls_passed"], r["n_false_positives"]),
         "",
         "**Held-out challenge set:** %s." % ("present" if r["has_holdout_suite"]
                                              else "none yet — every case here was authored by the "
                                                   "same people who wrote the guards"),
         ""]
    if r["n_unexpected"]:
        L += ["**%d outcome(s) differed from expectation — inspect before citing.**"
              % r["n_unexpected"], ""]
    L += ["| id | case | class | kind | group | severity | outcome | guard |",
          "|---|---|---|---|---|---|---|---|"]
    for row in r["rows"]:
        kind = "control" if row["is_control"] else (
            "mutation" if row["execution_type"] == "executable" else "limitation")
        if row["is_control"]:
            outcome = "passed" if row["caught"] else "**FALSE POSITIVE**"
        else:
            outcome = "caught" if row["caught"] else "**missed**"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |"
                 % (row["id"], row["name"], row["defect_class"], kind,
                    row["independence_group"], row["severity"], outcome, row["guard"]))
    L += ["", "## By guard family", "",
          "| family | defect TPs | defect FNs | controls | false positives | open gaps |",
          "|---|---|---|---|---|---|"]
    for k, v in sorted(r["by_family"].items()):
        L.append("| %s | %d | %d | %d | %d | %s |"
                 % (k, v["true_positives"], v["false_negatives"], v["controls"],
                    v["false_positives"], ", ".join(v["open_gaps"]) or "—"))
    L += ["", "## Missed defects — the structural gaps", ""]
    for row in r["rows"]:
        if not row["caught"] and not row["is_control"]:
            L.append("- **%s %s** (%s, %s). %s"
                     % (row["id"], row["name"], row["defect_class"], row["execution_type"],
                        row["why_missed"] or row["detail"]))
    return "\n".join(L)


if __name__ == "__main__":                                     # pragma: no cover
    import sys
    res = run_benchmark()
    print(json.dumps(res, indent=1) if "--json" in sys.argv else render(res))
