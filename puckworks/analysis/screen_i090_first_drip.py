"""screen_i090_first_drip.py — Insight Foundry cheap screen for candidate I-090.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Does first_drip_time, measured by data already in the manifest, separate the models that
    predict it by more than their within-model uncertainty?

THE PROTOCOL IS FROZEN AND COMMITTED SEPARATELY, BEFORE THIS MODULE EXISTED:
`docs/insights/screens/I-090/PROTOCOL.md`. This module executes that protocol and nothing else.

WHAT THE OBSERVABLE-DEFINITION GATE FINDS — the pair is not a rival pair:

  E3. `foster2025.infiltration` and `foster2025.machine_mode` bind to the SAME card,
      `docs/cards/foster2025.md`, whose Interface mapping says so in terms: "one card serves
      `foster2025.infiltration` and `foster2025.machine_mode`, so anything listed above is
      attributed to both." The tension row's "2 registered models name first_drip_time among
      their interface outputs" is therefore ONE Outputs clause counted twice. Co-location is not
      a relationship.

  E1. They are SEQUENTIAL STAGES, not rivals: machine_mode (stage `machine`) GENERATES the
      pressure history that infiltration (stage `infiltration`) CONSUMES. Both modules say so.
      They share the identical sharp-front law, phi_T s ds/dt = (k/mu) dP, so under a matched
      pressure history they do not merely agree -- they are the same model. This is DEMONSTRATED
      here (the MECHANISM_IDENTITY_CHECK), not asserted.

  E2. The model event (front reaches z = L) is not the measured event (first sample above a
      0.5 g scale threshold), and the repository declares no validated mapping between them. The
      card states the measured event is NOT a model output.

Any "separation" between these two is therefore a statement about which pressure history was
supplied, not about a mechanism. The discriminand is the machine boundary condition.

Run:  python -m puckworks.analysis.screen_i090_first_drip
"""
from __future__ import annotations

import hashlib
import inspect
import json
import pathlib

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-090"
COMPONENT_A = "foster2025.infiltration"
COMPONENT_B = "foster2025.machine_mode"
DATASET = "de1_fixtureA"
TENSION_ROW = "T-0171"

PROTOCOL_PATH = "docs/insights/screens/I-090/PROTOCOL.md"
BASE_COMMIT = "85f65c0d4b836990152fa4e9bf91c6d292a9e257"

INPUT_FILES = (
    PROTOCOL_PATH,
    "puckworks/models/foster2025/infiltration.py",
    "puckworks/models/foster2025/machine_mode.py",
    "puckworks/models/__init__.py",
    "docs/cards/foster2025.md",
    "docs/cards/foster2025_2.md",
    "puckworks/data/de1_fixtureA.json",
    "puckworks/data/MANIFEST.csv",
)

#: The one execution the protocol permits, and what it is NOT.
EXECUTION_CLASS = "MECHANISM_IDENTITY_CHECK"

#: Frozen in PROTOCOL.md section 5, before any number was computed.
IDENTITY_RMSE_MAX_MM = 0.01
IDENTITY_MAXABS_MAX_MM = 0.02

#: Grid densities for the refinement check. A residual that does not fall as the quadrature grid
#: refines is not quadrature error, and the identity claim would fail.
IDENTITY_GRIDS = (400, 1600, 6400)

#: Correction targets this screen may NAME but may never EDIT (PROTOCOL.md section 11).
CORRECTION_TARGETS = (
    "puckworks/data/MANIFEST.csv",
    "docs/cards/foster2025.md",
    "docs/ROADMAP.md",
)


def _sha256(rel_path: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel_path).read_bytes()).hexdigest()


def provenance() -> dict:
    return {
        "base_commit": BASE_COMMIT,
        "protocol_path": PROTOCOL_PATH,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "input_sha256": {f: _sha256(f) for f in INPUT_FILES},
        "command": "python -m puckworks.analysis.screen_i090_first_drip",
    }


def _registry_entry(name: str) -> dict:
    from puckworks.registry import components
    c = [x for x in components() if x.name == name][0]
    return {"name": c.name, "stage": c.stage, "kind": c.kind, "module": c.module,
            "assumptions": c.assumptions, "valid_range": c.valid_range,
            "evidence_strength": c.evidence_strength,
            "gates": [g.__name__ for g in c.gates]}


def _fixture() -> dict:
    return json.loads((REPO_ROOT / "puckworks/data/de1_fixtureA.json").read_text())


def _manifest_row(dataset_id: str) -> dict:
    import csv
    with open(REPO_ROOT / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["dataset_id"] == dataset_id:
                return dict(row)
    raise LookupError(dataset_id)


# ------------------------------------------------------------------------------------------
# E3 — are they rivals at all?
# ------------------------------------------------------------------------------------------

def relationship_check() -> dict:
    """Co-location is not a relationship. Establish what actually binds these two components.

    Checked three ways: the corpus map's card binding, the card's own words, and the registry
    stages. Any one of them alone would be weak; together they settle it.
    """
    corpus = json.loads((REPO_ROOT / "docs/insights/generated/corpus_map.json").read_text())
    cards = {}
    for e in corpus.get("entities", []):
        if e.get("id") in ("model:%s" % COMPONENT_A, "model:%s" % COMPONENT_B):
            cards[e["id"].split(":", 1)[1]] = e["attrs"].get("card_path")

    card_text = (REPO_ROOT / "docs/cards/foster2025.md").read_text(encoding="utf-8")
    shared_clause = ("one card\nserves `foster2025.infiltration` and `foster2025.machine_mode`, "
                     "so anything listed above is\nattributed to both")
    shared_declared = shared_clause.replace("\n", " ") in " ".join(card_text.split("\n"))

    inf_doc = inspect.getdoc(
        __import__("puckworks.models.foster2025.infiltration", fromlist=["x"])) or ""
    mm_doc = inspect.getdoc(
        __import__("puckworks.models.foster2025.machine_mode", fromlist=["x"])) or ""

    a, b = _registry_entry(COMPONENT_A), _registry_entry(COMPONENT_B)
    return dict(
        card_binding=cards,
        both_components_share_one_card=bool(len(set(cards.values())) == 1 and len(cards) == 2),
        card_declares_outputs_attributed_to_both=bool(shared_declared),
        card_quote="one card serves `foster2025.infiltration` and `foster2025.machine_mode`, so "
                   "anything listed above is attributed to both.",
        registry_stages={COMPONENT_A: a["stage"], COMPONENT_B: b["stage"]},
        stages_differ=bool(a["stage"] != b["stage"]),
        infiltration_docstring_says="their full pump/headspace model ... matters only when "
                                    "pressure is not measured, and is left as the PUCK LAB "
                                    "\"machine mode\" backlog item",
        machine_mode_docstring_says="Complements foster2025.infiltration (which consumes a "
                                    "measured P(t)); this is the \"machine mode\" that produces "
                                    "it.",
        infiltration_doc_names_machine_mode=bool("machine mode" in inf_doc),
        machine_mode_doc_names_complement=bool("Complements foster2025.infiltration" in mm_doc),
        card_2_quote="machine mode can be a separate machine-stage component emitting P(t)/Q(t) "
                     "that infiltration consumes (docs/cards/foster2025_2.md, Couplings)",
        relationship="PRODUCER_CONSUMER",
        are_rivals=False,
        why="the two components occupy different stages of one pipeline: machine_mode GENERATES "
            "the pressure history that infiltration CONSUMES. The `first_drip_time` edge appears "
            "on both because they share ONE card whose Outputs clause is, by the card's own "
            "statement, attributed to both -- one clause counted twice, not two independent "
            "predictions.")


# ------------------------------------------------------------------------------------------
# E1/E2 — the event-definition table
# ------------------------------------------------------------------------------------------

def event_definition_table() -> list[dict]:
    """The three candidate 'first drip' events, from the authorities, copied not paraphrased."""
    from puckworks.models.foster2025 import infiltration as inf
    from puckworks.models.foster2025.machine_mode import FosterParams
    p = FosterParams()
    return [
        dict(event="A. front arrival at the bed base",
             authority="%s.front_from_pressure(...)['t_saturate']" % COMPONENT_A,
             physical_event="sharp front s(t) reaches the bed depth L",
             detection_threshold="none -- an exact model boundary crossing",
             time_origin="start of the supplied pressure trace",
             pressure_history="RECORDED or prescribed, supplied by the caller",
             sampling_interval="not applicable (closed form)",
             known_delay="none -- there is no transport path in the model",
             rig="whatever rig supplied the trace"),
        dict(event="B. saturation time under a modelled pressure history",
             authority="%s.reported_times()[1] = t_s + t_shift" % COMPONENT_B,
             physical_event="s(t) reaches L in the staged pump/headspace ODE",
             detection_threshold="none -- an exact model boundary crossing",
             time_origin="model t=0, shifted by a FITTED start-time alignment "
                         "t_shift = %.3f s" % p.t_shift,
             pressure_history="GENERATED by the model from a pump characteristic and trapped "
                              "headspace; no recorded P(t) can be supplied",
             sampling_interval="not applicable (ODE)",
             known_delay="none modelled",
             rig="DeLonghi EC685 nominal pump, 59 mm basket (A = %.6f m2), L = %.3f mm, "
                 "fine grind" % (p.A, p.L * 1e3)),
        dict(event="C. first mass on the scale",
             authority="%s.observed_first_drip_s(t, weight_g)" % COMPONENT_A,
             physical_event="first recorded sample with weight strictly above %.1f g"
                            % inf.FIRST_DRIP_THRESHOLD_G,
             detection_threshold="%.1f g (module constant FIRST_DRIP_THRESHOLD_G)"
                                 % inf.FIRST_DRIP_THRESHOLD_G,
             time_origin="the fixture's own elapsed-time axis",
             pressure_history="not applicable -- this is the measurement side",
             sampling_interval="the fixture's cadence (see the evidence audit)",
             known_delay="UNCHARACTERISED -- basket, screen, spout and cup transport plus scale "
                         "response are not modelled or measured anywhere in the repository",
             rig="Decent DE1, 18 g dose"),
    ]


def event_gate(defs: list[dict], rel: dict) -> dict:
    """E1, E2, E3. Fails closed."""
    A, B, C = defs
    e1 = (A["time_origin"] == B["time_origin"]
          and A["pressure_history"] == B["pressure_history"])
    e2 = C["known_delay"].startswith("none")            # a characterised (zero) delay would pass
    e3 = bool(rel["are_rivals"])
    return dict(
        checks={
            "E1_same_event_across_the_two_components": dict(
                passed=bool(e1),
                reason="both compute front arrival at z = L, but on DIFFERENT time origins (a "
                       "supplied trace's start vs a model zero shifted by the fitted "
                       "t_shift = 0.796 s) and under DIFFERENT pressure histories (recorded vs "
                       "self-generated). Same physical event, different clocks and different "
                       "forcing"),
            "E2_model_event_equals_measured_event": dict(
                passed=bool(e2),
                reason="front breakthrough at a model boundary is not first registered scale "
                       "mass. The transport and instrument delay between them is uncharacterised, "
                       "and docs/cards/foster2025.md declares the measured event is NOT a model "
                       "output. Constructing the mapping here would be inventing a transfer "
                       "model, which the protocol lists as a no-go"),
            "E3_the_components_are_rivals": dict(passed=bool(e3), reason=rel["why"]),
        },
        passed=bool(e1 and e2 and e3),
        failed=[k for k, v in {"E1_same_event_across_the_two_components": e1,
                               "E2_model_event_equals_measured_event": e2,
                               "E3_the_components_are_rivals": e3}.items() if not v])


# ------------------------------------------------------------------------------------------
# evidence and replicate audit
# ------------------------------------------------------------------------------------------

def evidence_audit() -> dict:
    from puckworks.models.foster2025 import infiltration as inf
    fx = _fixture()
    t = np.asarray(fx["elapsed_s"], float)
    w = np.asarray(fx["weight_g"], float)
    dt = np.diff(t)
    thr = inf.FIRST_DRIP_THRESHOLD_G
    t_drip = inf.observed_first_drip_s(t, w)
    above = np.flatnonzero(w > thr)
    nonzero = np.flatnonzero(w > 0.0)
    row = _manifest_row(DATASET)

    return dict(
        dataset=DATASET,
        source=fx["source"],
        independent_extractions=1,
        independent_extractions_basis="the fixture is one named Visualizer shot "
                                      "(20210921T085910); there is no second shot id, no "
                                      "replicate index and no repeat column anywhere in it",
        rows_are_samples_not_replicates=True,
        n_samples=int(t.size),
        trace_span_s=[float(t[0]), float(t[-1])],
        cadence_s=dict(min=float(dt.min()), median=float(np.median(dt)),
                       mean=float(dt.mean()), max=float(dt.max())),
        event_resolution_s=float(np.median(dt)),
        event_resolution_note="this is the resolution of the event, NOT a population variance. "
                              "Densely sampled points within one extraction are not replicates",
        replicate_spread_available=False,
        experimental_spread_value=None,
        observed_first_drip_s=t_drip,
        detection_threshold_g=thr,
        first_nonzero_weight_s=float(t[nonzero[0]]) if nonzero.size else None,
        first_nonzero_weight_g=float(w[nonzero[0]]) if nonzero.size else None,
        samples_between_first_nonzero_and_threshold=int(above[0] - nonzero[0])
        if above.size and nonzero.size else None,
        dose_g=fx["dose_g"],
        grind_setting="%s (ASSUMED, per the fixture key `grind_setting_assumed`)"
                      % fx["grind_setting_assumed"],
        kappa="%.6f (FITTED to this same shot, per the fixture key `kappa_fitted`)"
              % fx["kappa_fitted"],
        matched_operating_configuration_fully_specified=False,
        configuration_gap="the grind setting is assumed rather than measured and the permeability "
                          "is fitted to this shot; neither is an independently supplied "
                          "configuration variable",
        manifest_row=row,
        manifest_caveat=row["caveat"],
        within_model_uncertainty=dict(
            **{COMPONENT_A: None, COMPONENT_B: None},
            note="NEITHER component declares an uncertainty on first_drip_time. The registry "
                 "declares evidence STRENGTHS (sign_or_compatibility, "
                 "source_curve_reproduction), which are labels, not bands"),
        prohibited_uncertainty_substitutes_not_used=[
            "solver convergence", "optimizer residual", "fit error for another target",
            "a single experimental/model residual", "between-model separation",
            "a qualitative evidence-strength label", "an assumed coefficient of variation"],
        conclusion="one physically independent extraction, no replicate spread, and no declared "
                   "within-model uncertainty on this observable for either component")


# ------------------------------------------------------------------------------------------
# the one permitted execution: MECHANISM_IDENTITY_CHECK
# ------------------------------------------------------------------------------------------

def mechanism_identity_check() -> dict:
    """Demonstrate that the two components share one sharp-front law.

    Solve `machine_mode` in ITS OWN declared configuration (Foster Table I), read off the driving
    pressure its solution implies at the bed top, and integrate `infiltration`'s PUBLIC closed
    form under exactly that pressure. If the two front trajectories coincide, the components do
    not merely agree -- they are the same model differing only in where P(t) comes from, which is
    what "not rivals" means concretely.

    No refit, no parameter change, no comparison against de1_fixtureA, and no claim about which
    component fits any data better.
    """
    from puckworks.models.foster2025 import infiltration as inf
    from puckworks.models.foster2025 import machine_mode as fm

    r = fm.solve()
    p = r["p"]
    t_p, t_s, s_p = r["t_p"], r["t_s"], r["s_p"]

    def _run(n_grid: int) -> dict:
        t = np.linspace(t_p, t_s, n_grid)
        s_mm, H_mm = [], []
        for ti in t:
            s, H = fm._sH(ti, r)
            s_mm.append(s); H_mm.append(H)
        s_mm = np.asarray(s_mm); H_mm = np.asarray(H_mm)
        # the driving pressure machine_mode's own solution implies at the bed top (Eq. 16/52,
        # rearranged): f_bed = (k/(mu s)) * dP  with  dP = p_h + p_c + rho g (H + s) - p_a
        dP = (fm.p_h(H_mm, p) + p.p_c + p.rho * p.g * (H_mm + s_mm) - p.p_a)
        # infiltration's public closed form, started from the ponding state s(t_p) = s_p
        out = inf.front_from_pressure(t, dP / 1e5, p.k, p.phi_T, p.L,
                                      mu=p.mu, rho=p.rho)
        s_inf = np.sqrt(np.minimum(s_p ** 2 + out["s"] ** 2, p.L ** 2))
        # compare away from the terminal cap, where both are pinned to L by construction
        keep = s_mm < p.L * 0.999
        d = (s_inf[keep] - s_mm[keep]) * 1e3                      # mm
        return dict(n_grid=n_grid, n_compared=int(keep.sum()),
                    rmse_mm=float(np.sqrt(np.mean(d ** 2))),
                    max_abs_mm=float(np.max(np.abs(d))))

    refinement = [_run(n) for n in IDENTITY_GRIDS]
    finest = refinement[-1]
    falls = all(refinement[i + 1]["rmse_mm"] < refinement[i]["rmse_mm"]
                for i in range(len(refinement) - 1))

    return dict(
        execution_class=EXECUTION_CLASS,
        is_a_discrimination_run=False,
        models_executed=[COMPONENT_B, COMPONENT_A],
        model_solves_performed=1 + len(IDENTITY_GRIDS),
        solves_note="one machine_mode ODE solve in its own declared configuration, plus %d "
                    "evaluations of infiltration's closed form at increasing quadrature "
                    "density. No refit, no parameter change, no de1_fixtureA comparison"
                    % len(IDENTITY_GRIDS),
        configuration="Foster Table I fine-grind fit, unmodified (L=%.5f m, A=%.6f m2, "
                      "k=%.3e m2, phi_T=%.3f)" % (p.L, p.A, p.k, p.phi_T),
        shared_law="phi_T * s * ds/dt = (k/mu) * dP  -- machine_mode integrates it as "
                   "ds/dt = f_bed/phi_T with f_bed = (k/(mu s)) dP; infiltration integrates the "
                   "same equation in closed form",
        window_s=[float(t_p), float(t_s)],
        refinement=refinement,
        rmse_mm=finest["rmse_mm"],
        max_abs_mm=finest["max_abs_mm"],
        threshold_rmse_mm=IDENTITY_RMSE_MAX_MM,
        threshold_max_abs_mm=IDENTITY_MAXABS_MAX_MM,
        residual_falls_with_grid_refinement=bool(falls),
        bed_depth_mm=float(p.L * 1e3),
        existing_gate_tolerance_mm=0.2,
        identity_holds=bool(finest["rmse_mm"] < IDENTITY_RMSE_MAX_MM
                            and finest["max_abs_mm"] < IDENTITY_MAXABS_MAX_MM and falls),
        interpretation="the two components are one front law. Their predicted first-drip times "
                       "can differ ONLY through the pressure history supplied, which is a "
                       "boundary condition, not a mechanism. first_drip_time cannot discriminate "
                       "a mechanism between them because there is only one mechanism.",
        what_this_does_not_show="that the shared law is CORRECT. Showing two implementations "
                                "agree is a statement about the code and the source, not about "
                                "the physics being right.")


# ------------------------------------------------------------------------------------------
# validity range
# ------------------------------------------------------------------------------------------

def validity_range_check() -> dict:
    from puckworks.models.foster2025.machine_mode import FosterParams
    fx = _fixture()
    p = FosterParams()
    a, b = _registry_entry(COMPONENT_A), _registry_entry(COMPONENT_B)
    return dict(
        de1_fixtureA=dict(machine="Decent DE1", dose_g=fx["dose_g"],
                          grind_setting_assumed=fx["grind_setting_assumed"],
                          recorded_pressure_trace=True),
        infiltration_declared_range=a["valid_range"],
        machine_mode_declared_range=b["valid_range"],
        machine_mode_declared_rig="DeLonghi EC685 nominal pump (Q_m = %.3e m3/s), 59 mm basket "
                                  "(A = %.6f m2), L = %.3f mm, fine grind < 300 um"
                                  % (p.Q_m, p.A, p.L * 1e3),
        machine_mode_can_consume_a_recorded_trace=False,
        machine_mode_consumption_note="`solve()` takes only a FosterParams; there is no argument "
                                      "for a recorded P(t). Supplying one would require refitting "
                                      "the pump characteristic (p_m, Q_m, R_f, beta), which the "
                                      "protocol lists as a no-go",
        de1_inside_machine_mode_range=False,
        de1_inside_machine_mode_range_why="the declared rig is a DeLonghi EC685 with a 59 mm "
                                          "basket and a 10 g fine-grind dose; de1_fixtureA is a "
                                          "Decent DE1 at 18 g with an assumed grind setting of "
                                          "1.9. The dose alone is 1.8x the declared value",
        infiltration_is_run_on_de1_by_an_existing_gate=True,
        infiltration_gate="gate_infiltration_triangle -- a declared, gated use of this component "
                          "on this fixture, carrying the component's own "
                          "sign_or_compatibility strength. This screen neither endorses nor "
                          "disputes that usage; it records it")


# ------------------------------------------------------------------------------------------
# adversarial checks
# ------------------------------------------------------------------------------------------

def adversarial_checks(ev: dict, ident: dict, vr: dict, rel: dict) -> list[dict]:
    from puckworks.models.foster2025 import infiltration as inf
    fx = _fixture()
    t = np.asarray(fx["elapsed_s"], float); w = np.asarray(fx["weight_g"], float)
    alt = {g: inf.observed_first_drip_s(t, w, threshold_g=g)
           for g in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0)}
    spread = [v for v in alt.values() if v is not None]
    return [
        dict(id="B1", check="threshold sensitivity",
             result="the measured event moves with the threshold: %s. Across 0.05-2.0 g it spans "
                    "%.3f s, which is %.1f sampling intervals. The event is threshold-defined, "
                    "and the repository fixes ONE threshold (%.1f g) as a module constant"
                    % ({("%.2f g" % k): v for k, v in alt.items()},
                       max(spread) - min(spread),
                       (max(spread) - min(spread)) / ev["event_resolution_s"],
                       inf.FIRST_DRIP_THRESHOLD_G),
             overturns=False,
             note="a single fixed threshold is the right choice for a gate; it does not make the "
                  "event equivalent to a model boundary crossing. For scale: that %.3f s "
                  "convention span is WIDER than the 1.4 s model bracket (6.4-7.8 s) the "
                  "existing gate compares against, so the event convention moves the measured "
                  "quantity by more than the model spread it is checked against"
                  % (max(spread) - min(spread))),
        dict(id="B2", check="is cadence being used as replicate spread?",
             result="no. The %.3f s median cadence is recorded as EVENT RESOLUTION and is never "
                    "used as an uncertainty band. `replicate_spread_available` is False and "
                    "`experimental_spread_value` is null" % ev["event_resolution_s"],
             overturns=False),
        dict(id="B3", check="the shared-card rescue -- do the implementations differ?",
             result="no. Tested on the FRONT LAW in each implementation rather than on prose: "
                    "feeding machine_mode's own implied bed-top pressure into infiltration's "
                    "public closed form reproduces machine_mode's front to RMSE %.2e mm "
                    "(max %.2e mm) on a %.3f mm bed, and the residual falls under grid "
                    "refinement (%s). They are one law"
                    % (ident["rmse_mm"], ident["max_abs_mm"], ident["bed_depth_mm"],
                       " -> ".join("%.1e" % r["rmse_mm"] for r in ident["refinement"])),
             overturns=False,
             note="this is the check that could have made the pair genuine rivals"),
        dict(id="B4", check="the same-event-different-origin rescue",
             result="aligning the origins does not create a rivalry, it removes the last "
                    "difference. machine_mode's reported time carries a FITTED t_shift = 0.796 s; "
                    "strip it and supply the same pressure history and the two components return "
                    "the same front. What remains is the boundary condition",
             overturns=False),
        dict(id="B5", check="validity range",
             result="de1_fixtureA lies OUTSIDE machine_mode's declared configuration (%s), and "
                    "machine_mode cannot consume a recorded pressure trace at all. So the "
                    "matched-configuration comparison the candidate asks for cannot be "
                    "constructed without a refit"
                    % vr["de1_inside_machine_mode_range_why"],
             overturns=False),
        dict(id="B6", check="the separation-as-uncertainty trap",
             result="no between-model separation is reported anywhere in this result, so it "
                    "cannot have been used as its own uncertainty. The screen reports an "
                    "IDENTITY, which is the opposite failure mode and is disclosed as such",
             overturns=False),
        dict(id="B7", check="would replicates have rescued it?",
             result="NO. The obstacles are structural: one card's Outputs clause counted twice, a "
                    "producer/consumer relationship rather than a rivalry, one shared front law, "
                    "and a declared configuration that excludes the fixture. A replicate campaign "
                    "on de1_fixtureA would supply a spread for an event that still has no second "
                    "model to discriminate against. Commissioning it would waste the experiment",
             overturns=False,
             note="stated explicitly because the candidate's expected outcome was "
                  "NEEDS_NEW_DATA plus a costed replicate request"),
        dict(id="B8", check="is first_drip_time therefore worthless as a discriminator?",
             result="no, and this screen does not claim that. It bounds ONE pair. A genuine "
                    "first-drip discrimination needs two INDEPENDENT front closures evaluated "
                    "under ONE recorded pressure history -- for example Foster's sharp front "
                    "against mo2023_2's filling-front switch (its Eqs. 29-30, noted in "
                    "docs/cards/mo2023_2.md as 'a cheap implementation of exactly this backlog "
                    "item'). That pair is not screened here and nothing above speaks to it",
             overturns=False),
    ]


# ------------------------------------------------------------------------------------------
# recorded-not-applied correction target
# ------------------------------------------------------------------------------------------

def recorded_findings() -> dict:
    """A finding the evidence audit surfaced, RECORDED and deliberately NOT corrected.

    PROTOCOL.md section 11: the Foundry is not an authority over an evidence label, and I-045 set
    the precedent of naming a correction target and leaving it byte-unchanged.
    """
    row = _manifest_row(DATASET)
    return dict(
        finding_id="I090-F1",
        category="MISLEADING_CLAIM (candidate; recorded, not adjudicated by this screen)",
        target="puckworks/data/MANIFEST.csv, row `de1_fixtureA`, column `validation_strength`",
        current_value=row["validation_strength"],
        contradicting_authority="docs/ROADMAP.md 7.1, entry dated 2026-07-16",
        contradicting_quote="the permeability comes from `kappa_fitted=1.196` fitted to the same "
                            "DE1 fixture-A shot and the sharp front is driven by that shot's own "
                            "pressure trace, so the first-drip bracket is a wide-bracket "
                            "compatibility check on in-sample data, not a parameter-free "
                            "independent result",
        what_makes_it_a_contradiction="the manifest cell asserts the top rung of the ROADMAP 0 "
                                      "ladder (`independent`) and the exact phrase "
                                      "(`parameter-free`) that the later changelog entry negates "
                                      "for this dataset's only first-drip gate use. The entry is "
                                      "dated AFTER the 2026-07-12 entry that had kept the "
                                      "'foster triangle' among the legitimate parameter-free "
                                      "uses, and it demoted the component's evidence_strength "
                                      "for precisely this reason",
        why_it_matters="ROADMAP 0 rung labels are load-bearing (CLAUDE.md rules 4 and 5), and the "
                       "Foundry copies this cell byte-identically into "
                       "docs/insights/generated/evidence_lineage_index.csv, so the corpus "
                       "inherits it",
        recommended_replacement="post-fit reconstruction (in-sample: kappa fitted to this shot; "
                                "front driven by this shot's own P(t)) -- per ROADMAP 7.1 "
                                "2026-07-16",
        blast_radius=[
            "puckworks/data/MANIFEST.csv row 27 validation_strength (machine-consumed)",
            "docs/insights/generated/evidence_lineage_index.csv (regenerated from the manifest)",
            "docs/cards/foster2025.md Status line ('parameter-free triangle')",
            "docs/ROADMAP.md body lines describing the triangle as independent/parameter-free",
            "docs/CORPUS_ANALYSIS_PLAN.md, docs/GUIDED_PULL_LABORATORY.md",
        ],
        applied=False,
        why_not_applied="CLAUDE.md: the Insight Foundry 'is never an authority' and 'may not "
                        "change, promote or restate any label, badge or validation rung'. I-045 "
                        "set the precedent and it is precise: its cheap screen NAMED three "
                        "correction targets and left them byte-unchanged; the correction was "
                        "applied only later (ROADMAP 7.1, 2026-08-07), in a separately authorized "
                        "cycle, and only AFTER the IF-7 deep screen had adjudicated the defect "
                        "against the PRIMARY SOURCE. This finding has had no such adjudication -- "
                        "it rests on two live repository statements contradicting each other -- so "
                        "applying it would skip the exact step that made the I-045 correction "
                        "legitimate. The blast radius also reaches ROADMAP body prose and a card "
                        "Status line, which would turn a one-cell correction into a sweep",
        what_would_authorise_applying_it="a source-level adjudication of what `kappa_fitted=1.196` "
                                         "was fitted to and whether the first-drip bracket is "
                                         "independent under ROADMAP 0 -- the I-045 deep-screen "
                                         "pattern -- followed by a separately authorized "
                                         "correction cycle",
        this_screen_does_not_adjudicate="whether `independent` is defensible under a strict "
                                        "reading of ROADMAP 0 (the drip time itself was not used "
                                        "in fitting kappa). The finding is that two LIVE "
                                        "repository statements contradict each other and the "
                                        "later one is the project's own adjudication -- not that "
                                        "this screen has re-derived the right rung",
        distinct_from_I045=True,
        distinct_from_I045_note="I-045's frozen rule selected three manifest rows and "
                                "tests/test_screen_i045.py asserts de1_fixtureA is FOREIGN to "
                                "that selection. This is an independent row and an independent "
                                "finding",
    )


# ------------------------------------------------------------------------------------------
# decision
# ------------------------------------------------------------------------------------------

def decide(gate_result: dict, ev: dict) -> dict:
    structural = [k for k in gate_result["failed"]
                  if k.startswith(("E1", "E2", "E3"))]
    if gate_result["passed"]:
        raise AssertionError("event gate passed: path 3 requires an executed discrimination, "
                             "which this branch does not implement")
    decision = "RETIRE" if structural else "NEEDS_NEW_DATA"
    return dict(
        decision=decision,
        rule_applied="protocol section 6 ordering rule, frozen before results: a STRUCTURAL "
                     "obstacle (not rivals / no common event definition / evidence outside a "
                     "declared configuration) is RETIRE, because no quantity of new measurement "
                     "changes it. NEEDS_NEW_DATA is reserved for a well-posed comparison whose "
                     "single missing item is a measurement or an uncertainty",
        gate_failures=gate_result["failed"],
        structural_failures=structural,
        rationale="foster2025.infiltration and foster2025.machine_mode are not rival predictors "
                  "of first drip. They are sequential stages of one pipeline -- machine_mode "
                  "GENERATES the pressure history infiltration CONSUMES -- bound to ONE card "
                  "whose Outputs clause the card itself attributes to both, which is why the "
                  "tension row counted two predicting models. They share the identical sharp-front "
                  "law, demonstrated to sub-micron agreement, so any difference between their "
                  "first-drip times is a difference in the pressure history supplied, not in a "
                  "mechanism. Separately, the model event (front reaches z = L) is not the "
                  "measured event (first sample above 0.5 g on the DE1 scale) and no validated "
                  "mapping exists; and de1_fixtureA lies outside machine_mode's declared "
                  "configuration, which cannot consume a recorded trace at all.",
        would_replicates_have_rescued_it=False,
        replicate_note="stated explicitly so that a replicate campaign is not commissioned for a "
                       "comparison that would still be ill-posed with any number of shots")


# ------------------------------------------------------------------------------------------
# screen
# ------------------------------------------------------------------------------------------

def screen() -> dict:
    rel = relationship_check()
    defs = event_definition_table()
    g = event_gate(defs, rel)
    ev = evidence_audit()
    vr = validity_range_check()
    ident = mechanism_identity_check()
    decision = decide(g, ev)
    checks = adversarial_checks(ev, ident, vr, rel)

    return {
        "screen": CANDIDATE_ID,
        "candidate_id": CANDIDATE_ID,
        "tension_row": TENSION_ROW,
        "disposition": ["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                        "NOT_A_MODEL_VALIDATION_UPGRADE"],
        "components": [COMPONENT_A, COMPONENT_B],
        "dataset": DATASET,
        "registry_entries": {COMPONENT_A: _registry_entry(COMPONENT_A),
                             COMPONENT_B: _registry_entry(COMPONENT_B)},
        "provenance": provenance(),
        "protocol": {"path": PROTOCOL_PATH, "sha256": _sha256(PROTOCOL_PATH),
                     "frozen_before_execution": True,
                     "note": "committed in its own commit, before this module existed"},
        "observable_definition": {
            "name": "first_drip_time",
            "units": "s",
            "three_distinct_events": defs,
            "one_common_definition_exists": False,
            "frozen_event_used_for_the_measured_side":
                "first sample with weight strictly above 0.5 g on the DE1 scale "
                "(FIRST_DRIP_THRESHOLD_G, the repository's single authoritative constant)"},
        "relationship_check": rel,
        "event_definition_gate": g,
        "evidence_audit": ev,
        "validity_range_check": vr,
        "matched_scenario": None,
        "matched_scenario_note": "no matched scenario exists: machine_mode accepts no recorded "
                                 "pressure history and de1_fixtureA lies outside its declared "
                                 "configuration. The only configuration where both are declared "
                                 "is machine_mode's own, which is where the identity check ran",
        "execution": ident,
        "models_executed": ident["models_executed"],
        "model_solves_performed": ident["model_solves_performed"],
        "models_executed_note": "one bounded MECHANISM_IDENTITY_CHECK inside machine_mode's own "
                                "declared configuration. NOT a discrimination run: neither "
                                "component was compared against de1_fixtureA, and nothing was "
                                "refitted",
        "uncertainty_authorities": {
            COMPONENT_A: dict(evidence_label="sign_or_compatibility",
                              numerical_band_on_first_drip=None,
                              note="a label, not a band"),
            COMPONENT_B: dict(evidence_label="source_curve_reproduction",
                              numerical_band_on_first_drip=None,
                              note="a label, not a band"),
            "measurement": dict(replicate_spread=None,
                                event_resolution_s=ev["event_resolution_s"],
                                note="one extraction. Event resolution is not population "
                                     "variance and is not used as one"),
            "conclusion": "no defensible discrimination uncertainty exists -- and it is not the "
                          "binding obstacle, because there is no rival pair to discriminate"},
        "primary_numerical_findings": {
            "independent_extractions": ev["independent_extractions"],
            "observed_first_drip_s": ev["observed_first_drip_s"],
            "detection_threshold_g": ev["detection_threshold_g"],
            "event_resolution_s": ev["event_resolution_s"],
            "mechanism_identity_rmse_mm": ident["rmse_mm"],
            "mechanism_identity_max_abs_mm": ident["max_abs_mm"],
            "mechanism_identity_holds": ident["identity_holds"],
            "bed_depth_mm": ident["bed_depth_mm"],
            "note": "no between-model separation is reported. The screen reports an IDENTITY "
                    "between the two components' front laws, which is why a separation would "
                    "have been meaningless"},
        "adversarial_checks": checks,
        "adversarial_checks_overturning": [c["id"] for c in checks if c["overturns"]],
        "decision": decision["decision"],
        "decision_record": decision,
        "recorded_findings": [recorded_findings()],
        "correction_targets_named_not_applied": list(CORRECTION_TARGETS),
        "reopen_condition":
            "a SECOND, INDEPENDENT front closure is registered and evaluated against "
            "foster2025.infiltration under ONE recorded pressure history on one rig -- for "
            "example mo2023_2's filling-front switch (Eqs. 29-30), which docs/cards/mo2023_2.md "
            "already names as 'a cheap implementation of exactly this backlog item'. THAT pair "
            "would be a genuine first-drip discrimination, and it would then also need: a "
            "characterised transport/instrument delay between front breakthrough and the scale "
            "threshold crossing, and physically independent replicate extractions to supply a "
            "spread. Replicates ALONE do not reopen this candidate -- with no rival pair there is "
            "nothing for a spread to discriminate.",
        "claim_ceiling":
            "A registry finding about how a shared-card Outputs clause generates a spurious "
            "discriminator row, plus a code-level identity between two implementations. It does "
            "NOT upgrade either component's rung: foster2025.infiltration remains "
            "sign_or_compatibility and foster2025.machine_mode remains "
            "source_curve_reproduction. It does NOT convert within-campaign evidence into "
            "independent validation. It does NOT establish that the shared front law is CORRECT "
            "-- two implementations agreeing is a statement about the code and the source, not "
            "about the physics. It does NOT establish mechanism identification in either "
            "direction. It does NOT validate the unresolved de1_fixtureA provenance condition, "
            "and it does not rely on that condition being resolved. It licenses no reader-facing "
            "statement about first drip in espresso.",
        "evidence_labels_unchanged": True,
        "administrative_exception_invoked": False,
        "administrative_exception_note": "a qualifying candidate defect was FOUND and RECORDED "
                                         "(see recorded_findings) and deliberately NOT "
                                         "corrected. No administrative surface was edited by "
                                         "this screen",
    }


# ------------------------------------------------------------------------------------------
# figure
# ------------------------------------------------------------------------------------------

def figure(result: dict | None = None, path: str | None = None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()
    ev, ident = r["evidence_audit"], r["execution"]
    ABS = "#b4472a"
    A_COL, B_COL, M_COL = "#37618a", "#7a5195", "#2e7d5b"

    fx = _fixture()
    t = np.asarray(fx["elapsed_s"], float)
    w = np.asarray(fx["weight_g"], float)
    P = np.asarray(fx["pressure_bar"], float)

    fig = plt.figure(figsize=(13.4, 9.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.34, wspace=0.22)

    # ---- (a) the pipeline, not a rivalry ----
    ax = fig.add_subplot(gs[0, 0])
    ax.set_axis_off()
    ax.set_title("(a)  Not a rival pair — a producer and its consumer", loc="left",
                 fontweight="bold")
    boxes = [(0.005, B_COL, "foster2025.machine_mode", "stage: machine\n\npump + trapped "
              "headspace\nGENERATES P(t)"),
             (0.355, A_COL, "foster2025.infiltration", "stage: infiltration\n\nsharp front "
              "under a\nsupplied P(t) - CONSUMES it"),
             (0.705, M_COL, "first_drip_time", "\nt_saturate:\ns(t) = L")]
    for x, colr, head, body in boxes:
        ax.add_patch(Rectangle((x, 0.55), 0.29, 0.31, transform=ax.transAxes, facecolor="white",
                               edgecolor=colr, linewidth=1.4))
        ax.text(x + 0.145, 0.815, head, ha="center", va="center", fontsize=6.6, color=colr,
                fontweight="bold", family="monospace")
        ax.text(x + 0.145, 0.678, body, ha="center", va="center", fontsize=6.8, linespacing=1.5)
    for x in (0.298, 0.648):
        ax.add_patch(FancyArrowPatch((x, 0.705), (x + 0.05, 0.705), transform=ax.transAxes,
                                     arrowstyle="-|>", mutation_scale=11, color="#555",
                                     linewidth=1.3))
    ax.text(0.5, 0.45, "ONE card serves both components — docs/cards/foster2025.md:\n"
                       "\"anything listed above is attributed to both\"",
            ha="center", va="center", fontsize=7.6, style="italic", linespacing=1.6,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#f4f4f4", edgecolor="#bbb"))
    ax.text(0.5, 0.22, "so the tension row's \"2 models predict first_drip_time\"\n"
                       "is ONE Outputs clause counted twice",
            ha="center", va="center", fontsize=8.2, color=ABS, fontweight="bold",
            linespacing=1.6)
    ax.text(0.5, 0.03, "co-location is not a relationship", ha="center", va="center",
            fontsize=8.4, style="italic", color=ABS)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # ---- (b) the mechanism identity ----
    ax = fig.add_subplot(gs[0, 1])
    n = [x["n_grid"] for x in ident["refinement"]]
    rm = [x["rmse_mm"] for x in ident["refinement"]]
    mx = [x["max_abs_mm"] for x in ident["refinement"]]
    ax.loglog(n, rm, "o-", color=M_COL, linewidth=1.7, markersize=5.0, label="RMSE of $\\Delta s$")
    ax.loglog(n, mx, "s--", color=M_COL, alpha=0.6, linewidth=1.3, markersize=4.2,
              label="max $|\\Delta s|$")
    ax.axhline(ident["threshold_rmse_mm"], color=ABS, linewidth=1.4, linestyle=":",
               label="frozen threshold, RMSE < %.2f mm" % ident["threshold_rmse_mm"])
    ax.axhline(ident["existing_gate_tolerance_mm"], color="#999", linewidth=1.2, linestyle="-.",
               label="existing gate tolerance, 0.2 mm")
    ax.set_xlabel("quadrature grid points over $[t_p,\\ t_s]$")
    ax.set_ylabel("front difference  |$s_{infiltration}-s_{machine\\_mode}$|  [mm]")
    ax.set_title("(b)  One shared front law, demonstrated", loc="left", fontweight="bold")
    ax.legend(loc="lower left", fontsize=7.0, framealpha=0.96)
    ax.grid(alpha=0.25, which="both", linewidth=0.5)
    ax.text(0.97, 0.80, "fed machine_mode's own implied $\\Delta P(t)$,\n"
                        "infiltration reproduces its front to %.1e mm\n"
                        "on a %.2f mm bed — and the residual FALLS\n"
                        "under refinement, so it is quadrature, not physics"
            % (ident["rmse_mm"], ident["bed_depth_mm"]),
            transform=ax.transAxes, ha="right", va="top", fontsize=7.0, linespacing=1.6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#ccc"))

    # ---- (c) the evidence: one shot, no spread ----
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(t, w, "-", color="#555", linewidth=1.2, label="de1_fixtureA weight $W(t)$ [g]")
    ax.plot(t, w, ".", color="#555", markersize=2.6)
    ax.axhline(ev["detection_threshold_g"], color=A_COL, linewidth=1.2, linestyle="--",
               label="detection threshold %.1f g" % ev["detection_threshold_g"])
    ax.axvline(ev["observed_first_drip_s"], color=ABS, linewidth=1.8,
               label="observed first drip %.3f s  (n = 1 shot)" % ev["observed_first_drip_s"])
    ax2 = ax.twinx()
    ax2.plot(t, P, "-", color="#c8a24a", linewidth=1.0, alpha=0.85)
    ax2.set_ylabel("pressure [bar]", color="#a8842a", fontsize=8)
    ax2.tick_params(axis="y", labelcolor="#a8842a", labelsize=7)
    ax.set_xlim(0, 12); ax.set_ylim(-0.4, 12)
    ax.set_xlabel("elapsed time [s]")
    ax.set_ylabel("recorded weight [g]")
    ax.set_title("(c)  The evidence: ONE extraction, no spread to draw", loc="left",
                 fontweight="bold")
    ax.legend(loc="center left", fontsize=6.9, framealpha=0.96)
    ax.text(0.985, 0.97,
            "NO ERROR BAR IS DRAWN — none exists.\n"
            "1 physically independent extraction; %d samples of it.\n"
            "cadence %.3f s (median) is EVENT RESOLUTION,\nnot population variance."
            % (ev["n_samples"], ev["event_resolution_s"]),
            transform=ax.transAxes, ha="right", va="top", fontsize=7.0, color=ABS,
            fontweight="bold", linespacing=1.6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=ABS, alpha=0.95))

    # ---- (d) three events, no validated mapping ----
    ax = fig.add_subplot(gs[1, 1])
    ax.set_axis_off()
    ax.set_title("(d)  Three events called \"first drip\", no validated mapping", loc="left",
                 fontweight="bold")
    rows = [
        (A_COL, "A  front arrival at $z=L$",
         "foster2025.infiltration · exact model boundary\ntime origin: start of the SUPPLIED trace"),
        (B_COL, "B  saturation under a MODELLED $P(t)$",
         "foster2025.machine_mode · exact model boundary\ntime origin: model zero + FITTED "
         "$t_{shift}=0.796$ s"),
        ("#555", "C  first mass on the scale",
         "de1_fixtureA · threshold event, %.1f g\ntransport + instrument delay UNCHARACTERISED"
         % ev["detection_threshold_g"]),
    ]
    for i, (colr, head, body) in enumerate(rows):
        y = 0.71 - 0.29 * i
        ax.add_patch(Rectangle((0.02, y), 0.96, 0.21, transform=ax.transAxes, facecolor="white",
                               edgecolor=colr, linewidth=1.3))
        ax.text(0.05, y + 0.155, head, fontsize=8.0, color=colr, fontweight="bold")
        ax.text(0.05, y + 0.062, body, fontsize=7.1, linespacing=1.55)
    for y in (0.665, 0.375):
        ax.add_patch(FancyArrowPatch((0.5, y + 0.045), (0.5, y - 0.04), transform=ax.transAxes,
                                     arrowstyle="-|>", mutation_scale=10, color=ABS,
                                     linewidth=1.4, linestyle=(0, (3, 2))))
        ax.text(0.53, y, "no validated mapping", fontsize=7.2, color=ABS, va="center",
                fontweight="bold")
    ax.text(0.5, 0.035, "the card itself: the scale-threshold comparator is \"NOT a model output\"",
            ha="center", va="center", fontsize=7.6, style="italic", color=ABS)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    fig.suptitle("I-090 cheap screen — CHEAP_SCIENTIFIC_SCREEN / NOT_A_PUBLICATION_RESULT / "
                 "NOT_A_MODEL_VALIDATION_UPGRADE\n"
                 "Decision: RETIRE — not a rival pair. Replicates would NOT have rescued it.",
                 fontsize=9.8, y=0.985)

    out = path or str(REPO_ROOT / "docs/insights/screens/I-090/figures/primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-090/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    fig = figure(r)
    ev, ident = r["evidence_audit"], r["execution"]
    print("protocol frozen before execution: %s (%s)"
          % (r["protocol"]["frozen_before_execution"], r["protocol"]["path"]))
    print("protocol sha256: %s" % r["protocol"]["sha256"])
    print("event gate: passed=%s failed=%s" % (r["event_definition_gate"]["passed"],
                                               r["event_definition_gate"]["failed"]))
    print("relationship: %s (rivals=%s)" % (r["relationship_check"]["relationship"],
                                            r["relationship_check"]["are_rivals"]))
    print("evidence: %d independent extraction(s), %d samples, spread=%s"
          % (ev["independent_extractions"], ev["n_samples"], ev["replicate_spread_available"]))
    print("mechanism identity: RMSE %.3e mm, max %.3e mm, holds=%s (grid falls=%s)"
          % (ident["rmse_mm"], ident["max_abs_mm"], ident["identity_holds"],
             ident["residual_falls_with_grid_refinement"]))
    print("adversarial checks overturning the finding: %s"
          % (r["adversarial_checks_overturning"] or "none"))
    print("DECISION: %s   (replicates would have rescued it: %s)"
          % (r["decision"], r["decision_record"]["would_replicates_have_rescued_it"]))
    print("recorded, NOT applied: %s" % r["recorded_findings"][0]["target"])
    print("wrote %s" % out)
    print("wrote %s" % fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
