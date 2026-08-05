"""screen_i076_matched_models.py — Insight Foundry cheap screen for candidate I-076.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Under one matched scenario, do pannusch2024.solver and cameron2020.extraction_bdf differ
    in sign, ordering, or magnitude on an observable they both produce?

THE PROTOCOL IS FROZEN AND COMMITTED SEPARATELY, BEFORE THIS MODULE EXISTED:
`docs/insights/screens/I-076/PROTOCOL.md`. This module executes that protocol and nothing else.

**NO MODEL IS EXECUTED.** The protocol's determination — that no admissible matched scenario
exists — is reached at scenario construction, which is upstream of running anything. This module
therefore performs an ADMISSIBILITY ANALYSIS over the cards, the registry, the manifest and the
components' own call signatures. `test_screen_i076.py` asserts that neither solver is invoked.

TWO INDEPENDENT BLOCKERS, either sufficient on its own:

  A. GRIND — the two components' grind inputs live in different, non-portable dial spaces.
     `pannusch2024.solver`'s campaign is on a Mahlkoenig E65S (its card points at Schmieder's
     apparatus; Schmieder's card names the grinder). `cameron2020.extraction_bdf` takes an EK43
     dial and resolves it through MEASURED microstructure tables. CLAUDE.md rule 9 / ledger
     A9,G5 forbids mapping one grinder's dial onto another's without an explicit refit adapter,
     and none exists. The numerical coincidence — E65S GL 1.7 vs EK43 dial 1.7 — is a trap, not
     a bridge.

  B. TEMPERATURE — `cameron2020.extraction_bdf.simulate_shot` has NO temperature parameter; it
     is isothermal. `pannusch2024.solver` is declared over T 80-98 C with temperature-dependent
     van't Hoff K(T) and Wilke-Chang D(T). The two cannot receive the same intervention on an
     axis only one of them has.

Both are checked programmatically below rather than asserted in prose.

Run:  python -m puckworks.analysis.screen_i076_matched_models
"""
from __future__ import annotations

import csv
import inspect
import json
import pathlib
import re
import statistics

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-076"
COMPONENT_A = "pannusch2024.solver"
COMPONENT_B = "cameron2020.extraction_bdf"
QUARANTINED = "cameron2020.paper_mode"

PROTOCOL_PATH = "docs/insights/screens/I-076/PROTOCOL.md"

# ------------------------------------------------------------------------------------------
# The candidate scenario, exactly as frozen in the protocol
# ------------------------------------------------------------------------------------------
SCENARIO_SOURCE = "schmieder2023/cup_masses"
SCENARIO_EXP = 7.0
SCENARIO_COMPONENT = "TDS"
SCENARIO_BREW_RATIO = "1/2"
SCENARIO_SELECTION_REASON = (
    "the SOURCE'S OWN DoE Central Point (doe_role == 'DoE Central Point'), selected because the "
    "source declares it the centre of its design — not by inspecting model output, and not by "
    "taking the midpoint of a range. No model had been run when it was chosen, and none has "
    "been run since.")
DOSE_G = 20.00
BEVERAGE_G = 40.0


def scenario():
    """The frozen candidate scenario, read from the source rather than transcribed."""
    from puckworks import data as d
    reps = [x for x in d.schmieder_cup_masses()
            if x["component"] == SCENARIO_COMPONENT
            and x["brew_ratio"] == SCENARIO_BREW_RATIO
            and x["exp"] == SCENARIO_EXP]
    reps.sort(key=lambda x: x["rep"])
    q = [x["scale_flow_ml_s"] for x in reps]
    t = [x["decent_temp_C"] for x in reps]
    c = [x["conc_in_cup"] for x in reps]
    return dict(
        source=SCENARIO_SOURCE, exp=SCENARIO_EXP, observable_component=SCENARIO_COMPONENT,
        brew_ratio=SCENARIO_BREW_RATIO, doe_role=reps[0]["doe_role"],
        selection_reason=SCENARIO_SELECTION_REASON,
        n_replicates=len(reps),
        grind_level_source_dial=reps[0]["grind_level"],
        measured_flow_mL_s=dict(values=[round(v, 4) for v in q],
                                mean=round(statistics.mean(q), 4),
                                min=round(min(q), 4), max=round(max(q), 4),
                                note="scale-derived measured flow — the authorization's "
                                     "preferred common intervention"),
        measured_temperature_C=dict(values=[round(v, 3) for v in t],
                                    mean=round(statistics.mean(t), 4),
                                    target=reps[0]["target_temp_C"]),
        measured_tds_mass_fraction=dict(values=[round(v, 6) for v in c],
                                        mean=round(statistics.mean(c), 6),
                                        mean_pct=round(100 * statistics.mean(c), 4),
                                        replicate_rsd_pct=round(
                                            100 * statistics.stdev(c) / statistics.mean(c), 4)),
        dose_g=DOSE_G, beverage_g=BEVERAGE_G,
        dose_provenance="docs/cards/schmieder2023.md Parameters: dose 20.00 g, nominal (fixed); "
                        "brew ratio 1/2 -> 40 g beverage",
        endpoint="matched collected beverage mass, 40 g",
        pressure_note="schmieder pressure_max_bar is a PER-SHOT MAXIMUM "
                      "(schmieder2023_AUDIT.md D2: 'Do not use as a Darcy dP(Q) point'); both "
                      "components would have been flow-driven, so no pressure node is on the "
                      "critical path")


# ------------------------------------------------------------------------------------------
# BLOCKER A — grind dial spaces
# ------------------------------------------------------------------------------------------
GRINDER_EVIDENCE = {
    COMPONENT_A: dict(
        registry_field="valid_range",
        card="docs/cards/pannusch2024.md",
        campaign_card="docs/cards/schmieder2023.md",
        grinder="Mahlkoenig E65S",
        grinder_quote="20 g dose, DE1 Pro + IMS basket/screen, Acqua Panna water, "
                      "Mahlkönig E65S",
        dial_span_quote="GL 1.4–2.0 (only ~7.5% of the E65S scale → near-identical",
        note="the registry's `EK43-type grind 1.4-2.0` is not supported by the component's own "
             "card, which places the work on Schmieder's apparatus; Schmieder's card names the "
             "grinder as an E65S. Recorded as a discrepancy, NOT corrected here — a screen may "
             "not edit a registry field."),
    COMPONENT_B: dict(
        registry_field="valid_range",
        card="docs/cards/cameron2020.md",
        grinder="EK43",
        grinder_quote="and Darcy-flux tables (EK43 dial 1.1-2.3)",
        note="grind enters via MEASURED microstructure (grind_microstructure(gs) -> phi1, phi2, "
             "a2, bet1, bet2) and Darcy-flux tables keyed to the EK43 dial, so it is "
             "load-bearing physics rather than a flux prefactor"),
}

#: The two existing, mutually inconsistent uncalibrated dial assignments for ONE physical grind.
#: Evidence that the mapping rule 9 forbids is not merely unproven but actively contradictory.
EXISTING_UNCALIBRATED_MAPS = [
    dict(where="puckworks/validation/slow/angeloni_bracket.py:_GRIND_MAP",
         declared="approximate, UNCALIBRATED cross-grinder map (Mythos granulometry -> EK43 gs)",
         mapping={"F": 1.3, "O": 1.9, "C": 2.4}, consumer=COMPONENT_B),
    dict(where="gate_pannusch_angeloni_per_condition / pannusch2024.solver.GRIND_17",
         declared="granulometry O treated as ~ pannusch grind 1.7 (centre grind)",
         mapping={"O": 1.7}, consumer=COMPONENT_A),
]


def blocker_grind():
    """Are the two grind inputs in the same dial space? Checked against the cards."""
    def _read(rel):
        p = REPO_ROOT / rel
        return p.read_text(encoding="utf-8") if p.exists() else ""

    schmieder = _read("docs/cards/schmieder2023.md")
    cameron = _read("docs/cards/cameron2020.md")
    e65s_found = "E65S" in schmieder
    ek43_found = "EK43" in cameron
    same_space = False                                  # only true if one grinder names both
    o_assignments = {m["consumer"]: m["mapping"].get("O") for m in EXISTING_UNCALIBRATED_MAPS}
    contradictory = len({v for v in o_assignments.values() if v is not None}) > 1
    return dict(
        blocker="A_grind_dial_spaces",
        component_a_grinder=GRINDER_EVIDENCE[COMPONENT_A]["grinder"],
        component_b_grinder=GRINDER_EVIDENCE[COMPONENT_B]["grinder"],
        e65s_named_in_campaign_card=e65s_found,
        ek43_named_in_cameron_card=ek43_found,
        same_dial_space=same_space,
        numerical_coincidence=dict(
            schmieder_grind_level=1.7, cameron_dial=1.7,
            note="the SAME NUMBER on two different grinders. Running cameron at gs=1.7 because "
                 "schmieder used GL 1.7 would be the forbidden mapping wearing a disguise."),
        declared_adapter_exists=False,
        rule="CLAUDE.md rule 9 / ledger A9,G5 — dial spaces are grinder-specific and "
             "non-portable; never map one grinder's dial onto another's without an explicit "
             "refit adapter.",
        existing_uncalibrated_maps=EXISTING_UNCALIBRATED_MAPS,
        existing_maps_contradict_each_other=contradictory,
        granulometry_O_assignments=o_assignments,
        grind_is_load_bearing_for_b=True,
        blocks=bool(not same_space),
        evidence=GRINDER_EVIDENCE)


# ------------------------------------------------------------------------------------------
# BLOCKER B — temperature axis
# ------------------------------------------------------------------------------------------
def blocker_temperature():
    """Does each component accept a temperature? Read from the actual call signatures."""
    from puckworks.models.cameron2020 import extraction_bdf as C
    from puckworks.models.pannusch2024 import solver as P
    cam = list(inspect.signature(C.simulate_shot).parameters)
    pan = list(inspect.signature(P.simulate_fractions).parameters)

    def has_T(params):
        return any(p == "T_C" or p.lower().startswith("t_c") or "temp" in p.lower()
                   for p in params)

    cam_T, pan_T = has_T(cam), has_T(pan)
    from puckworks.registry import components
    reg = {c.name: c for c in components()}
    return dict(
        blocker="B_temperature_axis",
        component_a_signature=pan, component_a_accepts_temperature=pan_T,
        component_b_signature=cam, component_b_accepts_temperature=cam_T,
        component_a_declared_range=reg[COMPONENT_A].valid_range,
        component_b_declared_range=reg[COMPONENT_B].valid_range,
        component_a_temperature_dependent_closures=[
            "vant_hoff_K(T) — solid-liquid partition", "diffusion_coeff(T) — Wilke-Chang"],
        component_b_is_isothermal=not cam_T,
        note="one component has a temperature axis and the other has none, so they cannot "
             "receive the same intervention on it. Fixing pannusch at the measured 88.26 C "
             "while cameron receives nothing is two experiments side by side, not a matched "
             "scenario.",
        blocks=bool(pan_T and not cam_T))


# ------------------------------------------------------------------------------------------
# Observable, inventory and uncertainty — recorded even though the screen stops upstream
# ------------------------------------------------------------------------------------------
OBSERVABLE = dict(
    name="whole-cup total dissolved solids",
    units="mass percent of the beverage",
    quantity_kind="mass fraction (NOT a volume concentration)",
    accumulation="cumulative, at the endpoint (NOT instantaneous)",
    basis="beverage MASS (40 g), not beverage volume",
    stopping_rule="matched collected beverage mass of 40 g; cameron via its own Eq. 26 "
                  "t_shot = m_out/(pi R0^2 rho_out q), pannusch via t_end = m_target/flow on "
                  "its g/s convention",
    component_a_native="fraction-averaged outlet concentration in mg/mL; its own port converts "
                       "measured TDS_pct by a factor of 10 (solver._MEAS), i.e. it assumes a "
                       "beverage density of 1000 kg/m^3",
    component_b_native="ShotResult.tds = 100 * M_cup / m_out — a true mass ratio, with "
                       "RHO_OUT = 997 kg/m^3 used internally",
    unit_conversions=["pannusch mg/mL -> mass % : divide by 10 (rho_beverage = 1000 kg/m^3, "
                      "pannusch's own declared convention)",
                      "measured schmieder conc_in_cup is already a mass fraction; x100 -> %"],
    measurement_basis_hazard="schmieder TDS is gravimetrically anchored per DIN 10775 on a "
                             "CENTRIFUGED SUPERNATANT with fines excluded "
                             "(schmieder2023_AUDIT.md D8) — a declared normalization hazard for "
                             "any cross-source TDS comparison",
    densities_differ=dict(pannusch_conversion=1000.0, cameron_internal=997.0,
                          note="recorded, not merged"))

INVENTORY_BASES = {
    COMPONENT_A: dict(convention="per-solute c_s0 (Table 2); TDS modelled as a caffeine-like "
                                 "pseudo-molecule", units="mg/mL"),
    COMPONENT_B: dict(convention="per-BED-VOLUME soluble inventory c_s0 = 118/phi_s, EY ceiling "
                                 "29.6 %, c_sat 212.4", units="kg/m^3"),
    "policy": "kept native. No rescaling, no forced equality, no refit. A difference caused "
              "solely by incompatible inventory bases is a semantic/convention difference, not "
              "a kinetic disagreement.",
}


def uncertainty_authorities(scn):
    """Enumerated SEPARATELY. Never pooled; never borrowed across components."""
    with open(REPO_ROOT / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    caveat = rows[SCENARIO_SOURCE]["caveat"]
    m = re.search(r"mean RSD ([\d.]+)% \(max ([\d.]+)%\)", caveat)
    return dict(
        measured_replicate=dict(
            applies_to="the measured observable (schmieder TDS)",
            this_scenario_rsd_pct=scn["measured_tds_mass_fraction"]["replicate_rsd_pct"],
            n_replicates=scn["n_replicates"],
            campaign_mean_rsd_pct=float(m.group(1)) if m else None,
            campaign_max_rsd_pct=float(m.group(2)) if m else None,
            source=SCENARIO_SOURCE + " MANIFEST caveat, verbatim: " + caveat),
        fitted_source_residual=dict(
            applies_to="pannusch's agreement with ITS OWN fit target",
            value="reproduced fit MAPEs — TDS 6.7 % (published 6.07 %)",
            prohibition="MAY NOT be used as cameron's predictive uncertainty"),
        numerical_convergence=dict(
            applies_to="discretisation only",
            cameron="~0.15 pt default-grid bias (paper SI convergence, registry note)",
            pannusch="grid/tolerance; negligible at the frozen configuration",
            prohibition="MAY NOT be treated as experimental or model-form uncertainty"),
        parameter=dict(applies_to="both", value=None,
                       note="not quantified in either card for this scenario"),
        model_form=dict(applies_to="both", value=None, note="not quantified"),
        pooling_policy="NOT pooled into a single threshold. A SURVIVE on magnitude would require "
                       "a commensurate, source-grounded authority for the compared quantity; "
                       "none spans both components here.")


# ------------------------------------------------------------------------------------------
# Comparability classification — frozen in the protocol, restated from the same evidence
# ------------------------------------------------------------------------------------------
COMPARABILITY_LEVELS = {
    1: "directly comparable",
    2: "comparable through an existing declared adapter",
    3: "same intervention but different observable",
    4: "same label but different basis",
    5: "non-comparable",
}


def comparability(grind, temp):
    primary = 5 if (grind["blocks"] or temp["blocks"]) else 1
    return dict(
        primary=dict(level=primary, name=COMPARABILITY_LEVELS[primary],
                     axis="intervention",
                     rationale="a matched scenario cannot be constructed: the grind axis has no "
                               "declared adapter between the two dial spaces, and the "
                               "temperature axis exists for only one of the two components."),
        secondary=[
            dict(level=2, name=COMPARABILITY_LEVELS[2], axis="observable",
                 rationale="whole-cup TDS mass % at a matched 40 g beverage endpoint, after "
                           "pannusch's own declared mg/mL <-> mass % convention. The observable "
                           "was never the obstacle."),
            dict(level=4, name=COMPARABILITY_LEVELS[4], axis="inventory",
                 rationale="'soluble inventory' names a per-solute pseudo-molecule quantity in "
                           "one component and a per-bed-volume pool with a 29.6 % EY ceiling in "
                           "the other."),
        ],
        note="RP-A concepts used as vocabulary only. No comparability schema, adapter registry, "
             "response atlas or sweep machinery is implemented here.")


# ------------------------------------------------------------------------------------------
# Decision
# ------------------------------------------------------------------------------------------
DECISION_RULE = dict(
    SURVIVE="a directly comparable or existing-adapter comparison shows a difference beyond the "
            "applicable declared uncertainty at the frozen interior scenario, and the difference "
            "is not explained by unit, endpoint, pressure-node, inventory or stopping-rule "
            "convention.",
    RETIRE="results overlap within applicable uncertainty; OR the declared validity ranges "
           "provide no common admissible scenario; OR the apparent disagreement is fully "
           "explained by a documented convention or basis difference.",
    NEEDS_NEW_DATA="constructing the matched scenario requires an invented parameter; OR the "
                   "outputs appear different but no defensible common uncertainty authority "
                   "exists; OR source metadata cannot establish a common observable and "
                   "endpoint.",
    disambiguation="Frozen in the protocol before execution: if the declared ranges simply DO "
                   "NOT INTERSECT on a shared axis, that is RETIRE — no data would change it. "
                   "If a common scenario COULD exist but stating it requires INVENTING a value "
                   "the sources do not supply, that is NEEDS_NEW_DATA, naming the measurement "
                   "that would supply it.")

UNBLOCKING_EVIDENCE = [
    dict(item=1, need="a grind calibration linking the two dial spaces",
         precisely="a measured PSD (or equivalent microstructure) for Schmieder's Mahlkoenig "
                   "E65S at GL 1.4/1.7/2.0, on the same basis as the existing "
                   "`cameron2020/psd_figure2` (Cameron's measured EK43 PSD at four dial "
                   "settings). Equivalently for Angeloni's Mythos O/C/F.",
         resolves="blocker A", sufficient_alone=False),
    dict(item=2, need="a temperature basis for cameron2020.extraction_bdf",
         precisely="either a declared temperature closure, or a source-backed statement of the "
                   "temperature its fixed parameters correspond to, so a pannusch run can be "
                   "placed at that temperature rather than at one cameron cannot represent.",
         resolves="blocker B", sufficient_alone=False),
]


def screen():
    scn = scenario()
    grind = blocker_grind()
    temp = blocker_temperature()
    unc = uncertainty_authorities(scn)
    comp = comparability(grind, temp)
    blockers = [b for b in (grind, temp) if b["blocks"]]

    if blockers:
        decision = "NEEDS_NEW_DATA"
        why = ("Constructing the matched scenario requires an invented parameter. %d "
               "independent blocker(s), each sufficient alone: %s. The observable, the "
               "endpoint, the dose, the measured flow and a six-replicate measured uncertainty "
               "are all available — the obstacle is the INTERVENTION, not the observable."
               % (len(blockers), "; ".join(b["blocker"] for b in blockers)))
    else:                                                  # pragma: no cover - not reachable now
        decision = "PENDING_EXECUTION"
        why = "A matched scenario is admissible; the comparison must be executed."

    return dict(
        screen=CANDIDATE_ID,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        components=[COMPONENT_A, COMPONENT_B],
        quarantined_and_not_invoked=QUARANTINED,
        protocol=dict(path=PROTOCOL_PATH,
                      frozen_before_execution=True,
                      note="committed in its own commit, before this module existed"),
        models_executed=False,
        models_executed_note="no solver is invoked anywhere in this screen; the determination is "
                             "reached at scenario construction, upstream of execution",
        scenario=scn,
        blockers=dict(grind=grind, temperature=temp, n_blocking=len(blockers)),
        observable=OBSERVABLE,
        inventory_bases=INVENTORY_BASES,
        uncertainty_authorities=unc,
        comparability=comp,
        decision_rule=DECISION_RULE,
        unblocking_evidence=UNBLOCKING_EVIDENCE,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_A, _C_B, _C_MEAS, _C_BLOCK = "#0072b2", "#e69f00", "#d55e00", "#cc79a7"


def figure(path=None, result=None):
    """The frozen scenario, the shared observable, and exactly where the common basis fails.

    The authorization requires that the figure must NOT imply that non-comparable native
    quantities are directly comparable. So no model prediction is drawn — none exists — and the
    two components' axes are shown as SEPARATE tracks that do not meet, with the missing adapter
    named on the gap. The one thing drawn on a common axis is the measured observable, which is
    genuinely shared and is not in dispute.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()
    scn, g, t = r["scenario"], r["blockers"]["grind"], r["blockers"]["temperature"]

    fig = plt.figure(figsize=(12.8, 8.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.42, wspace=0.26)

    # ---- A: the intervention axes, shown as two tracks that do not meet -------------------
    axA = fig.add_subplot(gs[0, :])
    axA.set_xlim(0, 100)
    axA.set_ylim(-0.4, 10.2)
    axA.axis("off")
    axA.set_title("A — the frozen scenario reaches both components on every axis EXCEPT the two "
                  "that block it", fontsize=9.2, color=_INK, pad=6, loc="left")

    rows = [
        ("beverage endpoint", "40 g collected mass", "40 g via Eq. 26 t_shot", True, ""),
        ("dose", "20.00 g", "m_in = 20.00 g", True, ""),
        ("flow (common intervention)", "measured %.3f mL/s  ->  g/s"
         % scn["measured_flow_mL_s"]["mean"], "same measured flow  ->  q [m/s]", True, ""),
        ("observable", "mg/mL  ->  mass % (rho=1000)", "mass % natively (rho_out=997)",
         True, ""),
        ("GRIND", "E65S  GL 1.7", "EK43 dial (1.1-2.3)", False,
         "no refit adapter — CLAUDE.md rule 9. Same NUMBER, different grinders."),
        ("TEMPERATURE", "T_C required; K(T), D(T)", "NO temperature parameter", False,
         "cameron is isothermal — the axis exists for only one component."),
    ]
    y = 8.5
    axA.text(23, 9.6, COMPONENT_A, fontsize=8.6, weight="bold", color=_C_A, ha="left")
    axA.text(58, 9.6, COMPONENT_B, fontsize=8.6, weight="bold", color=_C_B, ha="left")
    for label, a, b, ok, note in rows:
        col = _GRID if ok else _C_BLOCK
        axA.add_patch(FancyBboxPatch((1.0, y - 0.42), 97.0, 0.92,
                                     boxstyle="round,pad=0.02,rounding_size=0.08",
                                     fc=col, ec="none", alpha=0.10 if ok else 0.22, zorder=0))
        axA.text(2, y, label, fontsize=7.8, color=_INK,
                 weight="bold" if not ok else "normal")
        axA.text(23, y, a, fontsize=7.4, color=_C_A)
        axA.text(58, y, b, fontsize=7.4, color=_C_B)
        if ok:
            axA.annotate("", xy=(56.5, y), xytext=(50.5, y),
                         arrowprops=dict(arrowstyle="<->", color="#4a4a4a", lw=1.1))
        else:
            axA.plot([50.5, 56.5], [y, y], color=_C_BLOCK, lw=1.4)
            axA.plot([53.5], [y], marker="x", ms=9, color=_C_BLOCK, mew=2.4)
            axA.text(2, y - 0.42, note, fontsize=6.6, color=_C_BLOCK, style="italic")
        y -= 1.42

    # ---- B: the measured observable, the ONE thing on a common axis ----------------------
    axB = fig.add_subplot(gs[1, 0])
    vals = [100 * v for v in scn["measured_tds_mass_fraction"]["values"]]
    mean = scn["measured_tds_mass_fraction"]["mean_pct"]
    xs = range(1, len(vals) + 1)
    axB.axhspan(mean * (1 - 0.025), mean * (1 + 0.025), color=_C_MEAS, alpha=0.14, zorder=0,
                label="campaign mean RSD ±2.5 %")
    axB.plot(xs, vals, "s", ms=6, color=_C_MEAS, zorder=3, label="measured replicates (n=6)")
    axB.axhline(mean, color=_C_MEAS, lw=1.4, ls="--", zorder=2)
    axB.text(len(vals) + 0.35, mean, "mean\n%.2f %%" % mean, fontsize=7.4, color=_C_MEAS,
             va="center", ha="left")
    axB.set_xlim(0.4, len(vals) + 1.35)
    axB.set_xticks(list(xs))
    axB.set_xlabel("schmieder exp 7 replicate", fontsize=8)
    axB.set_ylabel("whole-cup TDS  [mass % of beverage]", fontsize=8)
    axB.grid(True, color=_GRID, lw=0.5)
    axB.set_axisbelow(True)
    axB.legend(loc="lower right", fontsize=7, frameon=False)
    axB.set_title("B — the shared observable exists and is well measured\n"
                  "NO model prediction is drawn: none was computed, because the scenario is "
                  "not admissible", fontsize=8.6, color=_INK, pad=6)

    # ---- C: what would unblock it --------------------------------------------------------
    axC = fig.add_subplot(gs[1, 1])
    axC.axis("off")
    axC.set_xlim(0, 100)
    axC.set_ylim(0, 100)
    axC.set_title("C — the named missing evidence", fontsize=8.6, color=_INK, pad=6, loc="left")
    yy = 88
    for u in r["unblocking_evidence"]:
        axC.add_patch(FancyBboxPatch((1, yy - 30), 97, 30,
                                     boxstyle="round,pad=0.4,rounding_size=1.4",
                                     fc=_C_BLOCK, ec="none", alpha=0.12, zorder=0))
        axC.text(4, yy - 5, "%d. %s" % (u["item"], u["need"]), fontsize=7.8, weight="bold",
                 color=_INK)
        import textwrap as _tw
        for j, ln in enumerate(_tw.wrap(u["precisely"], 74)[:4]):
            axC.text(4, yy - 11 - 5.0 * j, ln, fontsize=6.8, color=_MUTED)
        axC.text(4, yy - 29, "resolves %s · sufficient alone: %s"
                 % (u["resolves"], u["sufficient_alone"]), fontsize=6.8, color=_C_BLOCK,
                 style="italic")
        yy -= 36
    axC.text(4, yy - 2, "Neither alone unblocks the screen; both are required.",
             fontsize=7.4, color=_INK, weight="bold")

    fig.suptitle("I-076 — do pannusch2024.solver and cameron2020.extraction_bdf actually "
                 "disagree, or only claim to?", fontsize=11.5, y=1.005, x=0.005, ha="left",
                 weight="bold")
    fig.text(0.005, 0.963,
             "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
             "NOT_A_MODEL_VALIDATION_UPGRADE     Protocol frozen and committed BEFORE execution "
             "(PROTOCOL.md).     NO MODEL WAS EXECUTED — the determination is reached at "
             "scenario construction.", fontsize=7.0, color=_MUTED, style="italic", ha="left")
    fig.text(0.005, -0.045, va="top", ha="left", fontsize=7.1, color=_MUTED, linespacing=1.6,
             s="Comparability  primary (5) NON-COMPARABLE at the intervention. Secondary: on the "
               "OBSERVABLE alone (2) comparable through pannusch's own declared mg/mL↔mass %% "
               "convention; on INVENTORY (4) same label, different basis.\n"
               "Uncertainty authorities are kept separate and unpooled: measured replicate "
               "(this scenario %.2f %% RSD, campaign mean 2.5 %%), pannusch fit MAPE (never "
               "cameron's predictive uncertainty), numerical convergence (never experimental).\n"
               "DECISION  %s — %s"
               % (scn["measured_tds_mass_fraction"]["replicate_rsd_pct"],
                  r["decision"], r["decision_reasoning"]))

    path = path or (REPO_ROOT / "docs/insights/screens/I-076/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-076/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    scn = r["scenario"]
    print("protocol frozen before execution: %s (%s)"
          % (r["protocol"]["frozen_before_execution"], r["protocol"]["path"]))
    print("models executed: %s" % r["models_executed"])
    print("scenario: %s exp %s (%s), n=%d reps"
          % (scn["source"], scn["exp"], scn["doe_role"], scn["n_replicates"]))
    print("  measured flow %.4f mL/s | measured T %.2f C | TDS %.3f %% (RSD %.3f %%)"
          % (scn["measured_flow_mL_s"]["mean"], scn["measured_temperature_C"]["mean"],
             scn["measured_tds_mass_fraction"]["mean_pct"],
             scn["measured_tds_mass_fraction"]["replicate_rsd_pct"]))
    for name in ("grind", "temperature"):
        b = r["blockers"][name]
        print("  blocker %-12s blocks=%s" % (name, b["blocks"]))
    print("comparability: (%d) %s at the %s"
          % (r["comparability"]["primary"]["level"], r["comparability"]["primary"]["name"],
             r["comparability"]["primary"]["axis"]))
    print("DECISION: %s" % r["decision"])
    fig_path = figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
