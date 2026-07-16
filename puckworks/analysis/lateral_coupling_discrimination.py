"""WP6 — matched physical-vs-proxy discrimination harness for the lateral-coupling FEASIBILITY
model. Determines where the minimal two-node PHYSICAL network and the frozen streamtube SHARE
proxy are MATHEMATICALLY distinguishable on predeclared synthetic cases, and reports candidate
observables + effect sizes. This is NOT Paper-4 work: no N-path network, no PDE, no extraction
clocks, no experimental fitting, no alpha->Lambda mapping, no claim that espresso lies in any
regime or that Lambda is measurable.

Deterministic generator (no timestamps). Outputs under docs/analysis/generated/ (the nearest
established generated-artifact convention to this analysis module; the Paper-3 artifacts live
under docs/paper3_resource/generated/, but this is an analysis product, not a registry export).

    python -m puckworks.analysis.lateral_coupling_discrimination --write
    python -m puckworks.analysis.lateral_coupling_discrimination --verify
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from puckworks.models import lateral_coupling as lc
from puckworks.analysis.lateral_proxy import frozen_two_path_proxy

SCHEMA_VERSION = 1
P_IN = 9.0e5
GEN_REL = "docs/analysis/generated"
_ROOT = Path(__file__).resolve().parents[2]

LAMBDA_GRID = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 5.00, 10.0, 100.0]
ALPHA_GRID = tuple(round(i / 1000.0, 3) for i in range(1001))     # 0.000 .. 1.000
_EPS = 1e-9
BOUNDARY_LAMBDAS = [0.05 - _EPS, 0.05, 0.05 + _EPS, 5.0 - _EPS, 5.0, 5.0 + _EPS]
_RTOL, _ATOL = 1e-10, 1e-12                                        # distinguishability tolerance
PRECISION_FLOORS = [0.01, 0.02, 0.05]                             # 1% / 2% / 5% (scenarios only)


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    description: str
    P_in: float
    g1_top: float
    g1_bot: float
    g2_top: float
    g2_bot: float
    rationale: str

    @property
    def g(self):
        return (self.g1_top, self.g1_bot, self.g2_top, self.g2_bot)


CASES = (
    SyntheticCase("isoresistive_mirror", "path1 top-heavy, path2 the outlet mirror", P_IN,
                  3.0, 1.0, 1.0, 3.0,
                  "equal end-to-end conductance (equal uncoupled outlet shares) but very "
                  "different mid-node pressures -> the primary structural-discrimination case"),
    SyntheticCase("identical_paths", "two identical paths", P_IN, 3.0, 1.0, 3.0, 1.0,
                  "negative control: p1==p2 at every G_lat, q_lat==0, no lateral effect"),
    SyntheticCase("top_contrast_only", "inlet-half asymmetry only", P_IN, 3.0, 1.0, 1.0, 1.0,
                  "unequal end-to-end conductances -> proxy can alter shares (partial mimicry)"),
    SyntheticCase("bottom_contrast_only", "outlet-half asymmetry only", P_IN, 1.0, 3.0, 1.0, 1.0,
                  "outlet-side mirror of top_contrast: inlet- vs outlet-side asymmetry signature"),
    SyntheticCase("general_asymmetric", "positive non-mirror case", P_IN, 4.0, 0.8, 1.5, 2.5,
                  "guards against conclusions being an artifact of exact mirror symmetry"),
    SyntheticCase("scaled_mirror", "isoresistive_mirror x10 conductances", P_IN,
                  30.0, 10.0, 10.0, 30.0,
                  "scaling check: pressures/shares unchanged vs mirror; dimensional flows x10"),
)


def _tol_ok(x, ref):
    return abs(x) <= _ATOL + _RTOL * abs(ref)


def _proxy_outlet_share_1_over_alpha(case):
    """proxy outlet share of path 1 over the whole alpha grid (independent of Lambda)."""
    return np.array([frozen_two_path_proxy(case.P_in, *case.g, a)["proxy_outlet_share_1"]
                     for a in ALPHA_GRID])


def physical_row(case, Lambda):
    """Physical observables at one (case, Lambda), compared against the FROZEN UNCOUPLED
    SHARE-PROXY COMPLETION (analysis.lateral_proxy.frozen_two_path_proxy). Reports the exact
    Xi equalization group and closed-form gap fraction, and BOTH the continuous-alpha and
    grid-alpha share matches so no match is missed between grid points."""
    gax = lc.g_axial_reference(*case.g)
    G = Lambda * gax
    r = lc.model1_two_path(case.P_in, *case.g, G)
    r0 = lc.model1_two_path(case.P_in, *case.g, 0.0)          # uncoupled reference
    gap0 = abs(r0["p1"] - r0["p2"])
    gap = abs(r["p1"] - r["p2"])

    # EXACT equalization group Xi and closed-form gap fraction gap/gap0 = 1/(1+Xi).
    Xi = lc.equalization_number(G, *case.g)
    grf_closed = lc.gap_remaining_fraction(Xi)                # authoritative when gap0 > 0
    grf_numeric = (gap / gap0) if gap0 > 1e-300 else None     # cross-check
    # closed form must reproduce the numerical ratio to machine precision for a nonzero gap
    grf_closed_matches_numeric = (grf_numeric is None) or (abs(grf_closed - grf_numeric)
                                                           <= 1e-9 + 1e-9 * grf_numeric)
    if gap0 <= 1e-300:                                        # symmetric -> no gap to reduce
        gap_class = "not_applicable"
        grf_report = None
    else:
        gap_class = lc.equalization_regime(Xi)               # Xi-driven, not Lambda-driven
        grf_report = grf_closed

    q_in = r["q_in"]
    inlet_share_1 = r["q1_in"] / q_in if q_in else None
    outlet_share_1 = r["q1"] / r["Q"] if r["Q"] else None
    transfer = (outlet_share_1 - inlet_share_1) if (inlet_share_1 is not None) else None
    Q0 = r0["Q"]
    Q_over_Q0 = r["Q"] / Q0 if Q0 else None
    eff0 = r0["effective_conductance"]
    eff_ratio = r["effective_conductance"] / eff0 if eff0 else None
    # fixed-flow transform: to hold Q_target = Q0 the physical/uncoupled inlet-pressure ratio
    p_req_ratio = (Q0 / r["effective_conductance"]) / (Q0 / eff0)

    # uncoupled proxy share of path 1 (s0): the frozen completion's alpha=0 outlet share.
    s0 = frozen_two_path_proxy(case.P_in, *case.g, 0.0)["proxy_outlet_share_1"]
    proxy_share_alpha_invariant = abs(s0 - 0.5) <= _ATOL     # s0 == 0.5 -> proxy share is 0.5
    #                                                          for EVERY alpha (mirror structure)

    # --- CONTINUOUS-alpha share match: s_proxy(alpha) = (1-alpha)*s0 + alpha/2 -----------------
    if proxy_share_alpha_invariant:
        # every alpha gives share 0.5; a match exists iff the physical share is (numerically) 0.5
        alpha_star_continuous = None
        continuous_share_residual = abs(outlet_share_1 - 0.5)
        continuous_share_match_possible = _tol_ok(continuous_share_residual, 1.0)
    else:
        alpha_raw = (outlet_share_1 - s0) / (0.5 - s0)       # exact inverse of the proxy map
        alpha_star_continuous = alpha_raw
        in_unit = (-_ATOL <= alpha_raw <= 1.0 + _ATOL)
        continuous_share_match_possible = in_unit
        clamped = min(max(alpha_raw, 0.0), 1.0)
        s_at = (1.0 - clamped) * s0 + clamped / 2.0
        continuous_share_residual = 0.0 if in_unit else abs(s_at - outlet_share_1)

    # --- GRID-alpha share match (audit sweep only; NEVER the basis of a "no match" verdict) ----
    proxy_share_grid = _proxy_outlet_share_1_over_alpha(case)
    res_grid = np.abs(proxy_share_grid - outlet_share_1)
    j = int(np.argmin(res_grid))
    alpha_star_grid = ALPHA_GRID[j]
    grid_share_residual = float(res_grid[j])

    # --- joint match: BOTH the outlet share (continuous) AND Q/Q0 to tolerance ----------------
    q_res = abs(1.0 - Q_over_Q0)                             # proxy completion holds Q/Q0 == 1
    q_matchable = _tol_ok(q_res, 1.0)
    joint_match_possible = bool(continuous_share_match_possible and q_matchable)
    # mathematically distinguishable: NO continuous alpha reproduces both matched observables.
    distinguishable = not joint_match_possible

    # three DISTINCT notions, kept separate (item 9): the proxy structurally lacks a pressure
    # law, so it can never produce p1/p2/q_lat/distinct-inlet-vs-outlet-share (representational
    # non-equivalence, always true); mathematical distinguishability is the joint-match test
    # above; practical experimental resolvability is OPEN (no instrument/noise model supplied).
    representational_non_equivalence = True
    practical_experimental_resolvability = None

    # effect sizes (material differences in THIS synthetic case; NOT instrument accuracies)
    effects = {
        "Q_over_Q0_minus_1": abs(Q_over_Q0 - 1.0),
        "outlet_share_1_shift": abs(outlet_share_1 - s0),
        "gap_reduction": 0.0 if grf_report is None else (1.0 - grf_report),
        "depthwise_transfer": abs(transfer) if transfer is not None else 0.0,
        "p_required_ratio_dev": abs(p_req_ratio - 1.0),
    }
    material = {k: {"%dpct" % int(f * 100): bool(v > f) for f in PRECISION_FLOORS}
                for k, v in effects.items()}

    def rd(x):
        return None if x is None else round(float(x), 9)

    return {
        "case_id": case.case_id, "lambda_legacy_nominal": Lambda, "G_lat": rd(G),
        "g_axial_reference": rd(gax), "Xi": rd(Xi),
        "p1_over_Pin": rd(r["p1"] / case.P_in), "p2_over_Pin": rd(r["p2"] / case.P_in),
        "pressure_gap_over_Pin": rd(gap / case.P_in),
        "gap_remaining_fraction_closed_form": ("not_applicable" if grf_report is None
                                               else rd(grf_report)),
        "gap_closed_form_matches_numeric": grf_closed_matches_numeric,
        "pressure_gap_class": gap_class,
        "q1_in": rd(r["q1_in"]), "q2_in": rd(r["q2_in"]),
        "q1_out": rd(r["q1"]), "q2_out": rd(r["q2"]),
        "Q": rd(r["Q"]), "Q_over_Q0": rd(Q_over_Q0),
        "effective_conductance_ratio": rd(eff_ratio),
        "q_lat_1to2": rd(r["q_lat_1to2"]),
        "q_lat_over_Q": rd(r["q_lat_1to2"] / r["Q"]) if r["Q"] else None,
        "inlet_share_1": rd(inlet_share_1), "outlet_share_1": rd(outlet_share_1),
        "uncoupled_proxy_share_1": rd(s0),
        "proxy_share_alpha_invariant": proxy_share_alpha_invariant,
        "depthwise_share_transfer_1": rd(transfer),
        "node1_residual": rd(r["node1_residual"]), "node2_residual": rd(r["node2_residual"]),
        "global_residual": rd(r["global_residual"]),
        "condition_number": rd(r["condition_number"]),
        "p_required_physical_over_uncoupled": rd(p_req_ratio),
        # matched frozen-uncoupled-share-proxy-completion comparison
        "alpha_star_continuous": rd(alpha_star_continuous),
        "continuous_share_match_possible": continuous_share_match_possible,
        "continuous_share_residual": rd(continuous_share_residual),
        "alpha_star_grid": alpha_star_grid,
        "grid_share_residual": rd(grid_share_residual),
        "completion_Q_residual": rd(q_res), "completion_Q_matchable": q_matchable,
        "joint_match_possible": joint_match_possible,
        "mathematically_distinguishable": distinguishable,
        "representational_non_equivalence": representational_non_equivalence,
        "practical_experimental_resolvability": practical_experimental_resolvability,
        "material_effect_scenarios": material,
    }


def _build():
    rows = [physical_row(c, lam) for c in CASES for lam in LAMBDA_GRID]
    boundary = [physical_row(c, lam) for c in CASES for lam in BOUNDARY_LAMBDAS]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "GENERATED": "puckworks.analysis.lateral_coupling_discrimination --write (do not hand-edit)",
        "scope": "FEASIBILITY discrimination only — NOT Paper-4; no experimental fit, no "
                 "alpha->Lambda map, no transverse-permeability estimate, no claim espresso lies "
                 "in any regime or that Lambda/Xi is measurable.",
        "comparator": "frozen uncoupled share-proxy completion "
                      "(analysis.lateral_proxy.frozen_two_path_proxy): the exact ntube share "
                      "homogenizer w<-(1-alpha)*w+alpha applied to unit-mean relative flows under "
                      "the uncoupled completion (Q/Q0==1, one share through the whole depth, NO "
                      "pressure law). NOT the complete dynamic streamtube model.",
        "models": {
            "physical": "two-node steady Darcy network (models.lateral_coupling.model1_two_path)",
            "proxy": "frozen uncoupled share-proxy completion (frozen_two_path_proxy); has NO "
                     "pressure law and holds total flow at the uncoupled value.",
        },
        "sign_convention": "q_lat_1to2 = G_lat*(p1-p2) > 0 means flow path1 -> path2",
        "g_axial_reference_definition": "mean of the two uncoupled end-to-end series "
                                        "conductances g_series(g_top,g_bot)=g_top*g_bot/(g_top+g_bot)",
        "equalization_number_definition": "Xi = G_lat*(1/A1 + 1/A2), Ai = gi_top+gi_bot; EXACT: "
                                          "for a nonzero uncoupled gap, gap/gap0 = 1/(1+Xi). The "
                                          "pressure_gap_class is driven by Xi (5%%/95%% cutoffs: "
                                          "Xi<%.10g unchanged, Xi>=%g homogenized)."
                                          % (lc.XI_UNCHANGED, lc.XI_HOMOGENIZED),
        "P_in": P_IN,
        "lambda_note": "lambda_legacy_nominal is the axial-conductance-ratio grouping (WP6.3). "
                       "Its 0.05 and 5 boundaries are LEGACY / PROVISIONAL NOMINAL labels kept "
                       "for continuity — neither validated nor universal, and NOT the pressure "
                       "classifier (Xi is).",
        "lambda_grid": LAMBDA_GRID,
        "alpha_grid": {"start": 0.0, "stop": 1.0, "step": 0.001, "n": len(ALPHA_GRID),
                       "role": "audit sweep only; continuous alpha_star is the authoritative "
                               "share-match test so no match is missed between grid points"},
        "cases": [c.__dict__ for c in CASES],
        "rows": rows,
        "boundary_rows": boundary,
        "three_distinct_notions": {
            "representational_non_equivalence": "the proxy structurally cannot produce a pressure "
                "law (p1/p2/q_lat/distinct inlet-vs-outlet share) — always true, model-structural.",
            "mathematical_distinguishability": "no continuous alpha reproduces BOTH the outlet "
                "share and Q/Q0 — the joint_match_possible test.",
            "practical_experimental_resolvability": "OPEN — requires an instrument/noise model "
                "that is NOT supplied here; never inferred from a nonzero synthetic difference.",
        },
        "distinguishability_tolerance": {"rtol": _RTOL, "atol": _ATOL},
    }
    blob = json.dumps(doc, sort_keys=True, ensure_ascii=False)
    doc["content_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return doc


def _csv(doc):
    cols = ["case_id", "lambda_legacy_nominal", "Xi", "G_lat", "g_axial_reference",
            "p1_over_Pin", "p2_over_Pin", "pressure_gap_over_Pin",
            "gap_remaining_fraction_closed_form", "gap_closed_form_matches_numeric",
            "pressure_gap_class", "Q_over_Q0", "effective_conductance_ratio", "q_lat_1to2",
            "q_lat_over_Q", "inlet_share_1", "outlet_share_1", "uncoupled_proxy_share_1",
            "proxy_share_alpha_invariant", "depthwise_share_transfer_1",
            "p_required_physical_over_uncoupled", "alpha_star_continuous",
            "continuous_share_match_possible", "continuous_share_residual", "alpha_star_grid",
            "grid_share_residual", "completion_Q_residual", "completion_Q_matchable",
            "joint_match_possible", "mathematically_distinguishable",
            "representational_non_equivalence", "global_residual", "condition_number"]
    buf = io.StringIO()
    buf.write("# GENERATED by puckworks.analysis.lateral_coupling_discrimination --write; "
              "do not hand-edit.\n")
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in doc["rows"]:
        w.writerow({k: r.get(k) for k in cols})
    return buf.getvalue()


def _md(doc):
    L = ["<!-- GENERATED by puckworks.analysis.lateral_coupling_discrimination --write; "
         "do not hand-edit. -->",
         "# Lateral coupling — physical-vs-proxy discrimination (feasibility)", "",
         "**Scope / non-claims.** " + doc["scope"], "",
         "## Definitions",
         "- Physical: " + doc["models"]["physical"],
         "- Comparator: " + doc["comparator"],
         "- Sign: " + doc["sign_convention"],
         "- Reference conductance: " + doc["g_axial_reference_definition"],
         "- Equalization number: " + doc["equalization_number_definition"],
         "- alpha and Lambda/Xi are INDEPENDENT parameters — no alpha=f(Lambda) mapping is used.",
         "- **Three distinct notions, never conflated:** representational non-equivalence "
         "(structural) · mathematical distinguishability (the joint-match test) · practical "
         "experimental resolvability (**OPEN** — no instrument/noise model here).",
         "", "## Why the comparison is matched",
         "Both start from the same two uncoupled paths; the frozen uncoupled share-proxy",
         "completion homogenizes their flow SHARES (holding total flow at the uncoupled value),",
         "the physical model adds a transverse PRESSURE conductance. The outlet-share match is",
         "solved EXACTLY in continuous alpha (`alpha_star_continuous`); the 0.001 alpha grid is an",
         "audit sweep only, so no match is ever missed between grid points.", "",
         "## Synthetic cases",
         "| case | g1_top | g1_bot | g2_top | g2_bot | why |", "|---|---|---|---|---|---|"]
    for c in doc["cases"]:
        L.append("| %s | %g | %g | %g | %g | %s |" % (c["case_id"], c["g1_top"], c["g1_bot"],
                                                       c["g2_top"], c["g2_bot"], c["rationale"]))
    L += ["", "## Main results (per case × Lambda_legacy_nominal)",
          "`gap_frac` = 1/(1+Xi) (closed form). `a*_cont` is the exact continuous share-match "
          "alpha; `share_match` is whether it lies in [0,1]; `joint` folds in Q/Q0.",
          "| case | Lambda(nom) | Xi | gap_frac | gap_class | Q/Q0 | out_share | s0 | transfer | "
          "a*_cont | share_match | joint | distinguishable |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in doc["rows"]:
        L.append("| %s | %g | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["case_id"], r["lambda_legacy_nominal"], r["Xi"],
            r["gap_remaining_fraction_closed_form"], r["pressure_gap_class"],
            r["Q_over_Q0"], r["outlet_share_1"], r["uncoupled_proxy_share_1"],
            r["depthwise_share_transfer_1"], r["alpha_star_continuous"],
            r["continuous_share_match_possible"], r["joint_match_possible"],
            r["mathematically_distinguishable"]))
    # headline synthesis
    n_dist = sum(1 for r in doc["rows"] if r["mathematically_distinguishable"])
    L += ["", "## Fixed-pressure vs fixed-flow signatures",
          "Because the network is linear in P_in, the fixed-pressure total-flow rise (Q/Q0>1)",
          "maps to a fixed-flow pressure drop (p_required_physical/uncoupled<1). The frozen",
          "uncoupled share-proxy completion has NO pressure law and holds Q/Q0==1; any proxy",
          "pressure would come from retaining the independent axial paths, not from the",
          "homogenizing operator.", "",
          "## The mirror case and s0 = 0.5",
          "For `isoresistive_mirror` (and `scaled_mirror`) the uncoupled proxy share s0 is exactly",
          "0.5, so `s_proxy(alpha) = (1-alpha)*0.5 + alpha/2 = 0.5` for EVERY alpha — the proxy",
          "share is alpha-invariant. Any physical outlet share != 0.5 is therefore unreachable by",
          "the proxy at any alpha: the structural reason the mirror is a strong share-",
          "discrimination case (not an artifact of the grid).", "",
          "## Xi vs the legacy nominal Lambda band",
          "The `pressure_gap_class` column is driven by the EXACT Xi (5%/95% cutoffs). The",
          "0.05–5 `lambda_legacy_nominal` boundaries are legacy provisional nominal labels ONLY —",
          "not a validated or universal transition band, and not the pressure classifier.", "",
          "## Conservation & scaling", "Every row's `global_residual` ~ 0 and "
          "`gap_closed_form_matches_numeric` is true (the 1/(1+Xi) identity is verified against "
          "the solved gap). `scaled_mirror` reproduces `isoresistive_mirror` shares with 10× "
          "flows.", "",
          "## Candidate observables (feasibility, synthetic effect sizes only)",
          "- total flow ratio Q/Q0 (equivalently the fixed-flow pressure ratio);",
          "- depthwise inlet-vs-outlet share transfer (identically 0 for the proxy);",
          "- outlet-share shift for asymmetric cases.",
          "Per-observable 1%/2%/5% flags in JSON `material_effect_scenarios` mark where the effect",
          "is **material in the selected synthetic case** — they are NOT instrument accuracies and",
          "NOT an accessible-experiment claim.",
          "", "## Go / no-go",
          "- **%d / %d** case×Lambda rows are mathematically distinguishable (no continuous alpha"
          " reproduces both the outlet share and Q/Q0)." % (n_dist, len(doc["rows"])),
          "- `isoresistive_mirror` (uncoupled proxy share s0 = 0.5, so the proxy share is",
          "  alpha-invariant) is distinguishable through total flow / depthwise transfer once",
          "  coupled — the frozen uncoupled share-proxy completion cannot represent it.",
          "- `identical_paths` is NOT distinguishable (correct negative control: no lateral effect).",
          "- **The claim, stated precisely:** the minimal physical network is *mathematically",
          "  distinguishable from the frozen uncoupled share-proxy completion on predeclared",
          "  synthetic cases*. This is representational/mathematical only — NOT a claim that any",
          "  effect is experimentally resolvable, that Lambda/Xi is measurable, or that espresso",
          "  sits in any regime. The measurability and identifiability go/no-go boxes stay OPEN;",
          "  Paper 4 is NOT authorized.",
          ""]
    return "\n".join(L) + "\n"


def generate():
    doc = _build()
    return {
        "lateral_coupling_discrimination.json": json.dumps(doc, indent=2, sort_keys=True) + "\n",
        "lateral_coupling_discrimination.csv": _csv(doc),
        "lateral_coupling_discrimination.md": _md(doc),
    }


def write(root=_ROOT):
    out = Path(root) / GEN_REL
    out.mkdir(parents=True, exist_ok=True)
    for name, content in generate().items():
        (out / name).write_text(content, encoding="utf-8")
    return sorted(generate())


def verify(root=_ROOT):
    out = Path(root) / GEN_REL
    stale = []
    for name, content in generate().items():
        p = out / name
        if not p.exists() or p.read_text(encoding="utf-8") != content:
            stale.append(name)
    return stale


def main(argv=None):
    ap = argparse.ArgumentParser(prog="puckworks.analysis.lateral_coupling_discrimination")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        print("wrote:", write())
        return 0
    stale = verify()
    if stale:
        print("STALE (run --write):", stale)
        return 1
    print("generated lateral-coupling discrimination artifacts are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
