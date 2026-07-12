"""angeloni_bracket.py — angeloni2023 multi-species bracket (NOT run in CI).

A DATA-ONLY bracketing check (NOT a runtime port of the angeloni FeFlow coupled
solver, which the card says to skip). It asks: for the species our chain can
currently produce -- total solids / TDS via a registered extraction runtime
(cameron2020) -- does matched-(p, grind) output land within the angeloni
per-condition TS ranges? It REPORTS per-condition hits/misses; it does NOT
pass/fail hard, because cross-machine transfer is expected to be imperfect and
the misses are the informative part.

Validation strength: INDEPENDENT -- angeloni is a different machine (Simonelli/VA
+ Mythos), coffee (Arabica/Robusta blends), and basket (VST 20 g) than pannusch's
fit or cameron's EK43 calibration. TS (g/100 mL) ~ TDS (%). Cameron is isothermal,
so we match p and grind only; temperature is NOT matched (a labelled limitation).
The granulometry -> EK43 grind map is an APPROXIMATE cross-grinder guess (Mythos
O/C/F -> gs), explicitly NOT calibrated.

Run:  python -m puckworks.validation.slow.angeloni_bracket
"""
import numpy as np

# approximate, UNCALIBRATED cross-grinder map (Mythos granulometry -> EK43 gs)
_GRIND_MAP = {"F": 1.3, "O": 1.9, "C": 2.4}


def gate_angeloni_multispecies_bracket(p_bar=9.0, dose_g=20.0, bev_g=40.0):
    """Bracket cameron TDS against the angeloni per-granulometry TS ranges.
    Returns per-granulometry hit/miss (+ direction) and the grind-ordering check.
    REPORT semantics: 'bracketed' counts hits; a systematic miss is a finding,
    not a failure."""
    from puckworks.models.cameron2020 import extraction_bdf as cam
    from puckworks import data as d
    ts = d.angeloni_total_solids()
    rows = []
    cam_tds = {}
    for r_, gs in _GRIND_MAP.items():
        sh = cam.simulate_shot(gs, p_bar=p_bar, m_in=dose_g / 1000, m_out=bev_g / 1000)
        vals = [x["TS_g_100mL"] for x in ts if x["granulometry"] == r_]
        lo, hi = float(min(vals)), float(max(vals))
        cam_tds[r_] = float(sh.tds)
        hit = lo <= sh.tds <= hi
        rows.append(dict(granulometry=r_, gs=gs, cameron_tds=round(float(sh.tds), 2),
                         angeloni_ts_lo=round(lo, 2), angeloni_ts_hi=round(hi, 2),
                         bracketed=bool(hit),
                         direction=("in" if hit else ("low" if sh.tds < lo else "high"))))
    # grind-ordering: both should rise toward fine (F > O > C)
    order_cam = cam_tds["F"] > cam_tds["O"] > cam_tds["C"]
    order_ang = (np.mean([x["TS_g_100mL"] for x in ts if x["granulometry"] == "F"])
                 > np.mean([x["TS_g_100mL"] for x in ts if x["granulometry"] == "O"])
                 > np.mean([x["TS_g_100mL"] for x in ts if x["granulometry"] == "C"]))
    n_hit = sum(r["bracketed"] for r in rows)
    all_low = all(r["direction"] == "low" for r in rows)
    return dict(per_granulometry=rows, n_bracketed=n_hit, n_conditions=len(rows),
                grind_ordering_matches=bool(order_cam and order_ang),
                cameron_reads_low_systematically=bool(all_low),
                strength="independent (different machine/coffee/basket than the fits)",
                note="cross-machine bracket; species = TS/TDS. Cameron reproduces the "
                     "finer->higher grind ordering but reads ~2-4 TDS pts LOW vs "
                     "angeloni -- the SAME direction as the egidi bracket (ANALYSIS_P2 "
                     "2.1). Misses are the finding, not a gate failure.")


def gate_pannusch_angeloni_species_bracket(T_C=93.4, flow_mL_s=1.6, t_shot_s=25.0):
    """PER-SPECIES bracket: pannusch2024 (multi-solute, T/flow-resolved kinetics)
    forward-predicted cup concentrations vs the angeloni per-species measured
    RANGES. Unlike cameron (single lumped solute -> TDS only), pannusch produces
    caffeine (CF), trigonelline (TR), 5CQA, and TDS. Blind forward run (cl1
    cancels in the normalized solver, verified) at a matched espresso condition
    (T on-grid, flow ~beverage/tau, grind 1.7). angeloni bioactives are g/L =
    mg/mL (pannusch's units); TS g/100 mL = pannusch TDS(mg/mL)/10.

    Report semantics (not hard pass/fail): reports per-species hits/misses. The
    finding is that pannusch's kinetics -- fit to a DIFFERENT machine/coffee --
    land INSIDE the angeloni envelope for all four species (near the low edge),
    where cameron's TDS reads low. INDEPENDENT strength."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); ts = d.angeloni_total_solids()
    params = ps._solute_params()
    # (pannusch solute -> angeloni column, unit conversion to angeloni units, source)
    spec_map = {"caffeine": ("CF", 1.0, bio), "trigonelline": ("TR", 1.0, bio),
                "5CQA": ("5CQA", 1.0, bio), "tds": ("TS_g_100mL", 0.1, ts)}
    rows = []
    for sol, (col, conv, src) in spec_map.items():
        pred = float(ps.simulate_fractions(T_C, flow_mL_s, [0.0, t_shot_s],
                                           params[sol], cl1=1.0)[0]) * conv
        vals = [x[col] for x in src]
        lo, hi = float(min(vals)), float(max(vals))
        hit = lo <= pred <= hi
        rows.append(dict(pannusch_solute=sol, angeloni_species=col,
                         predicted=round(pred, 2), range_lo=round(lo, 2),
                         range_hi=round(hi, 2), bracketed=bool(hit),
                         direction=("in" if hit else ("low" if pred < lo else "high"))))
    n_hit = sum(r["bracketed"] for r in rows)
    return dict(per_species=rows, n_bracketed=n_hit, n_species=len(rows),
                strength="independent (different machine/coffee/basket than pannusch's fit)",
                note="pannusch (multi-solute kinetics) brackets all four species in "
                     "the angeloni envelope, near the low edge -- vs cameron's TDS "
                     "reading low. Envelope is wide (66 shots x conditions x variety) "
                     "so this is a regime check, not a per-condition validation.")


def _flow_of_p(p_bar, T_C=None):
    """CRUDE p->flow map: 40 g over tau(p), tau interpolated 35 s@6 bar -> 13 s@12
    bar (angeloni's stated range). Ignores T and mis-attributes the FULL tau range
    (which spans all conditions) to p alone -- the baseline the refinement fixes."""
    return 40.0 / float(np.interp(p_bar, [6, 12], [35, 13]))


# refined Darcy-consistent p->flow: q ~ p / mu(T). Cleaner (p,T) dependence than
# the crude linear-tau map; anchored to a physical espresso point (40 g / ~24 s at
# 9 bar, 93.4 C), NOT fitted to the angeloni concentrations.
_Q_REF, _P_REF, _T_REF = 1.67, 9.0, 93.4


def _flow_darcy(p_bar, T_C):
    """Refined flow map: Darcy q = q_ref * (p/p_ref) * (mu(T_ref)/mu(T)), with
    mu from the registered pannusch water-viscosity closure. Higher T -> lower mu
    -> higher flow. Still an assumption (single anchor, granulometry O only), but
    physically grounded, not fitted."""
    from puckworks.models.pannusch2024 import closures as pc
    mu = pc.water_viscosity(T_C + 273.15)
    mu_ref = pc.water_viscosity(_T_REF + 273.15)
    return _Q_REF * (p_bar / _P_REF) * (mu_ref / mu)


def gate_pannusch_angeloni_per_condition(t_shot_s=25.0, flow_map="darcy"):
    """PER-CONDITION pannusch vs angeloni (the demanding test the wide-envelope
    bracket is NOT). For granulometry O (~ pannusch grind 1.7), across the 9
    on-grid (T,p) points per variety, predict pannusch cup concentration
    (blind = pannusch's own coffee inventory; and inventory-MATCHED using
    angeloni Table 7 C0_s for CF/TR) and score per-condition MAPE vs each angeloni
    shot, plus the response-shape correlation.

    flow_map: 'darcy' (refined _flow_darcy, q ~ p/mu(T); default) or 'tau' (the
    crude _flow_of_p baseline). The refinement closes PART of the gap: the crude
    map over-attributed flow to high pressure, so 'darcy' cuts the overall blind
    MAPE ~31% -> ~26% (the residence-time component). The residual ~26% is
    cross-coffee INVENTORY + KINETIC mismatch, which no flow map can fix:
    inventory-matching helps caffeine but HURTS trigonelline. INDEPENDENT,
    per-condition. NOTE: ~20 s of PDE solves (slow; hand-run only)."""
    _flow = _flow_darcy if flow_map == "darcy" else _flow_of_p
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); ts = d.angeloni_total_solids()
    params = ps._solute_params()
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    tsmap = {(r["variety"], r["T_degC"], r["p_bar"]): r["TS_g_100mL"] for r in ts}
    SPEC = {"caffeine": ("CF", 1.0), "trigonelline": ("TR", 1.0),
            "5CQA": ("5CQA", 1.0), "tds": ("TS", 0.1)}
    out = {}
    for variety in ("Arabica", "Robusta"):
        shots = sorted((r for r in bio if r["variety"] == variety
                        and r["granulometry"] == "O" and r["on_grid"] == "True"),
                       key=lambda x: (x["T_degC"], x["p_bar"]))
        per = {}
        for sol, (col, conv) in SPEC.items():
            blind, matched, preds, meas = [], [], [], []
            for r in shots:
                T = r["T_degC"]; flow = _flow(r["p_bar"], T)
                m = tsmap[(variety, T, r["p_bar"])] if sol == "tds" else r[col]
                pb = float(ps.simulate_fractions(T, flow, [0.0, t_shot_s],
                                                 params[sol], cl1=1.0)[0]) * conv
                blind.append(abs(pb - m) / m * 100); preds.append(pb); meas.append(m)
                if (variety, col) in inv:                # inventory-matched (CF/TR)
                    sp2 = dict(params[sol]); sp2["c_s0"] = inv[(variety, col)]
                    pm = float(ps.simulate_fractions(T, flow, [0.0, t_shot_s],
                                                     sp2, cl1=1.0)[0]) * conv
                    matched.append(abs(pm - m) / m * 100)
            cc = float(np.corrcoef(preds, meas)[0, 1]) if np.std(meas) > 0 else float("nan")
            per[sol] = dict(mape_blind=round(float(np.mean(blind)), 1),
                            mape_inv_matched=(round(float(np.mean(matched)), 1)
                                              if matched else None),
                            shape_corr=round(cc, 2), n=len(shots))
        out[variety] = per
    allmape = np.mean([out[v][s]["mape_blind"] for v in out for s in SPEC])
    return dict(per_variety=out, n_conditions_per_variety=9, flow_map=flow_map,
                overall_mape_blind=round(float(allmape), 1),
                strength=("independent, per-condition (granulometry O on-grid; "
                          "p->flow " + ("Darcy q~p/mu(T)" if flow_map == "darcy"
                                        else "crude linear tau") + ")"),
                note="per-condition MAPE >> pooled-envelope bracket and angeloni's "
                     "own ~9-13% model. Inventory-matching helps caffeine, HURTS "
                     "trigonelline -> not pure inventory; per-species extraction "
                     "fraction + (T,p) shape do NOT transfer cleanly across "
                     "machine/coffee -- an irreducible-without-refit residual.")


def flow_map_refinement():
    """Report how much the refined Darcy(p,T) flow map closes the transfer gap vs
    the crude linear-tau baseline. PARTIAL by design: it fixes the residence-time
    component (the crude map over-attributed flow to high pressure); the residual
    is cross-coffee inventory + kinetic mismatch, which no flow map can close."""
    crude = gate_pannusch_angeloni_per_condition(flow_map="tau")["overall_mape_blind"]
    darcy = gate_pannusch_angeloni_per_condition(flow_map="darcy")["overall_mape_blind"]
    return dict(overall_mape_crude_tau=crude, overall_mape_refined_darcy=darcy,
                closed_pp=round(crude - darcy, 1),
                residual_source="cross-coffee inventory + per-species kinetic mismatch",
                note=f"refined Darcy(p,T) flow map cuts overall blind MAPE "
                     f"{crude}% -> {darcy}% (closes {round(crude - darcy, 1)} pp of "
                     f"the residence-time gap); residual >> angeloni's ~9-13% is "
                     f"NOT flow -- it is inventory + kinetics, only closable by "
                     f"refitting to the angeloni coffee.")


def report():
    r = gate_angeloni_multispecies_bracket()
    print("== angeloni2023 multi-species bracket (TS/TDS; INDEPENDENT; report) ==")
    print(f"{'gran':>5} {'gs':>4} {'cam_TDS':>8} {'angeloni_TS':>14} {'result':>8}")
    for x in r["per_granulometry"]:
        print(f"{x['granulometry']:>5} {x['gs']:>4} {x['cameron_tds']:>8} "
              f"{x['angeloni_ts_lo']:>6}-{x['angeloni_ts_hi']:<6} "
              f"{x['direction']:>8}")
    print(f"\nbracketed {r['n_bracketed']}/{r['n_conditions']}; grind ordering "
          f"matches: {r['grind_ordering_matches']}; Cameron reads low: "
          f"{r['cameron_reads_low_systematically']}.")
    print(r["note"])
    print("\n== pannusch2024 per-species bracket (multi-solute) ==")
    pr = gate_pannusch_angeloni_species_bracket()
    print(f"{'solute':>13} {'->species':>10} {'pred':>7} {'angeloni_range':>16} {'result':>7}")
    for x in pr["per_species"]:
        print(f"{x['pannusch_solute']:>13} {x['angeloni_species']:>10} "
              f"{x['predicted']:>7} {x['range_lo']:>6}-{x['range_hi']:<6} "
              f"{x['direction']:>7}")
    print(f"bracketed {pr['n_bracketed']}/{pr['n_species']}. {pr['note']}")
    print("\n== pannusch2024 PER-CONDITION vs angeloni (granulometry O on-grid) ==")
    pc = gate_pannusch_angeloni_per_condition()
    print(f"{'variety':>8} {'solute':>13} {'MAPE_blind':>10} {'MAPE_invmatch':>13} {'shape_r':>8}")
    for v, per in pc["per_variety"].items():
        for sol, x in per.items():
            im = "-" if x["mape_inv_matched"] is None else f"{x['mape_inv_matched']}%"
            print(f"{v:>8} {sol:>13} {x['mape_blind']:>9}% {im:>13} {x['shape_corr']:>8}")
    print(f"overall blind MAPE {pc['overall_mape_blind']}% "
          f"(flow map: {pc['flow_map']}). {pc['note']}")
    fr = flow_map_refinement()
    print(f"\nflow-map refinement: crude-tau {fr['overall_mape_crude_tau']}% -> "
          f"Darcy(p,T) {fr['overall_mape_refined_darcy']}% "
          f"(closed {fr['closed_pp']} pp). {fr['note']}")
    return dict(cameron=r, pannusch_bracket=pr, pannusch_per_condition=pc,
                flow_refinement=fr)


if __name__ == "__main__":
    report()
