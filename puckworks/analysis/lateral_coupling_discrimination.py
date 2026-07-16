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
    """Physical observables at one (case, Lambda), plus the four discrimination tests."""
    gax = lc.g_axial_reference(*case.g)
    G = Lambda * gax
    r = lc.model1_two_path(case.P_in, *case.g, G)
    r0 = lc.model1_two_path(case.P_in, *case.g, 0.0)          # uncoupled reference
    gap0 = abs(r0["p1"] - r0["p2"])
    gap = abs(r["p1"] - r["p2"])
    grf = (gap / gap0) if gap0 > 1e-300 else None            # gap_remaining_fraction
    reduction = None if grf is None else (1.0 - grf)
    if grf is None:
        gap_class = "not_applicable"
    elif reduction < 0.05:
        gap_class = "pressure_gap_unchanged"
    elif reduction >= 0.95:
        gap_class = "pressure_gap_homogenized"
    else:
        gap_class = "pressure_gap_transition"

    q_in = r["q_in"]
    inlet_share_1 = r["q1_in"] / q_in if q_in else None
    outlet_share_1 = r["q1"] / r["Q"] if r["Q"] else None
    transfer = (outlet_share_1 - inlet_share_1) if (inlet_share_1 is not None) else None
    Q0 = r0["Q"]
    Q_over_Q0 = r["Q"] / Q0 if Q0 else None
    eff0 = r0["effective_conductance"]
    eff_ratio = r["effective_conductance"] / eff0 if eff0 else None
    # Test 4 — fixed-flow transform: Q_target = Q0 -> required inlet pressures
    p_req_phys = Q0 / r["effective_conductance"]
    p_req_unc = Q0 / eff0
    p_req_ratio = p_req_phys / p_req_unc

    # Test 1 — outlet-share match over the full alpha grid
    proxy_share = _proxy_outlet_share_1_over_alpha(case)
    res_share = np.abs(proxy_share - outlet_share_1)
    j = int(np.argmin(res_share))
    alpha_star_share = ALPHA_GRID[j]
    min_share_res = float(res_share[j])
    exact_share_match = _tol_ok(min_share_res, outlet_share_1)

    # Test 2 — share + Q/Q0 completion (the Q-component is alpha-independent: proxy Q/Q0 == 1)
    q_res = abs(1.0 - Q_over_Q0)
    q_matchable = _tol_ok(q_res, 1.0)
    # mathematically distinguishable: no alpha reproduces BOTH observables to tolerance
    distinguishable = not (exact_share_match and q_matchable)

    # practical-resolution scenarios (effect sizes vs hypothetical floors; NOT instrument specs)
    effects = {
        "Q_over_Q0_minus_1": abs(Q_over_Q0 - 1.0),
        "outlet_share_1_shift": abs(outlet_share_1 - (r0["q1"] / Q0)),
        "gap_reduction": 0.0 if reduction is None else reduction,
        "depthwise_transfer": abs(transfer) if transfer is not None else 0.0,
        "p_required_ratio_dev": abs(p_req_ratio - 1.0),
    }
    resolves = {k: {"%dpct" % int(f * 100): bool(v > f) for f in PRECISION_FLOORS}
                for k, v in effects.items()}

    def rd(x):
        return None if x is None else round(float(x), 9)

    return {
        "case_id": case.case_id, "lambda": Lambda, "G_lat": rd(G), "g_axial_reference": rd(gax),
        "p1_over_Pin": rd(r["p1"] / case.P_in), "p2_over_Pin": rd(r["p2"] / case.P_in),
        "pressure_gap_over_Pin": rd(gap / case.P_in),
        "gap_remaining_fraction": ("not_applicable" if grf is None else rd(grf)),
        "pressure_gap_class": gap_class,
        "q1_in": rd(r["q1_in"]), "q2_in": rd(r["q2_in"]),
        "q1_out": rd(r["q1"]), "q2_out": rd(r["q2"]),
        "Q": rd(r["Q"]), "Q_over_Q0": rd(Q_over_Q0),
        "effective_conductance_ratio": rd(eff_ratio),
        "q_lat_1to2": rd(r["q_lat_1to2"]), "q_lat_over_Q": rd(r["q_lat_1to2"] / r["Q"]) if r["Q"] else None,
        "inlet_share_1": rd(inlet_share_1), "outlet_share_1": rd(outlet_share_1),
        "depthwise_share_transfer_1": rd(transfer),
        "node1_residual": rd(r["node1_residual"]), "node2_residual": rd(r["node2_residual"]),
        "global_residual": rd(r["global_residual"]),
        "condition_number": rd(r["condition_number"]),
        "p_required_physical_over_uncoupled": rd(p_req_ratio),
        # matched proxy comparison
        "alpha_star_share": alpha_star_share, "min_share_residual": rd(min_share_res),
        "exact_share_match_exists": exact_share_match,
        "completion_Q_residual": rd(q_res), "completion_Q_matchable": q_matchable,
        "mathematically_distinguishable": distinguishable,
        "precision_scenarios": resolves,
    }


def _build():
    rows = [physical_row(c, lam) for c in CASES for lam in LAMBDA_GRID]
    boundary = [physical_row(c, lam) for c in CASES for lam in BOUNDARY_LAMBDAS]
    doc = {
        "schema_version": SCHEMA_VERSION,
        "GENERATED": "puckworks.analysis.lateral_coupling_discrimination --write (do not hand-edit)",
        "scope": "FEASIBILITY discrimination only — NOT Paper-4; no experimental fit, no "
                 "alpha->Lambda map, no claim espresso lies in any regime or that Lambda is "
                 "measurable.",
        "models": {
            "physical": "two-node steady Darcy network (models.lateral_coupling.model1_two_path)",
            "proxy": "frozen streamtube share homogenizer w<-(1-alpha)*w+alpha "
                     "(analysis.lateral_proxy.frozen_two_path_proxy); has NO pressure law.",
        },
        "sign_convention": "q_lat_1to2 = G_lat*(p1-p2) > 0 means flow path1 -> path2",
        "g_axial_reference_definition": "mean of the two uncoupled end-to-end series "
                                        "conductances g_series(g_top,g_bot)=g_top*g_bot/(g_top+g_bot)",
        "P_in": P_IN,
        "lambda_grid": LAMBDA_GRID,
        "alpha_grid": {"start": 0.0, "stop": 1.0, "step": 0.001, "n": len(ALPHA_GRID)},
        "cases": [c.__dict__ for c in CASES],
        "rows": rows,
        "boundary_rows": boundary,
        "regime_labels_note": "the 0.05/5 Lambda labels are PROVISIONAL pressure-equalization "
                              "descriptors, NOT a proved proxy-discrimination theorem; see the "
                              "pressure_gap_class + mathematically_distinguishable columns.",
        "distinguishability_tolerance": {"rtol": _RTOL, "atol": _ATOL},
    }
    blob = json.dumps(doc, sort_keys=True, ensure_ascii=False)
    doc["content_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return doc


def _csv(doc):
    cols = ["case_id", "lambda", "G_lat", "g_axial_reference", "p1_over_Pin", "p2_over_Pin",
            "pressure_gap_over_Pin", "gap_remaining_fraction", "pressure_gap_class",
            "Q_over_Q0", "effective_conductance_ratio", "q_lat_1to2", "q_lat_over_Q",
            "inlet_share_1", "outlet_share_1", "depthwise_share_transfer_1",
            "p_required_physical_over_uncoupled", "alpha_star_share", "min_share_residual",
            "exact_share_match_exists", "completion_Q_residual", "completion_Q_matchable",
            "mathematically_distinguishable", "global_residual", "condition_number"]
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
         "- Proxy: " + doc["models"]["proxy"],
         "- Sign: " + doc["sign_convention"],
         "- Reference conductance: " + doc["g_axial_reference_definition"],
         "- alpha and Lambda are INDEPENDENT parameters — no alpha=f(Lambda) mapping is used.",
         "", "## Why the comparison is matched",
         "Both start from the same two uncoupled paths; the proxy homogenizes their flow SHARES,",
         "the physical model adds a transverse PRESSURE conductance. For every physical Lambda we",
         "search the whole alpha grid for any proxy match.", "",
         "## Synthetic cases",
         "| case | g1_top | g1_bot | g2_top | g2_bot | why |", "|---|---|---|---|---|---|"]
    for c in doc["cases"]:
        L.append("| %s | %g | %g | %g | %g | %s |" % (c["case_id"], c["g1_top"], c["g1_bot"],
                                                       c["g2_top"], c["g2_bot"], c["rationale"]))
    L += ["", "## Main results (per case × Lambda)",
          "| case | Lambda | gap_frac | gap_class | Q/Q0 | outlet_share_1 | transfer | "
          "alpha* | share_res | Q_res | distinguishable |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in doc["rows"]:
        L.append("| %s | %g | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["case_id"], r["lambda"], r["gap_remaining_fraction"], r["pressure_gap_class"],
            r["Q_over_Q0"], r["outlet_share_1"], r["depthwise_share_transfer_1"],
            r["alpha_star_share"], r["min_share_residual"], r["completion_Q_residual"],
            r["mathematically_distinguishable"]))
    # headline synthesis
    mirror = [r for r in doc["rows"] if r["case_id"] == "isoresistive_mirror" and r["lambda"] > 0]
    ident = [r for r in doc["rows"] if r["case_id"] == "identical_paths"]
    n_dist = sum(1 for r in doc["rows"] if r["mathematically_distinguishable"])
    L += ["", "## Fixed-pressure vs fixed-flow signatures",
          "Because the network is linear in P_in, the fixed-pressure total-flow rise (Q/Q0>1)",
          "maps to a fixed-flow pressure drop (p_required_physical/uncoupled<1). The share proxy",
          "alone has NO pressure law; any proxy pressure comes from retaining the independent",
          "axial paths (the uncoupled completion), not from the homogenizing operator.", "",
          "## Inside vs outside the provisional 0.05–5 Lambda band",
          "The `pressure_gap_class` column shows where the *pressure gap* actually transitions;",
          "compare it to the nominal Lambda labels — they do not coincide for every case.", "",
          "## Conservation & scaling", "Every row's `global_residual` ~ 0 (see CSV). "
          "`scaled_mirror` reproduces `isoresistive_mirror` pressures/shares with 10× flows.", "",
          "## Candidate observables (feasibility, synthetic effect sizes only)",
          "- total flow ratio Q/Q0 (equivalently the fixed-flow pressure ratio);",
          "- depthwise inlet-vs-outlet share transfer (identically 0 for the proxy);",
          "- outlet-share shift for asymmetric cases.",
          "Per-observable 1%/2%/5% *scenario* flags are in the JSON `precision_scenarios` — these",
          "are sensitivity scenarios, NOT instrument accuracies or an accessible-experiment claim.",
          "", "## Go / no-go",
          "- **%d / %d** case×Lambda rows are mathematically distinguishable (no alpha reproduces"
          " both the outlet share and Q/Q0)." % (n_dist, len(doc["rows"])),
          "- `isoresistive_mirror` (equal outlet shares, unequal mid-pressures) is distinguishable",
          "  purely through total flow / depthwise transfer once Lambda>0 — the share-only proxy",
          "  cannot see it.",
          "- `identical_paths` is NOT distinguishable (correct negative control: no lateral effect).",
          "- This is **synthetic / mathematical** distinguishability. It does NOT establish that",
          "  Lambda is experimentally measurable or that espresso sits in any regime. The",
          "  measurability and identifiability go/no-go boxes stay OPEN; Paper 4 is NOT authorized.",
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
