"""Generated named-shot evidence scorecard (Paper 3 review MC17).

WHY THIS EXISTS. The scorecard was the one asserted result in a paper about provenance that the
provenance machinery did not itself cover: Table 6 was maintained by hand. Two consequences showed
up as soon as it was regenerated from producers. First, a stage's evidence STATUS was an author's
word rather than a derived fact. Second, one row carried a quantitative claim -- an "approximately
6.6 % ramp shift" -- that **no producer in the repository emits**, which is precisely the defect
class this paper argues against.

WHAT IS DERIVED AND WHAT IS DECLARED. The chain of stages and the component selected at each stage
are DECLARED here, because they are a configuration choice, not a fact about the world. Everything
else is derived: a stage's evidence status comes from the selected component's SCOPED EVIDENCE
VECTOR (`evidence_graph.component_evidence_vector`), and its numbers come from named producers that
are executed, not transcribed. A stage with no registered component is marked observed, specified or
open, and a number with no producer is reported as UNBACKED rather than printed.

    python -m puckworks.paper3.named_shot_scorecard            # markdown table
    python -m puckworks.paper3.named_shot_scorecard --json     # machine-readable record
"""
from __future__ import annotations

import dataclasses as dc
import json

#: The illustrative configuration. Declared, not inferred: a named shot is a CHOICE of components
#: and inputs, which is the paper's whole point about what a simulation is.
NAMED_SHOT = {
    "fixture": "de1_fixtureA",
    "dose_g": 20.0,
    "beverage_g": 40.0,
    "grinder_dial": 1.7,
    "temperature_range_C": (80.0, 98.0),
    "dial_is_portable": False,          # ledger A9/G5 -- dial spaces are grinder-specific
}

#: Evidence relation -> the scorecard status it licenses. This is a RENAMING for a lay reader, not a
#: ranking: the relations remain non-ordinal (see evidence_graph, where the ordering was removed).
RELATION_STATUS = {
    "controlled_independent": "independent",
    "within_campaign_held_out": "held-out (within campaign)",
    "post_fit_reconstruction": "reconstructed",
    "source_curve_reproduction": "reconstructed (source curve)",
    "code_verification": "verified (code only)",
    "sign_or_compatibility": "compatibility check",
    "qualitative_capacity": "capacity only",
    "exploratory_synthesis": "exploratory",
    "proposed_experiment": "open",
}

#: Statuses available to stages that carry no registered component.
NON_COMPONENT_STATUS = ("specified", "observed", "open")


@dc.dataclass(frozen=True)
class StageSelection:
    """A declared choice at one stage of the named shot."""
    stage: str
    label: str
    component: str | None          # registry id, or None
    dataset: str | None            # manifest id, or None
    declared_status: str | None    # only for stages with no component
    caveat: str
    numbers: tuple = ()            # (name, producer_ref) pairs, executed at render time
    unbacked_numbers: tuple = ()   # claims previously printed with NO producer


def _fo_f_audit():
    from puckworks.models.wadsworth2026 import inertial as I
    r = I.de1_fixtureA_audit()
    return {
        "permeability_k_m2": r["k_m2"],
        "bed_length_L_m": r["L_m"],
        "cross_section_A_m2": r["A_m2"],
        "peak_superficial_q_m_s": r["q_peak_m_s"],
        "Fo_F_max_exp_closure": r["Fo_F_max_exp"],
        "Fo_F_max_zhou_closure": r["Fo_F_max_zhou"],
    }


#: Producer registry for the scorecard's numbers. Every entry is EXECUTED; nothing is transcribed.
NUMBER_PRODUCERS = {
    "puckworks.models.wadsworth2026.inertial.de1_fixtureA_audit": _fo_f_audit,
}


CHAIN = (
    StageSelection(
        stage="(configuration)", label="Named preparation",
        component=None, dataset=None, declared_status="specified",
        caveat="The grinder dial is not a portable physical coordinate; until a grinder-specific "
               "particle-size adapter exists, the cross-grinder mapping stays open rather than "
               "being treated as matched by dial number."),
    StageSelection(
        stage="machine", label="Machine boundary",
        component=None, dataset="de1_fixtureA", declared_status="observed",
        caveat="The exact pressure-node identity of the recorded trace is OPEN (basket gauge vs "
               "line), and node identity is documented in prose but is not a typed contract field, "
               "so a node substitution would be type-valid."),
    StageSelection(
        stage="infiltration", label="Infiltration",
        component="foster2025.infiltration", dataset="de1_fixtureA", declared_status=None,
        caveat="Same-shot compatibility check across a predeclared porosity bracket, NOT an "
               "independent prediction: the same shot supplies the pressure trace, the fitted "
               "permeability and the evaluation."),
    StageSelection(
        stage="packing", label="Packing / permeability",
        component="wadsworth2026.permeability", dataset="de1_fixtureA", declared_status=None,
        caveat="Literature prior plus a per-shot fitted fixture multiplier; not an independent "
               "permeability prediction, and outlet/screen resistance may be absorbed into it."),
    StageSelection(
        stage="flow", label="Flow law",
        component="wadsworth2026.inertial", dataset="de1_fixtureA", declared_status=None,
        caveat="The two Forchheimer numbers are the SAME shot under two k_I closures -- a closure "
               "spread, not a measurement range -- and k_I is extrapolated from a ceramics fit, "
               "never coffee-calibrated. This is a model-derived regime flag, not empirical "
               "validation of inertial espresso flow.",
        numbers=(("de1 fixture-A inertial audit",
                  "puckworks.models.wadsworth2026.inertial.de1_fixtureA_audit"),)),
    StageSelection(
        stage="bed_dynamics", label="Bed dynamics",
        component="waszkiewicz2025.poroelastic", dataset=None, declared_status=None,
        caveat="No direct porosity or strain measurement exists on the named shot; the branch is "
               "selected by configuration, and a different selection changes the status."),
    StageSelection(
        stage="extraction", label="Aggregate extraction",
        component="cameron2020.extraction_bdf", dataset=None, declared_status=None,
        caveat="Absolute extraction yield reads low against independent literature brackets in "
               "the current comparison."),
    StageSelection(
        stage="extraction", label="Named-solute extraction",
        component="pannusch2024.solver", dataset=None, declared_status=None,
        caveat="Fitted to its source campaign; there is no independent four-solute cup for the "
               "named fixture."),
    StageSelection(
        stage="(adapter)", label="Ramp sensitivity",
        component=None, dataset=None, declared_status="open",
        caveat="The pressure-to-flow adapter audit is a verification exercise, and its sensitivity "
               "is adapter-dependent rather than an observed shot effect.",
        unbacked_numbers=(
            "A shift of 'approximately 6.6 %' was previously printed for this row. No producer in "
            "the repository emits it. It is withdrawn rather than reproduced; restoring it "
            "requires a named producer.",)),
    StageSelection(
        stage="(measurement)", label="Final exact cup",
        component=None, dataset=None, declared_status="open",
        caveat="Requires running the capstone shot, retaining fractions or the full cup, and "
               "predeclaring whether the fitted fixture multiplier may be refitted."),
)


def _status_for(sel, vectors):
    """Derive a stage's status. Authored only where no component exists."""
    if sel.component is None:
        assert sel.declared_status in NON_COMPONENT_STATUS, sel.declared_status
        return sel.declared_status, ()
    vec = vectors.get(sel.component, ())
    relations = []
    for s in vec:
        if s.relation not in relations:
            relations.append(s.relation)
    if not relations:
        return "open", ()
    statuses = [RELATION_STATUS[r] for r in relations]
    return " + ".join(dict.fromkeys(statuses)), tuple(
        dict(relation=s.relation, scope=s.scope, gate=s.gate, outcome=s.outcome) for s in vec)


def scorecard():
    """Generate the named-shot scorecard. Statuses are DERIVED from evidence vectors; numbers are
    EXECUTED from producers; unbacked claims are reported as such."""
    from puckworks.paper3 import evidence_graph as EG

    vectors = EG.evidence_vectors()
    rows, unbacked = [], []
    for sel in CHAIN:
        status, evidence = _status_for(sel, vectors)
        numbers = {}
        for name, ref in sel.numbers:
            fn = NUMBER_PRODUCERS.get(ref)
            if fn is None:
                raise KeyError("no producer registered for %r" % ref)
            numbers[name] = dict(producer=ref, values=fn())
        rows.append(dict(
            stage=sel.stage, label=sel.label, component=sel.component, dataset=sel.dataset,
            status=status, evidence=evidence, caveat=sel.caveat, numbers=numbers,
            status_is_derived=sel.component is not None,
            unbacked_numbers=list(sel.unbacked_numbers)))
        unbacked.extend(sel.unbacked_numbers)

    open_stages = [r["label"] for r in rows if r["status"] == "open"]
    return dict(
        configuration=dict(NAMED_SHOT),
        n_stages=len(rows),
        n_derived_statuses=sum(1 for r in rows if r["status_is_derived"]),
        n_open_stages=len(open_stages),
        open_stages=open_stages,
        unbacked_claims=unbacked,
        rows=rows,
        note=("The chain and the component selected at each stage are DECLARED (a configuration is "
              "a choice). Every evidence status on a stage that has a registered component is "
              "DERIVED from that component's scoped evidence vector, and every number is executed "
              "from a named producer. The scorecard is an evidentiary ledger, not a prediction: it "
              "ends in 'measurement required', not a synthetic cup."))


def render(result=None):
    r = result or scorecard()
    L = ["**Table 6. Named-shot evidence scorecard (generated).** Statuses on stages with a "
         "registered component are derived from that component's scoped evidence vector; numbers "
         "are executed from named producers. %d of %d statuses are derived; %d stages remain open."
         % (r["n_derived_statuses"], r["n_stages"], r["n_open_stages"]), "",
         "| Stage | Selected component or input | Evidence status | Load-bearing caveat |",
         "|---|---|---|---|"]
    for row in r["rows"]:
        sel = row["component"] or row["dataset"] or "—"
        status = row["status"] + ("" if row["status_is_derived"] else " *(declared)*")
        caveat = row["caveat"]
        for u in row["unbacked_numbers"]:
            caveat += " **WITHDRAWN:** " + u
        if row["numbers"]:
            bits = []
            for name, blk in row["numbers"].items():
                vals = blk["values"]
                bits.append("Fo_F %.2f (exp) to %.1f (Zhou); k = %.2e m²; peak q = %.2e m s⁻¹"
                            % (vals["Fo_F_max_exp_closure"], vals["Fo_F_max_zhou_closure"],
                               vals["permeability_k_m2"], vals["peak_superficial_q_m_s"]))
            caveat = " ".join(bits) + ". " + caveat
        L.append("| %s | `%s` | %s | %s |" % (row["label"], sel, status, caveat))
    if r["unbacked_claims"]:
        L += ["", "**Claims withdrawn for want of a producer.** " + " ".join(r["unbacked_claims"])]
    return "\n".join(L)


import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"
_BEGIN = "<!-- scorecard:begin -->"
_END = "<!-- scorecard:end -->"


def _block():
    return _BEGIN + "\n" + render() + "\n" + _END


def write():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    if _BEGIN in text and _END in text:
        pre = text.split(_BEGIN)[0]
        post = text.split(_END, 1)[1]
        MANUSCRIPT.write_text(pre + _block() + post, encoding="utf-8")
        return MANUSCRIPT
    raise SystemExit("scorecard markers not found in the manuscript")


def verify():
    """Return '' when the manuscript's scorecard matches the generated one."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    if _BEGIN not in text or _END not in text:
        return "scorecard is not generated (missing markers) -- run --write"
    cur = _BEGIN + text.split(_BEGIN, 1)[1].split(_END, 1)[0] + _END
    return "" if cur.strip() == _block().strip() else "scorecard is stale -- run --write"


if __name__ == "__main__":                                    # pragma: no cover
    import sys
    if "--write" in sys.argv:
        print("wrote", write())
    elif "--verify" in sys.argv:
        problem = verify()
        print(problem or "scorecard is current")
        sys.exit(1 if problem else 0)
    else:
        res = scorecard()
        print(json.dumps(res, indent=1, default=str) if "--json" in sys.argv else render(res))
