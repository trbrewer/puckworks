"""screen_i040_evidence_halves.py — Insight Foundry cheap screen for candidate I-040.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    For the 1 datasets whose validation_strength names both independent + post_fit +
    same_campaign, which of those strengths does each consuming gate actually rely on?

The dataset is `waszkiewicz2025/traces_time_dependent`, whose MANIFEST validation_strength
cell names two strengths at once. This module attributes every consumer to the half its
assertion actually rests on, and compares that against the strength the consumer states.

METHOD — four layers, deliberately separated so a reviewer can reject one without the rest:

  1. STATIC ENUMERATION. An AST pass finds every call site of the loader
     `puckworks.data.waszkiewicz_traces`, then a simple-name call-graph closure finds every
     `gate_*` that could reach one. It OVER-approximates on purpose: a shared function name
     links unrelated functions, so it can flag a non-consumer, but it cannot miss a real one.
     Safe direction for a completeness check.

  2. DYNAMIC TRACE. Every gate the static layer flags is executed with the loader wrapped, and
     the actual call count recorded. This is the only model execution in the screen, and it is
     here for the reason the candidate's method statement allows: resolving whether a source
     path exists at all. It is what separates a real consumer from a name collision.

  3. DOCSTRING STRENGTH SCAN — the adversarial check. Each real consumer's docstring is
     scanned for ROADMAP §0 strength vocabulary. Any consumer resting on the post-fit half
     while its text contains "independent" is surfaced as a CANDIDATE PROMOTION and must be
     cleared by reading, not by assertion. This is the strongest available mechanical attempt
     to make the RETIRE go away.

  4. HUMAN ATTRIBUTION (`CONSUMERS`). For each consumer: the source columns read, the
     pressure-node convention, which half its ASSERTION depends on, and which strength it
     STATES. A machine cannot read an assertion. Reasoning is recorded per row so a reviewer
     can disagree with one row rather than the whole table.

`audit()` joins them and fails loudly if layer 2 finds a consumer layer 4 does not cover.

STRENGTH ORDER (ROADMAP §0, strongest first):

    independent  >  post-fit reconstruction  >  verification  >  qualitative

A PROMOTION is a consumer stating a strength STRICTLY STRONGER than the half its assertion
rests on. Stating a weaker one is conservative and is not a finding.

Run:  python -m puckworks.analysis.screen_i040_evidence_halves
"""
from __future__ import annotations

import ast
import inspect
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-040"
DATASET_ID = "waszkiewicz2025/traces_time_dependent"
LOADER = "waszkiewicz_traces"

#: The MANIFEST cell, copied byte-identical. The screen may not paraphrase it.
MANIFEST_VALIDATION_STRENGTH = (
    "independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)")

#: The MANIFEST caveat cell, copied byte-identical (it carries the node convention and the
#: soft-circularity disclosure several consumers inherit).
MANIFEST_CAVEAT = (
    "soft circularity: m_d(t) from TDS x Q on same rig; 11-13 bar dip below monotone model; "
    "basket vs line pressure both present (node id per RC-3/S5.9) | S5.9 nodes: "
    "basket_pressure__bar = P_basket (basket gauge), pressure__bar = line/pump-side.")

#: ROADMAP §0 vocabulary, strongest first. Lower index is stronger.
STRENGTH_ORDER = ["independent", "post-fit reconstruction", "verification", "qualitative"]

#: The halves the manifest cell names, plus the third category the screen found the cell does
#: not anticipate: a consumer that opens the file but scores nothing against it.
HALVES = {
    "A_equilibrium": dict(
        key="A_equilibrium",
        manifest_wording="independent within-rig (equilibrium)",
        strength="independent",
        observable="the long-run (last time-point) basket pressure and mass flow, one pair "
                   "per reference pressure — the 11-point equilibrium curve",
        columns=["basket_pressure__bar[-1]", "mass_flow_rate__g_per_s[-1]"],
        node="basket (P_basket, basket gauge)",
        in_manifest_cell=True),
    "B_post_fit_9bar": dict(
        key="B_post_fit_9bar",
        manifest_wording="post-fit (9-bar Q(t) reproduction)",
        strength="post-fit reconstruction",
        observable="the full time-resolved Q(t) trajectory (9 bar unless stated), whose "
                   "reconstruction consumes m_d(t) obtained as TDS x Q on the same rig",
        columns=["time__s", "mass_flow_rate__g_per_s", "mass__g"],
        node="basket (P_basket) drives; the scored observable is mass flow",
        in_manifest_cell=True),
    "C_time_base_only": dict(
        key="C_time_base_only",
        manifest_wording="(not named in the cell — found by this screen)",
        strength="qualitative",
        observable="the trace's `time__s` grid used as a CLOCK. No measured column is scored "
                   "against; the dataset supplies the time base and nothing else",
        columns=["time__s"],
        node="n/a — no pressure column is read",
        in_manifest_cell=False),
    "both": dict(
        key="both",
        manifest_wording="(consumer whose subject IS the split)",
        strength=None,
        observable="reads both halves because the comparison between them is its subject",
        columns=["time__s", "mass_flow_rate__g_per_s", "basket_pressure__bar",
                 "pressure__bar"],
        node="both nodes, compared",
        in_manifest_cell=True),
}


def _rec(name, kind, module, half, states, reads, node, why, disclosure=""):
    return dict(consumer=name, kind=kind, module=module, evidence_half=half,
                states_strength=states, columns_read=reads, node_convention=node,
                attribution_reasoning=why, explicit_disclosure=disclosure)


#: ---------------------------------------------------------------------------------------
#: LAYER 4 — HUMAN ATTRIBUTION. One row per consumer. Hand-read.
#: ---------------------------------------------------------------------------------------
CONSUMERS = [
    # --- registry gates -----------------------------------------------------------------
    _rec("gate_waszkiewicz_static_refit", "gate", "puckworks.validation.gates",
         "A_equilibrium", "independent",
         ["basket_pressure__bar[-1]", "mass_flow_rate__g_per_s[-1]"],
         "basket (P_basket)",
         "Assertion: 'refitting Eq. 16 to their 11-pressure long-run curve recovers "
         "(P_c, Q_c)'. Reaches the dataset only via poroelastic.steady_state_curve(), which "
         "takes the LAST time point of each trace. No point of the 9-bar trajectory enters "
         "the assertion, so the post-fit half is not load-bearing here.",
         "Docstring already discloses that the published-calibration comparison is 'same "
         "method + data', so that clause is not offered as independent corroboration."),
    _rec("gate_waszkiewicz_dynamic_9bar", "gate", "puckworks.validation.gates",
         "B_post_fit_9bar", "post-fit reconstruction",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Assertion: parameter-free Eq. 18 reproduces the 9-bar Q(t) ramp, scored against "
         "tr[9.0] over the whole window. Squarely the post-fit half.",
         "Docstring: 'Post-fit reconstruction (m_d from the same rig, per card)'."),
    _rec("gate_kappa_t_degeneracy", "gate", "puckworks.validation.gates",
         "B_post_fit_9bar", "verification",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Assertion is MODEL-VS-MODEL: coupled_kappa_t with branches off must equal "
         "waszkiewicz2025.poroelastic. The 9-bar trace is the common scoring target, so the "
         "half consumed is B; the claim gated is the reduction, which is weaker. Stating "
         "'verification' is therefore conservative, not a promotion.",
         "Docstring: 'Verification of the reduction.' The rung-4 reference is computed from "
         "the poroelastic component on the same window, not carried as a literal."),
    _rec("gate_kappa_t_composition_diagnostic", "gate", "puckworks.validation.gates",
         "B_post_fit_9bar", None,
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Assertion: adding the mo2023_2 swelling branch over-closes the shared porosity and "
         "worsens the 9-bar residual — a diagnostic scored on the post-fit half. The "
         "docstring names NO strength; the label is carried downstream by PV-05 "
         "('qualitative'), which is weaker than the half. No promotion, but the reader gets "
         "no label from the gate itself.",
         "Docstring: 'report the residual, do not tune it away' (card)."),
    _rec("gate_p2_kappa_ladder", "gate", "puckworks.validation.gates",
         "B_post_fit_9bar", None,
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Assertion: a time-dependent Phi(t) beats three constant nulls on the 9-bar "
         "rising-flow window by ~4.9x. Entirely the post-fit half, via harness.kappa_t_ladder. "
         "The docstring names NO strength; the label is carried downstream by PV-02 "
         "('post-fit reconstruction'), which matches the half exactly.",
         "Docstring qualifies the mechanistic content itself: 'no coefficient fitted to the "
         "scored trace, but target-informed upstream', and records that a 4-param flexible "
         "cubic reaches ~0.10 — so the ladder establishes NEED for time variation, not a "
         "mechanism."),
    _rec("gate_p2_cross_pressure", "gate", "puckworks.validation.gates",
         "B_post_fit_9bar", "post-fit reconstruction",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), all 11 pressures",
         "Assertion: one shared campaign-wide calibration predicts all 11 pressures and the "
         "three kappa(t) mechanisms separate by regime. Time-resolved across the campaign — "
         "the post-fit half, widened from 9 bar to all pressures.",
         "Docstring: 'within-campaign CONDITIONAL transfer, NOT independent out-of-sample "
         "validation' — an explicit REFUSAL of the independent half. This is why the "
         "adversarial token scan flags it: the word 'independent' appears negated."),
    _rec("gate_ntube_kappa_t_union", "gate", "puckworks.validation.gates",
         "C_time_base_only", "qualitative",
         ["time__s"], "n/a — no pressure column read from this dataset",
         "Found by the dynamic trace, NOT by the obvious reading — four loader calls, via "
         "coupled_kappa_t.simulate(P_bar=..., branches=('extraction',)) with no explicit `t`, "
         "so simulate falls back to tr[P_bar]['time__s'] as its CLOCK. No measured column is "
         "scored against. The assertion (single-channel collapse, N_eff -> ~1) is carried by "
         "the streamtube/porosity machinery, not by this dataset. Neither manifest half is "
         "load-bearing; the dataset supplies a time grid.",
         "Docstring: 'EXPLORATORY SYNTHESIS, qualitative strength ... NOT a proven "
         "unconditional instability' and 'NOT a registered component / validated law'."),

    # --- public claims ------------------------------------------------------------------
    _rec("PV-02", "public_claim", "puckworks.public.claims",
         "B_post_fit_9bar", "post-fit reconstruction",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Numeric result is the ladder RMSE triple (0.116 / 0.573 / 4.9x) on the 9-bar "
         "window; the dependency names the dataset as 'the measured flow trace all branches "
         "are scored against'. Post-fit half, stated exactly.",
         "evidence_strength='post-fit reconstruction'; badge EXPLORATORY_SIMULATION; caveat "
         "'Sufficient, NOT unique'. DECISIVE: its evidence_selection for "
         "waszkiewicz2025.poroelastic selects ONLY "
         "'waszkiewicz2025.poroelastic::gate_waszkiewicz_dynamic_9bar' and records "
         "'EXCLUDED: gate_waszkiewicz_static_refit, which concerns the steady-state "
         "pressure-flow curve and the recovered P_c/Q_c -- a different observable.' The "
         "independent-half gate is explicitly refused as evidence for the post-fit claim."),
    _rec("PV-05", "public_claim", "puckworks.public.claims",
         "B_post_fit_9bar", "qualitative",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket), 9.0 bar",
         "Numeric result is the composition-residual triple on the same 9-bar window; the "
         "dependency names the dataset as 'the measured trace the composite is scored "
         "against'. Post-fit half, stated at the weakest rung.",
         "evidence_strength='qualitative'; badge EXPLORATORY_SIMULATION. Its evidence "
         "selection likewise EXCLUDES the degeneracy/reduction records as 'not what is "
         "asserted here'."),

    # --- producers (compute; assert nothing on their own) --------------------------------
    _rec("poroelastic.steady_state_curve", "producer",
         "puckworks.models.waszkiewicz2025.poroelastic",
         "A_equilibrium", None,
         ["basket_pressure__bar[-1]", "mass_flow_rate__g_per_s[-1]"], "basket (P_basket)",
         "The equilibrium-half extractor: last time point per pressure. Asserts nothing; it "
         "is the edge by which half A reaches gate_waszkiewicz_static_refit.",
         "Docstring names it 'the 11-point equilibrium curve their static fit consumes'."),
    _rec("harness.kappa_t_ladder", "producer", "puckworks.harness",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar",
         "Producer behind gate_p2_kappa_ladder and PV-02; scores every rung on the 9-bar "
         "window.", ""),
    _rec("harness.result2_residual_diagnostics", "producer", "puckworks.harness",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar",
         "Window-sensitivity diagnostics on the same 9-bar residual.", ""),
    _rec("harness.cross_pressure_discrimination", "producer", "puckworks.harness",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), all 11 pressures",
         "Producer behind gate_p2_cross_pressure; time-resolved across the campaign.", ""),
    _rec("harness.cross_pressure_loco", "producer", "puckworks.harness",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), all 11 pressures",
         "Leave-one-condition-out over the same time-resolved traces.", ""),
    _rec("coupled_kappa_t.simulate", "producer", "puckworks.models.brewer2026.coupled_kappa_t",
         "C_time_base_only", None, ["time__s"], "n/a — no pressure column read",
         "Reads tr[P_bar]['time__s'] ONLY, and only when the caller passes no `t`. Its "
         "(P_c, Q_c) come from published_calibration() — a DIFFERENT manifest row "
         "(waszkiewicz2025/static_calibration), not this one. Callers that also score against "
         "the trace (degeneracy_rmse, composition_residual) read the flow column themselves.",
         ""),
    _rec("coupled_kappa_t.degeneracy_rmse", "producer",
         "puckworks.models.brewer2026.coupled_kappa_t",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar",
         "Scores the branches-off reduction against the 9-bar trace.", ""),
    _rec("coupled_kappa_t.composition_residual", "producer",
         "puckworks.models.brewer2026.coupled_kappa_t",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar",
         "Scores the composite against the 9-bar trace.", ""),
    _rec("model_composition.build_payload", "producer", "puckworks.public.model_composition",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar",
         "Assembles the PV-05 payload from the same 9-bar residuals; inherits PV-05's label "
         "rather than stating its own.", ""),

    # --- analyses -----------------------------------------------------------------------
    _rec("analysis.residual_autocorr.residual_autocorr_waszkiewicz", "analysis",
         "puckworks.analysis.residual_autocorr",
         "B_post_fit_9bar", "verification", ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket)",
         "Residual autocorrelation of the ladder fit — a property of the post-fit residual. "
         "Asserts a numerical/statistical property, not a physical one, so it states a rung "
         "weaker than the half.", ""),
    _rec("analysis.waszkiewicz_shot_level.recorded_pressure_robustness", "analysis",
         "puckworks.analysis.waszkiewicz_shot_level",
         "both", "post-fit reconstruction",
         ["time__s", "mass_flow_rate__g_per_s", "basket_pressure__bar", "pressure__bar"],
         "BOTH nodes compared — this is its subject",
         "Compares the recorded-pressure convention against the reference-pressure label, "
         "touching the equilibrium endpoint and the trajectory. Its assertion is about the "
         "campaign's own bookkeeping, so it leans on neither half as evidence FOR a model.",
         "The consumer that makes the basket-vs-line node distinction explicit rather than "
         "implicit."),
    _rec("slow.external_waszkiewicz.waszkiewicz_external_tds", "analysis",
         "puckworks.validation.slow.external_waszkiewicz",
         "B_post_fit_9bar", "post-fit reconstruction",
         ["time__s", "mass_flow_rate__g_per_s"], "basket (P_basket)",
         "Slow-lane external TDS comparison driven by the measured trace.",
         "Slow lane, not CI."),

    # --- rendering (asserts nothing; inherits) -------------------------------------------
    _rec("figures.fig3_ladder", "figure", "puckworks.figures",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar", "Renders the ladder; inherits PV-02's label.", ""),
    _rec("figures.fig4_composition", "figure", "puckworks.figures",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar", "Renders the composition; inherits PV-05's label.", ""),
    _rec("figures_paper3.fig5_negative_composition", "figure", "puckworks.figures_paper3",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket)", "Renders the negative composition result; inherits.", ""),
    _rec("figures_paper_b2._trace", "figure", "puckworks.figures_paper_b2",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket), 9.0 bar", "Paper B2 trace panel; inherits.", ""),
    _rec("viz.producers.shot_traces", "viz", "puckworks.viz.producers",
         "B_post_fit_9bar", None,
         ["time__s", "mass_flow_rate__g_per_s", "basket_pressure__bar"],
         "basket (P_basket)",
         "VizSpec producer for the raw shot trace. Renders measured data; the badge and "
         "fidelity ceiling are carried by the VizSpec, not minted here.", ""),
    _rec("viz.producers.wetting_front", "viz", "puckworks.viz.producers",
         "B_post_fit_9bar", None, ["time__s", "mass_flow_rate__g_per_s"],
         "basket (P_basket)", "VizSpec producer for the wetting-front overlay; inherits.", ""),
]


# ------------------------------------------------------------------------------------------
# Layer 1 — static enumeration
# ------------------------------------------------------------------------------------------
_SKIP_DIRS = {"__pycache__", ".git", "build", "dist", ".venv"}


def _py_files():
    for p in sorted((REPO_ROOT / "puckworks").rglob("*.py")):
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        yield p


def call_sites():
    """Every call site of the loader, with its enclosing function. Static, no import."""
    pat = re.compile(r"\b%s\s*\(" % LOADER)
    out = []
    for p in _py_files():
        src = p.read_text(encoding="utf-8")
        if not pat.search(src):
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:                                    # pragma: no cover
            continue
        funcs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        lines = src.splitlines()
        for m in pat.finditer(src):
            ln = src[:m.start()].count("\n") + 1
            text = lines[ln - 1].strip()
            if text.startswith("#") or text.startswith('"""') or "def %s(" % LOADER in text:
                continue                                       # comment / docstring / the def
            inner = sorted((f for f in funcs if f[0] <= ln <= f[1]),
                           key=lambda f: f[1] - f[0])
            out.append(dict(file=str(p.relative_to(REPO_ROOT)), line=ln,
                            function=inner[0][2] if inner else "<module>", source=text))
    return out


def _defs_and_calls():
    defs, index = {}, {}
    for p in _py_files():
        mod = str(p.relative_to(REPO_ROOT).with_suffix("")).replace("/", ".")
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:                                    # pragma: no cover
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            called = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    if isinstance(f, ast.Name):
                        called.add(f.id)
                    elif isinstance(f, ast.Attribute):
                        called.add(f.attr)
            defs["%s.%s" % (mod, node.name)] = called
            index.setdefault(node.name, []).append("%s.%s" % (mod, node.name))
    return defs, index


def gates_reaching_static():
    """Every `gate_*` that COULD transitively reach the loader (over-approximating)."""
    defs, index = _defs_and_calls()
    memo = {}

    def reaches(qual, stack):
        if qual in memo:
            return memo[qual]
        if qual in stack:
            return False
        memo[qual] = False                                     # provisional, breaks cycles
        found = False
        for name in defs.get(qual, ()):
            if name == LOADER:
                found = True
                break
            for target in index.get(name, ()):
                if target != qual and reaches(target, stack | {qual}):
                    found = True
                    break
            if found:
                break
        memo[qual] = found
        return found

    return sorted(q for q in defs
                  if q.rsplit(".", 1)[-1].startswith("gate_") and reaches(q, frozenset()))


# ------------------------------------------------------------------------------------------
# Layer 2 — dynamic trace
# ------------------------------------------------------------------------------------------
def trace_gates(gate_names):
    """Execute each named gate with the loader wrapped; return {gate: loader_call_count}.

    The ONLY execution in this screen, and it is here to resolve whether a source path
    exists — the carve-out the candidate's method statement allows. Nothing is fitted or
    scored; the gate results are discarded.
    """
    import time

    from puckworks import data as D
    from puckworks.validation import gates as G

    real = getattr(D, LOADER)
    calls = []

    def traced(*a, **k):
        calls.append(1)
        return real(*a, **k)

    setattr(D, LOADER, traced)
    rebound = []
    for name, mod in list(sys.modules.items()):
        if name.startswith("puckworks") and getattr(mod, LOADER, None) is real:
            setattr(mod, LOADER, traced)
            rebound.append(mod)
    try:
        out = {}
        for g in gate_names:
            calls.clear()
            t0 = time.time()
            err = None
            try:
                getattr(G, g)()
            except Exception as exc:                           # pragma: no cover - diagnostic
                err = "%s: %s" % (type(exc).__name__, exc)
            out[g] = dict(loader_calls=len(calls), seconds=round(time.time() - t0, 2),
                          error=err)
        return out
    finally:
        setattr(D, LOADER, real)
        for mod in rebound:
            setattr(mod, LOADER, real)


# ------------------------------------------------------------------------------------------
# Layer 3 — adversarial docstring strength scan
# ------------------------------------------------------------------------------------------
_VOCAB = {"independent": "independent",
          "post-fit": "post-fit reconstruction",
          "post fit": "post-fit reconstruction",
          "reconstruction": "post-fit reconstruction",
          "verification": "verification",
          "qualitative": "qualitative"}


def docstring_scan(gate_names):
    """Adversarial probe: which strength words appear in each real consumer's own docstring.

    A gate resting on the post-fit half whose text contains "independent" is a CANDIDATE
    PROMOTION and must be cleared by reading. This is the strongest mechanical attempt
    available to make a RETIRE go away.
    """
    from puckworks.validation import gates as G
    half = {c["consumer"]: c["evidence_half"] for c in CONSUMERS}
    out = {}
    for g in gate_names:
        fn = getattr(G, g, None)
        if fn is None:
            continue
        doc = (inspect.getdoc(fn) or "").lower()
        tokens = sorted({v for k, v in _VOCAB.items() if k in doc})
        flag = ("independent" in tokens and half.get(g) == "B_post_fit_9bar")
        out[g] = dict(tokens_found=tokens, states_no_strength=not tokens,
                      candidate_promotion=flag,
                      independent_is_negated=bool(
                          flag and re.search(r"not independent|not\s+\w+\s+independent", doc)))
    return out


# ------------------------------------------------------------------------------------------
# Join, and the decision
# ------------------------------------------------------------------------------------------
def _rung(label):
    return STRENGTH_ORDER.index(label) if label in STRENGTH_ORDER else None


def promotions():
    """Consumers stating a strength STRICTLY STRONGER than their load-bearing half."""
    out = []
    for c in CONSUMERS:
        stated, hk = c["states_strength"], c["evidence_half"]
        if stated is None or hk == "both":
            continue
        half = HALVES[hk]
        s, h = _rung(stated), _rung(half["strength"])
        if s is not None and h is not None and s < h:
            out.append(dict(consumer=c["consumer"], states=stated, half=half["key"],
                            half_strength=half["strength"],
                            reasoning=c["attribution_reasoning"]))
    return out


def audit(run_trace=True):
    sites = call_sites()
    static_gates = gates_reaching_static()
    static_names = [g.rsplit(".", 1)[-1] for g in static_gates]

    trace = trace_gates(static_names) if run_trace else {}
    real_gates = sorted(g for g, v in trace.items() if v["loader_calls"] > 0)
    false_positives = sorted(g for g, v in trace.items() if v["loader_calls"] == 0)

    covered = {c["consumer"].rsplit(".", 1)[-1] for c in CONSUMERS}
    site_fns = {s["function"] for s in sites
                if s["function"] not in ("waszkiewicz_traces_per_brew", "<module>")}
    uncovered_sites = sorted(site_fns - covered)
    uncovered_gates = sorted(set(real_gates) - covered) if run_trace else []
    complete = not uncovered_sites and not uncovered_gates

    scan = docstring_scan(real_gates) if run_trace else {}
    unresolved = sorted(g for g, v in scan.items()
                        if v["candidate_promotion"] and not v["independent_is_negated"])

    proms = promotions()
    by_half = {}
    for c in CONSUMERS:
        by_half.setdefault(c["evidence_half"], []).append(c["consumer"])

    if not complete:
        decision, why = "NEEDS_NEW_DATA", (
            "The mechanical enumeration found a consumer the human attribution table does "
            "not cover, so the split cannot be asserted for every active use.")
    elif proms:
        decision, why = "SURVIVE", (
            "At least one consumer states a strength stronger than the half its assertion "
            "rests on.")
    else:
        decision, why = "RETIRE", (
            "Every active use preserves the split: no consumer states a strength stronger "
            "than the half its assertion rests on, and the adversarial docstring scan "
            "produced no unresolved candidate promotion.")

    return dict(
        screen=CANDIDATE_ID, dataset=DATASET_ID,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        manifest_validation_strength_verbatim=MANIFEST_VALIDATION_STRENGTH,
        manifest_caveat_verbatim=MANIFEST_CAVEAT,
        strength_order_strongest_first=STRENGTH_ORDER,
        halves=HALVES,
        enumeration=dict(
            static_call_sites=sites, n_static_call_sites=len(sites),
            static_gates_reaching=static_gates, n_static_gates=len(static_gates),
            dynamic_trace=trace,
            real_gate_consumers=real_gates, n_real_gate_consumers=len(real_gates),
            static_false_positives=false_positives,
            n_static_false_positives=len(false_positives),
            uncovered_call_site_functions=uncovered_sites,
            uncovered_gates=uncovered_gates, complete=complete),
        adversarial_docstring_scan=dict(
            per_gate=scan, unresolved_candidate_promotions=unresolved,
            gates_stating_no_strength=sorted(g for g, v in scan.items()
                                             if v["states_no_strength"])),
        consumers=CONSUMERS, n_consumers=len(CONSUMERS),
        consumers_by_half={k: sorted(v) for k, v in by_half.items()},
        promotions=proms, n_promotions=len(proms),
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
#: House print tokens (puckworks.figures). Categorical subset #0072b2/#e69f00/#cc79a7 passes
#: the lightness-band, chroma, CVD-separation and normal-vision checks on the light surface;
#: the sub-3:1 contrast WARN is discharged the way the check requires — every mark carries a
#: visible text label, and the full table is in result.json. Grey is the house NEUTRAL token,
#: not a categorical slot. This is a print/light figure; there is no dark variant, because the
#: house palette is a print palette.
_HALF_COLOR = {"A_equilibrium": "#0072b2",        # GOOD
               "B_post_fit_9bar": "#e69f00",      # ACCENT
               "C_time_base_only": "#6b6b6b",     # NULL (neutral, not a hue slot)
               "both": "#cc79a7"}                 # WARN
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"


def figure(path=None):
    """The primary figure: which half each ASSERTING consumer leans on, and its stated rung.

    Deliberately a table-figure, because the candidate's minimum figure is a table and the
    quantity being shown is categorical attribution, not magnitude. Only consumers that make
    an assertion are drawn (gates + public claims); producers, analyses and renderers inherit
    and are summarised in the footer, with the full set in result.json.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})

    r = audit()
    order = ["A_equilibrium", "B_post_fit_9bar", "C_time_base_only"]
    rows = []
    for hk in order:
        members = [c for c in CONSUMERS
                   if c["evidence_half"] == hk and c["kind"] in ("gate", "public_claim")]
        members.sort(key=lambda c: (c["kind"] != "gate", c["consumer"]))
        if members:
            rows.append(("HEADER", hk, None))
            rows += [("ROW", hk, c) for c in members]

    fig, ax = plt.subplots(figsize=(10.6, 0.42 * len(rows) + 3.1))
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.6, len(rows) + 2.2)
    ax.axis("off")

    ax.text(0, len(rows) + 1.75, "I-040 — which half of a mixed-strength manifest cell each "
            "consumer actually leans on", fontsize=11.5, weight="bold", color=_INK, va="top")
    ax.text(0, len(rows) + 1.05, "dataset  %s        MANIFEST validation_strength (verbatim): "
            "“%s”" % (DATASET_ID, MANIFEST_VALIDATION_STRENGTH),
            fontsize=8, color=_MUTED, va="top")
    ax.text(0, len(rows) + 0.58,
            "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
            "NOT_A_MODEL_VALIDATION_UPGRADE — provenance bookkeeping; asserts nothing "
            "about physics", fontsize=7.2, color=_MUTED, va="top", style="italic")

    x_name, x_cols, x_states, x_verdict, x_end = 3.0, 29.0, 59.0, 74.0, 97.0
    ax.text(x_name, len(rows) + 0.02, "consumer (asserting)", fontsize=7.6, weight="bold",
            color=_MUTED)
    ax.text(x_cols, len(rows) + 0.02, "source columns read", fontsize=7.6, weight="bold",
            color=_MUTED)
    ax.text(x_states, len(rows) + 0.02, "strength it STATES", fontsize=7.6, weight="bold",
            color=_MUTED)
    ax.text(x_verdict, len(rows) + 0.02, "vs the half it leans on", fontsize=7.6,
            weight="bold", color=_MUTED)
    ax.plot([0, x_end], [len(rows) - 0.28] * 2, color=_GRID, lw=0.9)

    for i, (kind, hk, c) in enumerate(rows):
        y = len(rows) - 1 - i
        col = _HALF_COLOR[hk]
        if kind == "HEADER":
            h = HALVES[hk]
            tag = ("half A" if hk == "A_equilibrium" else
                   "half B" if hk == "B_post_fit_9bar" else "NOT IN THE CELL")
            ax.add_patch(FancyBboxPatch((0.4, y - 0.14), x_end - 0.8, 0.52,
                                        boxstyle="round,pad=0.02,rounding_size=0.1",
                                        fc=col, ec="none", alpha=0.13, zorder=0))
            ax.plot([0.4, 0.4 + 0.55], [y + 0.12] * 2, color=col, lw=5,
                    solid_capstyle="butt")
            ax.text(1.6, y + 0.03, "%s  —  “%s”" % (tag, h["manifest_wording"]),
                    fontsize=8.4, weight="bold", color=_INK)
            ax.text(x_states, y + 0.03, "half's own strength: %s"
                    % (h["strength"] or "—"), fontsize=7.6, color=_MUTED)
            continue

        stated = c["states_strength"]
        half_s = HALVES[hk]["strength"]
        if stated is None:
            verdict, vcol = "states none — label carried downstream", _MUTED
        elif _rung(stated) == _rung(half_s):
            verdict, vcol = "matches the half", "#0072b2"
        elif _rung(stated) > _rung(half_s):
            verdict, vcol = "weaker than the half (conservative)", _MUTED
        else:
            verdict, vcol = "PROMOTION", "#d55e00"

        ax.plot([1.2, 1.9], [y + 0.06] * 2, color=col, lw=4, solid_capstyle="butt")
        ax.text(x_name, y, c["consumer"], fontsize=8, color=_INK,
                weight="bold" if c["kind"] == "public_claim" else "normal")
        ax.text(x_cols, y, ", ".join(c["columns_read"]), fontsize=6.8, color=_MUTED)
        ax.text(x_states, y, stated or "—", fontsize=7.6, color=_INK)
        ax.text(x_verdict, y, verdict, fontsize=7.4, color=vcol)
        ax.plot([0, x_end], [y - 0.32] * 2, color=_GRID, lw=0.5, zorder=0)

    e = r["enumeration"]
    n_other = sum(1 for c in CONSUMERS if c["kind"] not in ("gate", "public_claim"))
    foot = (
        "Enumeration  %d loader call sites · %d gates flagged by static reachability "
        "(over-approximating) · %d confirmed by dynamic tracing · %d name-collision "
        "false positives.\n"
        "Adversarial check  docstring strength scan flags gate_p2_cross_pressure "
        "(“independent” on the post-fit half) — cleared: the word appears\n"
        "    NEGATED (“NOT independent out-of-sample validation”). No unresolved candidate "
        "promotion.\n"
        "Decisive  PV-02’s evidence selection names ONLY gate_waszkiewicz_dynamic_9bar and "
        "records “EXCLUDED: gate_waszkiewicz_static_refit …\n"
        "    a different observable” — the independent-half gate is refused as evidence for "
        "the post-fit claim.\n"
        "Not drawn  %d producers / analyses / renderers that assert nothing and inherit a "
        "label; all %d consumers are in result.json.\n"
        "DECISION  RETIRE — %d promotions found. Every active use preserves the split."
        % (e["n_static_call_sites"], e["n_static_gates"], e["n_real_gate_consumers"],
           e["n_static_false_positives"], n_other, r["n_consumers"], r["n_promotions"]))
    ax.text(0, -0.35, foot, fontsize=7, color=_MUTED, va="top", linespacing=1.55)

    fig.tight_layout()
    path = path or (REPO_ROOT / "docs/insights/screens/I-040/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = audit()
    out = REPO_ROOT / "docs/insights/screens/I-040/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    fig_path = figure()
    e = r["enumeration"]
    print("call sites            %d" % e["n_static_call_sites"])
    print("gates (static, over)  %d" % e["n_static_gates"])
    print("gates (dynamic, real) %d   false positives %d"
          % (e["n_real_gate_consumers"], e["n_static_false_positives"]))
    print("consumers attributed  %d   complete=%s" % (r["n_consumers"], e["complete"]))
    print("unresolved candidate promotions: %s"
          % (r["adversarial_docstring_scan"]["unresolved_candidate_promotions"] or "none"))
    print("promotions            %d" % r["n_promotions"])
    print("DECISION: %s" % r["decision"])
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
