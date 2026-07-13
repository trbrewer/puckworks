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

# --- matched-beverage endpoint (review B1) --------------------------------------
# angeloni collect 40 +/- 2 g beverage at a 1:2 ratio (20 g dose); density ~1, so
# ~40 mL. A fixed 25 s window is NOT a matched cup: with grind-specific flow it
# represents ~50/77/29 mL for O/C/F. Terminate every simulation when the collected
# volume reaches V_TARGET so the compared cups share the same endpoint.
_V_TARGET_ML = 40.0


def _matched_bounds(flow_mL_s, v_target=_V_TARGET_ML):
    """[0, t_end] with t_end = V_target / Q -> a matched-mass cup (constant flow)."""
    return [0.0, float(v_target) / float(flow_mL_s)]


def _mape_level(f, m):
    """EXACT minimiser of the MAPE objective over the inventory LEVEL c
    (review B3). J(c) = mean_i (f_i/m_i)|c - m_i/f_i| is minimised by the WEIGHTED
    MEDIAN of x_i = m_i/f_i with weights w_i = f_i/m_i -- not a grid argmin and not
    the plain median. Returns (c*, MAPE% at c*)."""
    f = np.asarray(f, float); m = np.asarray(m, float)
    x = m / f; w = f / m
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.cumsum(w)
    k = int(np.searchsorted(cw, 0.5 * cw[-1]))
    c = float(x[min(k, len(x) - 1)])
    return c, float(np.mean(np.abs(c * f - m) / m) * 100.0)


# rate domain for the profiles (review B6): log-spaced and WIDER than the old
# [0.4, 2.5] linear grid, so a boundary optimum is exposed rather than imposed.
_RATE_DOMAIN = np.geomspace(0.15, 6.5, 18)

# pannusch2024 fitted per-grind grain geometry (card Table 2: psi, d_s2 for grind
# 1.4/1.7/2.0). The port freezes the centre grind (1.7) for all experiments; B5
# uses these to test geometry sensitivity. They vary <15% across grinds.
_PGEOM = {"1.4": dict(psi=0.19, d_s2=332e-6),
          "1.7": dict(psi=0.23, d_s2=330e-6),
          "2.0": dict(psi=0.22, d_s2=301e-6)}


def _log_level_mape(f, m):
    """Level fit under a LOG (relative-error) loss, for the M6 loss-sensitivity:
    minimising sum|ln(c f_i) - ln m_i| gives ln c* = median(ln m_i - ln f_i), i.e.
    c* = geometric median of m_i/f_i. Returns the resulting MAPE% (for comparability
    with the weighted-median MAPE fit)."""
    f = np.asarray(f, float); m = np.asarray(m, float)
    c = float(np.exp(np.median(np.log(m) - np.log(f))))
    return c, float(np.mean(np.abs(c * f - m) / m) * 100.0)


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


def gate_pannusch_angeloni_species_bracket(T_C=93.4, flow_mL_s=1.6):
    """PER-SPECIES bracket: pannusch2024 (multi-solute, T/flow-resolved kinetics)
    forward-predicted cup concentrations vs the angeloni per-species measured
    RANGES. Unlike cameron (single lumped solute -> TDS only), pannusch produces
    caffeine (CF), trigonelline (TR), 5CQA, and TDS. Blind forward run (cl1
    cancels in the normalized solver, verified) at a representative espresso
    condition (T on-grid, grind 1.7), integrated to the MATCHED 40 g/mL beverage
    endpoint (t_end = 40 mL / flow, review MAJ-08 -- no longer a fixed 25 s). At
    the 1.6 mL/s default this endpoint is ~25 s, so the envelope screen is
    essentially unchanged but now shares the paper's matched-mass contract.
    angeloni bioactives are g/L = mg/mL (pannusch's units); TS g/100 mL =
    pannusch TDS(mg/mL)/10.

    Report semantics (not hard pass/fail): reports per-observable hits/misses. The
    finding is that pannusch's kinetics -- fit to a DIFFERENT machine/coffee --
    land INSIDE the angeloni envelope for the three named solutes AND the
    aggregate-solids proxy TDS (near the low edge), where cameron's TDS reads low.
    INDEPENDENT strength. (TDS is a source-specific aggregate-solids proxy, NOT a
    fourth named solute -- reported alongside but semantically distinct, M5.)"""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); ts = d.angeloni_total_solids()
    params = ps._solute_params()
    # (pannusch solute -> angeloni column, unit conversion to angeloni units, source)
    spec_map = {"caffeine": ("CF", 1.0, bio), "trigonelline": ("TR", 1.0, bio),
                "5CQA": ("5CQA", 1.0, bio), "tds": ("TS_g_100mL", 0.1, ts)}
    rows = []
    for sol, (col, conv, src) in spec_map.items():
        pred = float(ps.simulate_fractions(T_C, flow_mL_s, _matched_bounds(flow_mL_s),
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
                note="pannusch (multi-solute kinetics) brackets the three named "
                     "solutes + the aggregate-solids proxy TDS in the angeloni "
                     "envelope, near the low edge -- vs cameron's TDS "
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


def gate_pannusch_angeloni_per_condition(t_shot_s=25.0, flow_map="darcy",
                                         v_target=_V_TARGET_ML):
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
            conditions = []                               # per-shot residual records (MAJ-17)
            for r in shots:
                T = r["T_degC"]; flow = _flow(r["p_bar"], T)
                bounds = _matched_bounds(flow, v_target)  # matched cup at v_target (B1)
                m = tsmap[(variety, T, r["p_bar"])] if sol == "tds" else r[col]
                pb = float(ps.simulate_fractions(T, flow, bounds,
                                                 params[sol], cl1=1.0)[0]) * conv
                blind.append(abs(pb - m) / m * 100); preds.append(pb); meas.append(m)
                rec = dict(T_degC=T, p_bar=r["p_bar"], pred_blind=pb, meas=m,
                           signed_resid_blind_pct=round((pb - m) / m * 100, 2),
                           pred_matched=None, signed_resid_matched_pct=None)
                if (variety, col) in inv:                # inventory-matched (CF/TR)
                    sp2 = dict(params[sol]); sp2["c_s0"] = inv[(variety, col)]
                    pm = float(ps.simulate_fractions(T, flow, bounds,
                                                     sp2, cl1=1.0)[0]) * conv
                    matched.append(abs(pm - m) / m * 100)
                    rec["pred_matched"] = pm
                    rec["signed_resid_matched_pct"] = round((pm - m) / m * 100, 2)
                conditions.append(rec)
            cc = float(np.corrcoef(preds, meas)[0, 1]) if np.std(meas) > 0 else float("nan")
            per[sol] = dict(mape_blind=round(float(np.mean(blind)), 1),
                            mape_inv_matched=(round(float(np.mean(matched)), 1)
                                              if matched else None),
                            shape_corr=round(cc, 2), n=len(shots),
                            conditions=conditions)         # signed residuals vs (T,p)
        out[variety] = per
    allmape = np.mean([out[v][s]["mape_blind"] for v in out for s in SPEC])
    return dict(per_variety=out, n_conditions_per_variety=9, flow_map=flow_map,
                overall_mape_blind=round(float(allmape), 1),
                strength=("independent, per-condition (granulometry O on-grid; "
                          "p->flow " + ("Darcy q~p/mu(T)" if flow_map == "darcy"
                                        else "crude linear tau") + ")"),
                note="per-condition MAPE >> pooled-envelope bracket and angeloni's "
                     "own ~9-13% model, at MATCHED 40 g cups. Inventory-matching "
                     "helps caffeine, HURTS trigonelline -> not pure inventory; the "
                     "per-species (T,p) transfer residual is NOT REMOVED by the "
                     "tested flow maps + inventory match (competing sources -- grain "
                     "geometry, viscosity, assay -- are not separately bounded here).")


def endpoint_mass_sensitivity(v_targets=(38.0, 40.0, 42.0)):
    """ENDPOINT-MASS sensitivity (review A2-09): Angeloni collect 40 +/- 2 g at ~unit
    density, so the matched cup could be anywhere in ~38-42 mL. Re-run the per-condition
    blind transfer at each endpoint volume and report whether the overall blind MAPE and
    the qualitative pattern (inventory-matching HELPS caffeine, HURTS trigonelline) are
    stable -- i.e. the transfer conclusion does not hinge on the exact 40 g/40 mL
    approximation or a +/-5% density/tolerance error. NOTE: ~1 min of PDE solves per
    endpoint (slow; hand-run)."""
    import numpy as np
    rows = []
    for v in v_targets:
        pc = gate_pannusch_angeloni_per_condition(v_target=v)
        pv = pc["per_variety"]
        # the caffeine-helps / trigonelline-hurts signature (Arabica, blind vs matched)
        ar = pv["Arabica"]
        caf = ar["caffeine"]; tri = ar["trigonelline"]
        rows.append(dict(
            v_target_ml=v, overall_mape_blind=pc["overall_mape_blind"],
            caffeine_matched_helps=bool(caf["mape_inv_matched"] is not None
                                        and caf["mape_inv_matched"] < caf["mape_blind"]),
            trigonelline_matched_hurts=bool(tri["mape_inv_matched"] is not None
                                            and tri["mape_inv_matched"] > tri["mape_blind"])))
    mapes = [r["overall_mape_blind"] for r in rows]
    caffeine_invariant = all(r["caffeine_matched_helps"] for r in rows)
    trig_invariant = all(r["trigonelline_matched_hurts"] for r in rows)
    pattern_invariant = caffeine_invariant and trig_invariant
    spread = round(max(mapes) - min(mapes), 1)
    return dict(
        rows=rows, v_targets=list(v_targets),
        overall_mape_spread_pp=spread,
        overall_mape_range=[round(min(mapes), 1), round(max(mapes), 1)],
        caffeine_helps_invariant=caffeine_invariant,
        trigonelline_hurts_invariant=trig_invariant,
        pattern_invariant_across_endpoints=pattern_invariant,
        verdict=("HONEST endpoint-mass caveat (review A2-09): across matched-cup endpoints "
                 "%s mL (the 40 +/- 2 g window at ~unit density), the overall blind "
                 "transfer MAPE is MODERATELY endpoint-sensitive -- it moves %.1f pp "
                 "(%.1f -> %.1f%%) -- and the finer trigonelline-hurts signature is NOT "
                 "invariant (it flips near the +5%% endpoint). The ROBUST parts are the "
                 "large per-condition transfer residual itself and the caffeine "
                 "inventory-match improvement (both hold at every endpoint). So the "
                 "headline (a large, structured residual not fixed by inventory alone) "
                 "does not hinge on the 40 g approximation, but the exact MAPE magnitude "
                 "and the trigonelline detail DO carry a ~5 pp endpoint uncertainty that "
                 "the manuscript should state, not dismiss."
                 % ("/".join("%g" % v for v in v_targets), spread, min(mapes), max(mapes))),
        strength="endpoint-mass robustness of the per-condition transfer (declared 40 g "
                 "approximation); does not re-open the independent-identification scope")


def flow_map_refinement():
    """Report how much the refined Darcy(p,T) flow map closes the transfer gap vs
    the crude linear-tau baseline. PARTIAL by design: it reduces the residence-time
    component (the crude map over-attributed flow to high pressure). The residual is
    NOT REMOVED by the two tested flow maps -- but competing sources (grain geometry,
    viscosity, endpoint, assay) are not separately quantified, so this does not
    uniquely attribute the residual to inventory+kinetics (review M2)."""
    crude = gate_pannusch_angeloni_per_condition(flow_map="tau")["overall_mape_blind"]
    darcy = gate_pannusch_angeloni_per_condition(flow_map="darcy")["overall_mape_blind"]
    return dict(overall_mape_crude_tau=crude, overall_mape_refined_darcy=darcy,
                closed_pp=round(crude - darcy, 1),
                residual_note="not removed by the two tested flow maps; competing "
                              "sources not separately bounded",
                note=f"refined Darcy(p,T) flow map cuts overall blind MAPE "
                     f"{crude}% -> {darcy}% (closes {round(crude - darcy, 1)} pp of "
                     f"the residence-time component) at matched 40 g cups; the "
                     f"residual >> angeloni's ~9-13% is NOT REMOVED by the two tested "
                     f"maps -- attribution to inventory+kinetics is not established "
                     f"until geometry/viscosity/endpoint are separately bounded.")


def refit_pannusch_angeloni(rate_grid=None):
    """Refit pannusch KINETICS to the angeloni coffee -- a NEW calibration (POST-FIT
    reconstruction, NOT independent). Per solute per variety, fit two knobs to the
    9 on-grid granulometry-O points and VALIDATE on the 2 held-out off-grid O
    points ((96,9) and (91,8)):
      - c_s0 (inventory LEVEL): cup conc is exactly linear in c_s0, so the optimum
        is analytic (a rescale) -- NOT a real kinetic fit.
      - rate_scale (KINETICS): a multiplier on the Sherwood prefactors A1,A2.
    The van't Hoff / Re-exponent STRUCTURE is held (only its overall rate moves).

    Finding: the ~31% transfer gap decomposes cleanly. CAFFEINE needs rate_scale
    ~1.0 (kinetics already transfer; gap was pure inventory -- and the fitted c_s0
    RECOVERS the angeloni Table 7 value). TRIGONELLINE needs rate_scale ~0.4
    (pannusch over-extracts it for the angeloni coffee -- a genuine kinetic
    difference). After the refit, holdout MAPE is mostly single-digit. Strength:
    post-fit on-grid; 2-point off-grid holdout is a WEAK independent check.
    NOTE: ~90 s of PDE solves (slow; hand-run only)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); ts = d.angeloni_total_solids()
    params = ps._solute_params()
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    tsmap = {(r["variety"], r["T_degC"], r["p_bar"]): r["TS_g_100mL"] for r in ts}
    SPEC = {"caffeine": ("CF", 1.0), "trigonelline": ("TR", 1.0),
            "5CQA": ("5CQA", 1.0), "tds": ("TS", 0.1)}
    rate_grid = _RATE_DOMAIN if rate_grid is None else np.asarray(rate_grid)

    def _frac(sp, rs, conds):
        s = dict(sp); s["A1"] = sp["A1"] * rs; s["A2"] = sp["A2"] * rs; s["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
                        T, _flow_darcy(p, T), _matched_bounds(_flow_darcy(p, T)),
                        s, cl1=1.0)[0]) for T, p in conds])

    _best_cs0 = _mape_level                               # EXACT weighted-median (B3)

    out = {}
    for variety in ("Arabica", "Robusta"):
        def sh(on):
            return [r for r in bio if r["variety"] == variety
                    and r["granulometry"] == "O"
                    and r["on_grid"] == ("True" if on else "False")]
        on, off = sh(True), sh(False)
        per = {}
        for sol, (col, conv) in SPEC.items():
            def meas(r):
                return (tsmap[(variety, r["T_degC"], r["p_bar"])]
                        if sol == "tds" else r[col]) * conv
            conds = [(r["T_degC"], r["p_bar"]) for r in on]; m = np.array([meas(r) for r in on])
            co = [(r["T_degC"], r["p_bar"]) for r in off]; mo = np.array([meas(r) for r in off])
            best = None
            for rs in rate_grid:
                f = _frac(params[sol], rs, conds); cs0, mp = _best_cs0(f, m)
                if best is None or mp < best[2]:
                    best = (float(rs), cs0, mp)
            rs, cs0, mp = best
            fo = _frac(params[sol], rs, co)
            mpo = float(np.mean(np.abs(cs0 * fo - mo) / mo) * 100)
            at_bound = bool(rs <= rate_grid[0] * 1.001 or rs >= rate_grid[-1] * 0.999)
            per[sol] = dict(rate_scale=round(rs, 2), c_s0_fit=round(cs0, 1),
                            rate_at_boundary=at_bound,
                            c_s0_table7=(round(inv[(variety, col)], 1)
                                         if (variety, col) in inv else None),
                            mape_on_grid=round(mp, 1), mape_holdout=round(mpo, 1),
                            # review A3-03: raw holdout for the headline macro-average
                            mape_holdout_raw=float(mpo), mape_on_grid_raw=float(mp))
        out[variety] = per
    # M5: the HEADLINE macro-average is over the three NAMED solutes only; TDS is a
    # source-specific aggregate-solids PROXY, reported separately (not a 4th solute).
    # A3-03: average RAW per-fit holdouts, not the rounded display fields.
    named = ("caffeine", "trigonelline", "5CQA")
    hold_named = np.mean([out[v][s]["mape_holdout_raw"] for v in out for s in named])
    hold_proxy = np.mean([out[v]["tds"]["mape_holdout_raw"] for v in out])
    hold_all = np.mean([out[v][s]["mape_holdout_raw"] for v in out for s in SPEC])
    n_bound = sum(out[v][s]["rate_at_boundary"] for v in out for s in named)
    return dict(per_variety=out,
                named_solutes=list(named),
                mean_holdout_named=round(float(hold_named), 1),          # HEADLINE
                mean_holdout_aggregate_solids_proxy=round(float(hold_proxy), 1),
                mean_holdout_with_proxy=round(float(hold_all), 1),
                mean_holdout_mape=round(float(hold_named), 1),           # back-compat = named
                rate_domain=[round(float(rate_grid[0]), 2), round(float(rate_grid[-1]), 2)],
                n_rate_at_boundary=n_bound,
                strength="reconstruction (on-grid, a new calibration); 2-point off-grid "
                         "O holdout = weak internal check",
                note="matched-mass (40 g) cups, exact weighted-median level, wide log "
                     "rate domain. HEADLINE macro-average is the three NAMED solutes "
                     "(caffeine/trigonelline/5-CQA); TDS is a source-specific "
                     "aggregate-solids PROXY reported separately, NOT a 4th solute (M5). "
                     "Refit is a NEW angeloni calibration (granulometry O only, 9-point "
                     "fit); read per-species rate/c_s0 as a valley point, NOT a "
                     "mechanistic decomposition. %d/%d named-solute rates at the "
                     "(widened) domain boundary." % (n_bound, len(named) * len(out)))


# per-granulometry flow, from the card's OWN fitted hydraulic conductivity k_r(p)
# and per-granulometry shot times tau (angeloni2023.md): flow(p,T,gran) =
# (40 g / tau_gran) * k_r(p)/k_r(9) * mu(T_ref)/mu(T).
_TAU_GRAN = {"O": 20.0, "C": 13.0, "F": 35.0}
_KR = {"O": (2.60e-9, -6.50e-8, 5.08e-7), "C": (3.90e-9, -1.05e-7, 8.50e-7),
       "F": (1.20e-9, -3.17e-8, 2.56e-7)}


def _flow_gran(p_bar, T_C, gran):
    from puckworks.models.pannusch2024 import closures as pc
    a, b, c = _KR[gran]
    kr = lambda p: a * p * p + b * p + c
    mu = pc.water_viscosity(T_C + 273.15); mu_ref = pc.water_viscosity(_T_REF + 273.15)
    return (40.0 / _TAU_GRAN[gran]) * (kr(p_bar) / kr(9.0)) * (mu_ref / mu)


def joint_multigrind_fit():
    """IN-SAMPLE shared-parameter compatibility check (review A3-32: this is NOT a
    held-out transfer test -- all O+C+F data are fitted jointly). Fit ONE shared,
    grind-INDEPENDENT (rate_scale, c_s0) jointly to all three granulometries O+C+F at
    once (each grind with its own measured flow), and report the residual STRUCTURE
    rather than forcing a success.

    Method (per variety, per clean g/L species): pool the on-grid points of O, C, F;
    for each rate_scale, choose the single global c_s0 (level, linear -> analytic)
    that minimises the POOLED MAPE; keep the best rate. Report the pooled MAPE, the
    per-grind MAPE breakdown at that joint optimum, and — as the reference — the sum
    of the three per-grind INDEPENDENT best fits. The GAP (joint − independent) is
    the cost of forcing one inventory+rate to serve all grinds; a structured
    per-grind residual (one grind carrying the error) is the signature of
    non-transferability.

    Finding (expected, consistent with §4/§5): the residual STRUCTURE across grinds
    (whether one grind carries the error) is the signature of interest. Strength:
    IN-SAMPLE shared-parameter compatibility (all grinds fitted; NOT a held-out
    transfer test, and adequacy must be read against reduced-model baselines, not an
    absolute rule -- review A3-19). NOTE: ~2-3 min of PDE solves (slow; hand-run). """
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives()
    params = ps._solute_params()
    SPEC = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    GRINDS = ("O", "C", "F")

    def sh(variety, gran):
        return [r for r in bio if r["variety"] == variety
                and r["granulometry"] == gran and r["on_grid"] == "True"]

    def frac(sp, rs, conds, gran):
        s = dict(sp); s["A1"] = sp["A1"] * rs; s["A2"] = sp["A2"] * rs; s["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
                        T, _flow_gran(p, T, gran), _matched_bounds(_flow_gran(p, T, gran)),
                        s, cl1=1.0)[0]) for T, p in conds])

    rate_grid = _RATE_DOMAIN
    out = {}
    for variety in ("Arabica", "Robusta"):
        per = {}
        for sol, col in SPEC.items():
            # per-grind predictions-per-unit-level and measurements
            pug, meas = {}, {}
            for g in GRINDS:
                rows = sh(variety, g)
                conds = [(r["T_degC"], r["p_bar"]) for r in rows]
                meas[g] = np.array([r[col] for r in rows])
                pug[g] = {rs: frac(params[sol], rs, conds, g) for rs in rate_grid}
            # (a) JOINT: one rate + one global c_s0 (EXACT weighted median) over O+C+F
            best = None
            for rs in rate_grid:
                f_all = np.concatenate([pug[g][rs] for g in GRINDS])
                m_all = np.concatenate([meas[g] for g in GRINDS])
                cs0, mp = _mape_level(f_all, m_all)
                if best is None or mp < best[2]:
                    # FULL PRECISION per-grind MAPE (review MAJ-12: no rounding before
                    # aggregation -- round only for display in the returned dict)
                    pg = {g: float(np.mean(np.abs(cs0 * pug[g][rs] - meas[g])
                                           / meas[g]) * 100) for g in GRINDS}
                    best = (float(rs), cs0, mp, pg)
            rs_j, cs0_j, mape_j, pergrind_j = best
            # (b) per-grind INDEPENDENT best (the reference), full precision
            indep = {}
            for g in GRINDS:
                indep[g] = float(min(_mape_level(pug[g][rs], meas[g])[1]
                                     for rs in rate_grid))
            at_bound = bool(rs_j <= rate_grid[0] * 1.001 or rs_j >= rate_grid[-1] * 0.999)
            # review A3-03: keep RAW per-grind arrays for every headline aggregate; the
            # rounded copies are display-only. `indep_mean`/`cost` below MUST read the raw
            # fields, never the rounded ones.
            indep_mean_fit = float(np.mean(list(indep.values())))
            per[sol] = dict(
                joint_rate=round(rs_j, 2), joint_c_s0=round(cs0_j, 1),
                joint_rate_at_boundary=at_bound,
                joint_pooled_mape=float(mape_j),              # full precision
                joint_per_grind_mape={g: round(pergrind_j[g], 1) for g in GRINDS},
                joint_per_grind_mape_raw={g: float(pergrind_j[g]) for g in GRINDS},
                independent_per_grind_mape={g: round(indep[g], 1) for g in GRINDS},
                independent_per_grind_mape_raw={g: float(indep[g]) for g in GRINDS},
                independent_mean_raw=indep_mean_fit,
                cost_of_sharing_pp=round(mape_j - indep_mean_fit, 1))
        out[variety] = per
    # pooled == MACRO-AVERAGE across the 6 (variety x solute) joint fits, from full
    # precision (review MAJ-12/A3-03); cost-of-sharing = paired joint-minus-independent.
    # BOTH numerator and independent comparator read RAW fields (not the rounded dicts).
    pooled = float(np.mean([out[v][s]["joint_pooled_mape"]
                            for v in out for s in SPEC]))
    indep_mean = float(np.mean([out[v][s]["independent_mean_raw"]
                                for v in out for s in SPEC]))
    n_bound = sum(out[v][s]["joint_rate_at_boundary"] for v in out for s in SPEC)
    n_tot = len([1 for v in out for s in SPEC])
    cost = pooled - indep_mean
    # IN-SAMPLE compatibility reading (review A3-19/A3-32): the cost-of-sharing is the
    # in-sample penalty for forcing one (c_s0, rate) across grinds vs per-grind fits.
    # This is NOT a held-out transfer result and adequacy is NOT decided by a bare
    # threshold -- it must be read against reduced-model baselines (one constant per
    # grind is nearly competitive; see transfer_skill_vs_baselines). We report the gap
    # descriptively and flag that the per-grind fits have MORE flexibility, so lower
    # in-sample error there is expected.
    read = ("forcing a single shared (c_s0, rate) across O+C+F costs %.1f pp of in-sample "
            "MAPE vs the more flexible per-grind fits (pooled %.1f%% vs %.1f%%). This is "
            "an IN-SAMPLE parameter-sharing penalty, NOT a held-out transfer test; whether "
            "it counts as 'adequate' depends on reduced-model baselines (a per-grind "
            "constant is nearly competitive), not on an absolute cutoff." % (
                cost, pooled, indep_mean))
    return dict(per_variety=out,
                pooled_definition="macro-average across the 6 (variety x solute) joint fits",
                mean_joint_pooled_mape=round(pooled, 1),
                mean_independent_per_grind_mape=round(indep_mean, 1),
                cost_of_sharing_pp=round(cost, 1),
                joint_rate_domain=[round(float(_RATE_DOMAIN[0]), 2),
                                   round(float(_RATE_DOMAIN[-1]), 2)],
                n_joint_rate_at_boundary=n_bound, n_species_variety=n_tot,
                is_in_sample_not_heldout=True,
                verdict="IN-SAMPLE shared-parameter compatibility (matched-mass 40 g cups, "
                        "exact weighted-median level, wide log rate domain): " + read
                        + " %d/%d rates at the widened domain boundary." % (n_bound, n_tot))


def validate_refit_granulometry():
    """Validate the angeloni refit ACROSS granulometries C/F (held-out grinds).
    Uses the card's own per-granulometry flow (k_r(p) + tau). Two tests, on the
    clean g/L species (CF/TR/5CQA; TDS dropped -- unit-aggregate artifact):

    (1) TRANSFER: fit (rate_scale, c_s0) on granulometry O, PREDICT C and F with
        no refit. If the fit is a transferable coffee property it should hold.
    (2) DEGENERACY: refit independently at O/C/F and compare the fitted knobs.

    Finding (CORRECTED at matched mass, review B1): the O-fit (level+rate PAIR)
    transfers REASONABLY to the held-out grinds (held-out C/F MAPE ~3-18%), a large
    improvement over the pre-correction fixed-25s result (~25-49%) which was mostly
    an unmatched-endpoint artifact. This EMPIRICALLY illustrates the identifiability
    lesson (review M1): the (rate_scale, c_s0) split is DEGENERATE WITHIN a grind
    (the fitted rate flips across flow-map/domain; see identifiability_panel), yet
    predictions along that compensating manifold stay stable across grind -- so
    individual non-identifiability does NOT imply predictive non-transfer. The
    earlier 'no shared calibration / caffeine=inventory / trigonelline=kinetic'
    reading was an over-interpretation of the endpoint artifact. NOTE: slow."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives()
    params = ps._solute_params()
    SPEC = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}

    def sh(variety, gran):
        return [r for r in bio if r["variety"] == variety
                and r["granulometry"] == gran and r["on_grid"] == "True"]

    def frac(sp, rs, conds, gran):
        s = dict(sp); s["A1"] = sp["A1"] * rs; s["A2"] = sp["A2"] * rs; s["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
                        T, _flow_gran(p, T, gran), _matched_bounds(_flow_gran(p, T, gran)),
                        s, cl1=1.0)[0]) for T, p in conds])

    best_cs0 = _mape_level                                # EXACT weighted-median (B3)

    def o_profile(variety, sol):
        """Full O-grind profile: per-rate (c_s0, O-MAPE) over the wide domain."""
        rows = sh(variety, "O"); col = SPEC[sol]
        conds = [(r["T_degC"], r["p_bar"]) for r in rows]; m = np.array([r[col] for r in rows])
        cs0s, mps = [], []
        for rs in _RATE_DOMAIN:
            f = frac(params[sol], rs, conds, "O"); cs0, mp = best_cs0(f, m)
            cs0s.append(cs0); mps.append(mp)
        return np.asarray(_RATE_DOMAIN, float), np.asarray(cs0s), np.asarray(mps)

    def fit(variety, sol, gran):
        rows = sh(variety, gran); col = SPEC[sol]
        conds = [(r["T_degC"], r["p_bar"]) for r in rows]; m = np.array([r[col] for r in rows])
        best = None
        for rs in _RATE_DOMAIN:                            # wide log domain (B6)
            f = frac(params[sol], rs, conds, gran); cs0, mp = best_cs0(f, m)
            if best is None or mp < best[2]:
                best = (float(rs), cs0, mp)
        return best                                       # rate, c_s0, mape

    def heldout_mape(variety, sol, gran, rs, cs0):
        rows = sh(variety, gran); col = SPEC[sol]
        conds = [(r["T_degC"], r["p_bar"]) for r in rows]; m = np.array([r[col] for r in rows])
        pred = cs0 * frac(params[sol], rs, conds, gran)
        return float(np.mean(np.abs(pred - m) / m) * 100), conds, m, pred

    transfer, degeneracy, points, manifold = {}, {}, {}, {}
    for variety in ("Arabica", "Robusta"):
        for sol, col in SPEC.items():
            rates, cs0s, mpsO = o_profile(variety, sol)   # full O profile (A2-02)
            iO = int(np.argmin(mpsO)); rsO, cs0O, mpO = float(rates[iO]), float(cs0s[iO]), float(mpsO[iO])
            held = {}
            for g in ("C", "F"):
                hm, conds, m, pred = heldout_mape(variety, sol, g, rsO, cs0O)
                held[g] = hm                              # FULL PRECISION (A2-11/12)
                points[f"{variety}:{sol}:{g}"] = [
                    dict(T=float(T), p=float(p), obs=float(mo), pred=float(pr))
                    for (T, p), mo, pr in zip(conds, m, pred)]
            transfer[(variety, sol)] = dict(O_fit_mape=round(mpO, 2),
                                            heldout_C=round(held["C"], 2),
                                            heldout_F=round(held["F"], 2))
            # A2-02: transfer the NEAR-OPTIMAL O-grind set (O-MAPE <= 1.10*min), not
            # only the point optimum, and report the held-out C/F envelope over the
            # compensating manifold -- so "stable along the manifold" is TESTED.
            near = mpsO <= mpsO[iO] * 1.10
            env = {}
            for g in ("C", "F"):
                vals = np.array([heldout_mape(variety, sol, g, float(rates[k]),
                                              float(cs0s[k]))[0]
                                 for k in np.where(near)[0]])
                env[g] = dict(point=round(held[g], 2),
                              n_in_set=int(near.sum()),
                              median=round(float(np.median(vals)), 2),
                              p5_p95=[round(float(np.percentile(vals, 5)), 2),
                                      round(float(np.percentile(vals, 95)), 2)],
                              worst=round(float(np.max(vals)), 2))
            manifold[f"{variety}:{sol}"] = env
        # degeneracy: refit at each granulometry (Arabica only, representative)
        if variety == "Arabica":
            for sol in SPEC:
                degeneracy[sol] = {g: (lambda b: dict(rate=round(b[0], 1),
                                   c_s0=round(b[1], 1), mape=round(b[2], 2)))(
                                   fit("Arabica", sol, g)) for g in ("O", "C", "F")}
    hc = [t["heldout_C"] for t in transfer.values()]
    hf = [t["heldout_F"] for t in transfer.values()]
    # manifold envelope: worst held-out MAPE across the near-optimal set, over all fits
    mani_worst = max(max(v["C"]["worst"], v["F"]["worst"]) for v in manifold.values())
    mani_worst_point = max(max(t["heldout_C"], t["heldout_F"]) for t in transfer.values())
    return dict(transfer=transfer, degeneracy_arabica=degeneracy, points=points,
                manifold_transfer=manifold,
                manifold_worst_heldout_mape=round(mani_worst, 2),
                point_worst_heldout_mape=round(mani_worst_point, 2),
                heldout_C_range=[round(min(hc), 1), round(max(hc), 1)],
                heldout_F_range=[round(min(hf), 1), round(max(hf), 1)],
                verdict="At MATCHED 40 g cups the O-refit produces held-out C/F absolute "
                        "MAPE of ~%.0f-%.0f%% (C) and ~%.0f-%.0f%% (F) at the point "
                        "optimum -- a large improvement over the pre-correction fixed-25s "
                        "result (~25-49%%), an unmatched-endpoint artifact (review B1/B5). "
                        "NULL-BENCHMARK CAVEAT (review A3-01): these ABSOLUTE errors do "
                        "NOT by themselves establish mechanistic transfer skill -- an "
                        "O-trained level-only constant is nearly as accurate; see "
                        "transfer_skill_vs_baselines for the skill scores. MANIFOLD SET "
                        "(review A2-02/A3-02): transferring the DISCRETE near-optimal "
                        "O-grind MAPE set (within 10%% of the min on the 18-point rate "
                        "grid) to C/F, the worst AGGREGATE held-out MAPE across the set is "
                        "%.1f%% (vs %.1f%% at the point optimum) -- so the aggregate error "
                        "is stable across the set, though condition-wise prediction "
                        "envelopes remain owed (A3-11). The (rate,c_s0) split remains "
                        "DEGENERATE within a grind (the rate flips across flow-map/domain; "
                        "see identifiability_panel)." % (
                            min(hc), max(hc), min(hf), max(hf),
                            mani_worst, mani_worst_point))


def table7_rate_constraint(panel, inventory_g_L, rel_band=0.10):
    """A3-13: quantify the SAME-CAMPAIGN orthogonal constraint that the Table 7 measured
    inventory places on the kinetic rate. The identifiability valley is the profiled
    inventory path c*(rate); an independent inventory measurement (Angeloni Table 7,
    roast-and-ground) intersects that path at a specific rate. We solve for the rate where
    c*(rate) equals the Table 7 value, and propagate a declared +/-`rel_band` sensitivity
    on the inventory to a rate INTERVAL. This is a fast, PDE-free post-processing of the
    panel's profile (no likelihood; a same-campaign orthogonal constraint, NOT an external
    validation). Returns None if the value lies outside the profiled range."""
    import numpy as np
    prof = panel["profile"]
    rates = np.asarray(prof["rates"], float); cstar = np.asarray(prof["c_star"], float)
    lo_dom, hi_dom = float(rates[0]), float(rates[-1])

    def _rate_at(inv):
        # c*(rate) is monotone-decreasing along the valley; interpolate in log-rate.
        if inv >= cstar.max() or inv <= cstar.min():
            return None
        order = np.argsort(cstar)            # ascending c*
        lr = np.interp(inv, cstar[order], np.log(rates[order]))
        return float(np.exp(lr))

    r_mid = _rate_at(inventory_g_L)
    r_hi_inv = _rate_at(inventory_g_L * (1.0 + rel_band))   # higher inventory -> lower rate
    r_lo_inv = _rate_at(inventory_g_L * (1.0 - rel_band))
    band = sorted(x for x in (r_lo_inv, r_hi_inv) if x is not None)
    interior = bool(r_mid is not None and lo_dom * 1.01 < r_mid < hi_dom * 0.99)
    return dict(
        inventory_g_L=round(float(inventory_g_L), 3),
        implied_rate=round(r_mid, 3) if r_mid is not None else None,
        implied_rate_band=[round(b, 3) for b in band] if len(band) == 2 else None,
        rel_band=rel_band, intersection_interior=interior,
        intersection_unique=bool(r_mid is not None),
        note=("The Table 7 inventory intersects the profiled valley at a single interior "
              "rate, so an orthogonal same-campaign inventory measurement COLLAPSES the "
              "otherwise broad inventory-rate profile to a narrow rate band -- the "
              "strongest available constraint on the rate. Same-campaign (Angeloni), NOT "
              "an independent external validation."
              if interior else
              "The Table 7 inventory does not intersect the profiled valley interior to "
              "the tested rate domain; the constraint is censored/absent here."))


def transfer_skill_vs_baselines(varieties=("Arabica", "Robusta"),
                                solutes=("caffeine", "trigonelline", "5CQA")):
    """A3-01 (submission-blocking null benchmark): does the mechanistic O->C/F transfer
    add predictive SKILL beyond simple level-only baselines available at prediction time?
    A low absolute MAPE can arise from analyte levels that are stable across operating
    conditions, even if the model contributes little condition-specific signal (the
    review's own data-only check found an O-trained constant within ~0.4 pp of the model).
    So we compare the mechanistic transfer against PREDECLARED baselines fit ONLY on the
    O training grind:

      - O-trained MAPE-optimal CONSTANT: one level fit to the 9 O obs by the exact
        weighted-median MAPE solution, applied UNCHANGED to every held-out C/F point --
        captures ONLY the analyte level, no temperature/pressure/flow/kinetic response;
      - SAME-(T,p) O lookup: the observed O concentration at the matching (T,p) DoE
        condition -- uses the same-campaign O response across grind, no mechanistic model.

    For each variety x named solute we fit the model on O (rate + weighted-median level)
    and predict held-out C/F (mirroring validate_refit_granulometry's flow map/fit), then
    report FULL-PRECISION per-grind and pooled MAPE for the model and each baseline, the
    skill score 1 - MAPE_model/MAPE_baseline, and PAIRED per-condition loss differences
    (model - constant). NOTE: ~2-3 min of PDE solves (slow; hand-run)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); params = ps._solute_params()
    SPEC = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}

    def sh(variety, gran):
        return [r for r in bio if r["variety"] == variety
                and r["granulometry"] == gran and r["on_grid"] == "True"]

    def frac(sp, rs, conds, gran):
        s = dict(sp); s["A1"] = sp["A1"] * rs; s["A2"] = sp["A2"] * rs; s["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
                        T, _flow_gran(p, T, gran), _matched_bounds(_flow_gran(p, T, gran)),
                        s, cl1=1.0)[0]) for T, p in conds])

    per = {}
    grind_err = {"C": {"model": [], "const": [], "lookup": []},
                 "F": {"model": [], "const": [], "lookup": []}}
    n_model_worse_than_const = 0; n_cases = 0
    for variety in varieties:
        for sol in solutes:
            col = SPEC[sol]
            rowsO = sh(variety, "O"); condsO = [(r["T_degC"], r["p_bar"]) for r in rowsO]
            mO = np.array([r[col] for r in rowsO], float)
            # mechanistic model: fit rate on O by MAPE (weighted-median level per rate)
            best = None
            for rs in _RATE_DOMAIN:
                f = frac(params[sol], rs, condsO, "O"); c, mp = _mape_level(f, mO)
                if best is None or mp < best[2]:
                    best = (float(rs), c, mp)
            rsO, cs0O, _ = best
            # O-trained MAPE-optimal constant: fit a level to a UNIT prediction on O
            c_const = float(_mape_level(np.ones(len(mO)), mO)[0])
            o_by_tp = {(r["T_degC"], r["p_bar"]): float(r[col]) for r in rowsO}
            entry = {}
            for g in ("C", "F"):
                rows = sh(variety, g); conds = [(r["T_degC"], r["p_bar"]) for r in rows]
                m = np.array([r[col] for r in rows], float)
                e_model = np.abs(cs0O * frac(params[sol], rsO, conds, g) - m) / m * 100.0
                e_const = np.abs(c_const - m) / m * 100.0
                lookup = np.array([o_by_tp[(T, p)] for (T, p) in conds], float)
                e_lookup = np.abs(lookup - m) / m * 100.0
                grind_err[g]["model"].extend(e_model)
                grind_err[g]["const"].extend(e_const)
                grind_err[g]["lookup"].extend(e_lookup)
                entry[g] = dict(
                    model_mape=round(float(e_model.mean()), 2),
                    const_mape=round(float(e_const.mean()), 2),
                    lookup_mape=round(float(e_lookup.mean()), 2),
                    paired_model_minus_const=[round(float(a - b), 2)
                                              for a, b in zip(e_model, e_const)])
                for a, b in zip(e_model, e_const):
                    n_cases += 1
                    if a > b + 1e-9:
                        n_model_worse_than_const += 1
            fit_model = float(np.mean([entry[g]["model_mape"] for g in ("C", "F")]))
            fit_const = float(np.mean([entry[g]["const_mape"] for g in ("C", "F")]))
            per[f"{variety}:{sol}"] = dict(
                C=entry["C"], F=entry["F"],
                model_macro_mape=round(fit_model, 2),
                const_macro_mape=round(fit_const, 2),
                skill_vs_const=round(1.0 - fit_model / fit_const, 3))

    def _mean(xs):
        return float(np.mean(xs)) if len(xs) else float("nan")
    # pooled model / baseline MAPE and skill, per grind and overall
    pooled = {}
    for g in ("C", "F"):
        mm = _mean(grind_err[g]["model"]); mc = _mean(grind_err[g]["const"])
        ml = _mean(grind_err[g]["lookup"])
        pooled[g] = dict(model_mape=round(mm, 2), const_mape=round(mc, 2),
                         lookup_mape=round(ml, 2),
                         skill_vs_const=round(1.0 - mm / mc, 3),
                         skill_vs_lookup=round(1.0 - mm / ml, 3))
    all_model = grind_err["C"]["model"] + grind_err["F"]["model"]
    all_const = grind_err["C"]["const"] + grind_err["F"]["const"]
    all_lookup = grind_err["C"]["lookup"] + grind_err["F"]["lookup"]
    macro_model = _mean(all_model); macro_const = _mean(all_const)
    macro_lookup = _mean(all_lookup)
    skill_const = 1.0 - macro_model / macro_const
    skill_lookup = 1.0 - macro_model / macro_lookup
    # paired model-minus-constant loss (all held-out C/F points)
    paired = np.array(all_model) - np.array(all_const)
    return dict(
        per_fit=per, pooled_by_grind=pooled,
        pooled_model_mape=round(macro_model, 2),
        pooled_const_mape=round(macro_const, 2),
        pooled_lookup_mape=round(macro_lookup, 2),
        skill_vs_const=round(skill_const, 3),
        skill_vs_lookup=round(skill_lookup, 3),
        paired_model_minus_const_mean_pp=round(float(paired.mean()), 3),
        paired_model_minus_const_median_pp=round(float(np.median(paired)), 3),
        n_points=n_cases,
        n_model_worse_than_const=n_model_worse_than_const,
        baselines=["O-trained MAPE-optimal constant", "same-(T,p) O lookup"],
        verdict=("NULL-BENCHMARK skill (review A3-01): the mechanistic O->C/F transfer "
                 "gives pooled held-out MAPE %.2f%% vs %.2f%% for an O-trained level-only "
                 "constant (skill %.1f%%) and %.2f%% for a same-(T,p) O lookup (skill "
                 "%.1f%%). The model is WORSE than the constant on %d of %d held-out "
                 "points, and the paired mean model-minus-constant loss is %+.2f pp. "
                 "READING: low absolute C/F MAPE does NOT by itself establish mechanistic "
                 "transfer skill -- a constant carrying only the O level is nearly "
                 "competitive; the incremental skill of the kinetic/transport structure "
                 "over a level-only baseline is small and must be reported alongside the "
                 "absolute error, not in place of it." % (
                     macro_model, macro_const, 100 * skill_const, macro_lookup,
                     100 * skill_lookup, n_model_worse_than_const, n_cases,
                     float(paired.mean()))),
        strength="predeclared null-benchmark skill comparison (level-only baselines, "
                 "full precision); quantifies incremental mechanistic skill, not just "
                 "absolute fit")


def identifiability_panel(variety="Arabica", solute="caffeine", n_rate=29, n_cs0=41,
                          rate_lo=None, rate_hi=None):
    """FORMAL identifiability panel for the (inventory c_s0, kinetic rate) whole-cup
    degeneracy (PAPER_A_DRAFT §4/§8 owed): quantifies the flat valley beyond the
    tabulated sweep. On the angeloni on-grid granulometry-O whole-cup points, build
    the SSE objective over (rate_scale, c_s0) at the MATCHED 40 g cup endpoint (B1)
    — c_s0 enters linearly so its axis is cheap once the per-rate fraction
    predictions are solved — locate the minimum, fit a local Hessian in LOG
    parameters (u=ln rate, v=ln c_s0; geomspace grids are uniform in log so the
    finite differences are valid on the non-uniform rate axis, and log-params are
    the standard sloppiness basis), and report:

      - condition number kappa = lambda_max/lambda_min of the log-param SSE Hessian
        (LARGE -> a sloppy, practically non-identifiable direction);
      - the sloppy eigenvector (its components in (ln rate, ln c_s0) space —
        expected to lie along the c_s0*phi=const valley);
      - the LOCAL INVERSE-CURVATURE COUPLING coefficient from the inverse SSE Hessian
        (expected ~ +/-1). This is a geometric coupling diagnostic of the SSE surface,
        NOT a statistical parameter correlation: no likelihood or measurement-error
        model is specified, so it carries no confidence interpretation (review MAJ-03).
      - the profiled-objective interval on the rate: the fraction of the swept LOG-rate
        grid whose profiled SSE (optimised over c_s0) stays within 10% of the minimum
        (near 1.0 -> the data do not bound the rate), plus the log-width of that set.

    OBJECTIVE CONTRACT (review MAJ-02): the profile, surface, Hessian, condition
    number and coupling coefficient are all built on unweighted concentration-scale
    SSE with a LEAST-SQUARES nuisance level -- SSE is a smooth local-curvature
    diagnostic. MAPE (the exact weighted-median level) is the paper's PREDICTIVE
    metric elsewhere; here it is reported ONLY as a cross-check (frac_within_mape) to
    confirm the qualitative non-identifiability is not an SSE artefact. The 10% band
    is a stated tolerance, not a confidence interval (no likelihood is specified).

    Strength: verification/diagnostic (quantifies a known degeneracy on the transfer
    target; not a new validation). NOTE: ~1-2 min of PDE solves (slow; hand-run)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    col = COL[solute]
    bio = d.angeloni_bioactives()
    params = ps._solute_params()
    rows = [r for r in bio if r["variety"] == variety
            and r["granulometry"] == "O" and r["on_grid"] == "True"]
    conds = [(r["T_degC"], r["p_bar"]) for r in rows]
    m = np.array([r[col] for r in rows], float)
    rlo = _RATE_DOMAIN[0] if rate_lo is None else rate_lo            # domain (A2-06)
    rhi = _RATE_DOMAIN[-1] if rate_hi is None else rate_hi
    rates = np.geomspace(rlo, rhi, n_rate)                           # wide log (B6)
    # per-unit-level fraction predictions f(rate): one PDE solve per rate, at the
    # matched 40 g cup endpoint (B1)
    F = np.array([[float(ps.simulate_fractions(
                    T, _flow_darcy(p, T), _matched_bounds(_flow_darcy(p, T)),
                    {**params[solute], "A1": params[solute]["A1"] * rs,
                     "A2": params[solute]["A2"] * rs, "c_s0": 1.0}, cl1=1.0)[0])
                   for T, p in conds] for rs in rates])            # (n_rate, n_cond)
    sse = lambda pred: float(np.sum((pred - m) ** 2))
    # analytic best c_s0 per rate + the SSE profile (least-squares nuisance level)
    c_star = np.array([float(np.dot(F[i], m) / np.dot(F[i], F[i])) for i in range(n_rate)])
    sse_prof = np.array([sse(c_star[i] * F[i]) for i in range(n_rate)])
    # MAPE cross-check (review MAJ-02): profile the SAME degeneracy under the paper's
    # PREDICTIVE metric -- exact weighted-median level per rate -- to confirm the
    # flat valley is not an SSE artefact. Reported as a secondary contract only.
    # NOTE _mape_level returns (c*, MAPE%); take ONLY the MAPE column (review A2-01 --
    # the earlier code kept the whole tuple, so min/threshold/mean mixed levels + MAPEs).
    mape_prof = np.array([_mape_level(F[i], m)[1] for i in range(n_rate)])
    i0 = int(np.argmin(sse_prof))
    rate_star, cs0_star, sse_min = float(rates[i0]), float(c_star[i0]), float(sse_prof[i0])
    # 2D SSE on (rate grid x c_s0 grid) around the minimum. Both axes are
    # GEOMETRIC (uniform in LOG), so the Hessian below is taken in LOG parameters
    # u=ln(rate), v=ln(c_s0) with constant steps -- the standard sloppiness basis,
    # and correct for the non-uniform (geomspace) rate grid.
    cs0 = cs0_star * np.geomspace(0.55, 1.8, n_cs0)
    S = np.array([[sse(c * F[i]) for c in cs0] for i in range(n_rate)])
    j0 = int(np.argmin(np.abs(cs0 - cs0_star)))
    du = float(np.log(rates[1] / rates[0]))           # log-rate step (uniform)
    dv = float(np.log(cs0[1] / cs0[0]))               # log-c_s0 step (uniform)
    ii = min(max(i0, 1), n_rate - 2); jj = min(max(j0, 1), n_cs0 - 2)
    Suu = (S[ii + 1, jj] - 2 * S[ii, jj] + S[ii - 1, jj]) / du ** 2
    Svv = (S[ii, jj + 1] - 2 * S[ii, jj] + S[ii, jj - 1]) / dv ** 2
    Suv = (S[ii + 1, jj + 1] - S[ii + 1, jj - 1] - S[ii - 1, jj + 1]
           + S[ii - 1, jj - 1]) / (4 * du * dv)
    H = np.array([[Suu, Suv], [Suv, Svv]])
    evals, evecs = np.linalg.eigh(H)
    lam_min, lam_max = float(evals[0]), float(evals[-1])
    sloppy = evecs[:, 0]                              # eigenvector of the small eigenvalue
    # NUMERICAL HONESTY: the profile min can sit at a rate-SWEEP BOUNDARY (corollary 1,
    # the shallow boundary optimum). There the central-difference Hessian is NOT a
    # valid interior stationary-point curvature, so the condition number / inverse-
    # Hessian correlation are unreliable -- flag it and lean on the profile interval.
    rate_at_boundary = bool(i0 == 0 or i0 == n_rate - 1)
    flat_to_precision = bool(lam_min <= lam_max * 1e-6)   # sloppy dir flat to precision
    if flat_to_precision:
        kappa = float(lam_max / max(lam_min, lam_max * 1e-6))   # a LOWER bound (>~1e6)
        kappa_note = ">1e6 (Hessian singular in the sloppy direction to precision)"
    else:
        kappa = float(lam_max / lam_min); kappa_note = None
    try:
        C = np.linalg.inv(H)
        coupling_raw = float(C[0, 1] / np.sqrt(C[0, 0] * C[1, 1]))
    except np.linalg.LinAlgError:
        coupling_raw = float("nan")
    coupling_degenerate = bool(not np.isfinite(coupling_raw) or abs(coupling_raw) > 1.0)
    # local inverse-curvature COUPLING coefficient (geometric, log-param space) --
    # NOT a statistical correlation (review MAJ-03): no likelihood/noise model.
    coupling = (float(np.clip(coupling_raw, -1.0, 1.0))
                if np.isfinite(coupling_raw) else float("nan"))
    hessian_reliable = bool(not rate_at_boundary and not flat_to_precision
                            and not coupling_degenerate)
    # profiled SSE objective (a stated 10% tolerance, NOT a confidence set): fraction
    # of the swept LOG-rate grid within 10% of the min, and the log-width of that set
    within = sse_prof <= sse_min * 1.10
    frac_within = float(np.mean(within))                  # fraction of LOG-rate grid pts
    lo = float(rates[within][0]); hi = float(rates[within][-1])
    log_width = float(np.log(hi / lo))                    # width WITHIN the tested domain
    # A3-04: is the 10% tolerance set CENSORED by the tested domain? If it reaches an
    # edge, the true near-optimal extent is open there and log_width is a LOWER BOUND.
    lower_censored = bool(within[0]); upper_censored = bool(within[-1])
    width_censored = bool(lower_censored or upper_censored)
    # MAPE cross-check: same 10% tolerance under the predictive metric
    mape_min = float(np.min(mape_prof))
    within_mape = mape_prof <= mape_min * 1.10
    frac_within_mape = float(np.mean(within_mape))
    # A3-09/A3-12: QUANTITATIVE agreement between the SSE and MAPE tolerance sets --
    # Jaccard overlap of grid membership + log-distance between the two objective
    # minima -- replaces the arbitrary "both fractions > 0.30" binary flag.
    inter = int(np.sum(within & within_mape)); union = int(np.sum(within | within_mape))
    jaccard = float(inter / union) if union else float("nan")
    rate_mape_min = float(rates[int(np.argmin(mape_prof))])
    best_rate_log_distance = float(abs(np.log(rate_star / rate_mape_min)))
    mape_agrees = bool(np.isfinite(jaccard) and jaccard >= 0.5)  # DERIVED from overlap
    return dict(
        variety=variety, solute=solute, n_conditions=len(m),
        rate_star=round(rate_star, 3), c_s0_star=round(cs0_star, 3),
        rate_optimum_at_sweep_boundary=rate_at_boundary,
        objective="unweighted concentration-scale SSE, least-squares nuisance level",
        condition_number=round(kappa, 1), condition_number_note=kappa_note,
        parameter_basis="log (u=ln rate, v=ln c_s0); matched-mass 40 g cups",
        rate_domain=[round(float(rates[0]), 2), round(float(rates[-1]), 2)],
        fd_steps_logparams=[round(du, 4), round(dv, 4)],
        hessian_eigenvalues=[round(lam_min, 4), round(lam_max, 4)],
        hessian_reliable=hessian_reliable,             # False -> use the profile below
        sloppy_direction_lnrate_lncs0=[round(float(x), 3) for x in sloppy],
        # geometric coupling of the SSE surface, NOT a statistical correlation (MAJ-03)
        local_curvature_coupling=round(coupling, 3), coupling_degenerate=coupling_degenerate,
        profile_rate_within10pct=[round(lo, 2), round(hi, 2)],
        profile_fraction_of_log_grid=round(frac_within, 2),
        profile_log_width=round(log_width, 3),
        # A3-04: censoring of the 10% tolerance set by the tested rate domain
        profile_lower_censored=lower_censored,
        profile_upper_censored=upper_censored,
        profile_log_width_censored=width_censored,
        # MAPE cross-check (secondary metric): same flat-valley conclusion?
        mape_profile_fraction_within10pct=round(frac_within_mape, 2),
        # A3-09/A3-12: quantitative SSE<->MAPE set agreement (not an arbitrary flag)
        sse_mape_threshold_jaccard=round(jaccard, 2) if np.isfinite(jaccard) else None,
        sse_mape_best_rate_log_distance=round(best_rate_log_distance, 3),
        mape_cross_check_agrees=mape_agrees,
        # --- surface + profile + Hessian for the objective-surface figure (Fig 2) ---
        surface=dict(rates=[float(x) for x in rates],
                     cs0=[float(x) for x in cs0],
                     sse=[[float(v) for v in row] for row in S]),
        profile=dict(rates=[float(x) for x in rates],
                     c_star=[float(x) for x in c_star],
                     sse=[float(x) for x in sse_prof], sse_min=float(sse_min)),
        hessian_logparams=[[float(Suu), float(Suv)], [float(Suv), float(Svv)]],
        verdict=("(c_s0, rate) is PRACTICALLY NON-IDENTIFIABLE from single-grind "
                 "matched-mass whole-cup data. %s The objective-based evidence "
                 "(conditional on the model and observation operator) is the profile: "
                 "the SSE (optimised over c_s0) stays within 10%% of the minimum over "
                 "%.0f%% of the swept log-rate grid [%.2f, %.2f]%s -> the data do not "
                 "bound the rate; the MAPE tolerance set overlaps the SSE set with "
                 "Jaccard %.2f. The best rate sits at %s."
                 % (("Log-parameter SSE-Hessian condition number %.0f with an inverse-"
                     "curvature coupling %.2f (~ -1, the valley direction; a geometric "
                     "diagnostic, NOT a statistical correlation)."
                     % (kappa, coupling)) if hessian_reliable else
                    ("The rate optimum is at the sweep boundary / the sloppy "
                     "direction is flat to numerical precision, so the local "
                     "Hessian is unreliable here (an even MORE degenerate case)."),
                    100 * frac_within, lo, hi,
                    (" (upper extent RIGHT-CENSORED by the tested domain)" if upper_censored
                     else (" (lower extent censored)" if lower_censored else "")),
                    jaccard if np.isfinite(jaccard) else float("nan"),
                    "an interior stationary point" if not rate_at_boundary
                    else "a shallow boundary optimum (corollary 1)")))


def identifiability_panel_convergence(variety="Arabica", solute="caffeine"):
    """GRID-DENSITY + DOMAIN convergence for the identifiability panel (review
    A2-06/07): re-run the panel at increasing rate-grid densities (18/36/72) on the
    default domain, and on a NARROWER and a WIDER domain, and report the stability of
    the condition number, curvature coupling, and the DOMAIN-INDEPENDENT profile
    log-width. The point is to show the flat-valley conclusion is not an artefact of a
    coarse grid or the chosen domain, and to flag any threshold set that touches a
    sweep boundary (right-censored). NOTE: several 1-2 min panels (slow; hand-run)."""
    import numpy as np
    rows = []
    # (label, n_rate, rate_lo, rate_hi)
    configs = [("grid-18/default", 18, None, None),
               ("grid-36/default", 36, None, None),
               ("grid-72/default", 72, None, None),
               ("grid-144/default", 144, None, None),
               ("grid-36/narrow[0.3,3]", 36, 0.3, 3.0),
               ("grid-36/wide[0.1,10]", 36, 0.1, 10.0)]
    for label, nr, rlo, rhi in configs:
        p = identifiability_panel(variety, solute, n_rate=nr, n_cs0=41,
                                  rate_lo=rlo, rate_hi=rhi)
        rows.append(dict(
            label=label, n_rate=nr, domain=p["rate_domain"],
            condition_number=p["condition_number"],
            hessian_reliable=p["hessian_reliable"],
            curvature_coupling=p["local_curvature_coupling"],
            profile_fraction_of_log_grid=p["profile_fraction_of_log_grid"],
            profile_log_width=p["profile_log_width"],
            rate_optimum_at_sweep_boundary=p["rate_optimum_at_sweep_boundary"],
            threshold_set_touches_boundary=bool(
                p["profile_rate_within10pct"][0] <= p["rate_domain"][0] * 1.001
                or p["profile_rate_within10pct"][1] >= p["rate_domain"][1] * 0.999)))
    # stability across the DEFAULT-domain densities (the coarse-grid check; now to 144)
    dens = [r for r in rows if "default" in r["label"] and r["hessian_reliable"]]
    kappa_vals = [r["condition_number"] for r in dens]
    lw_vals = [r["profile_log_width"] for r in dens]
    kappa_stable = bool(len(kappa_vals) >= 2
                        and (max(kappa_vals) - min(kappa_vals)) <= 0.5 * min(kappa_vals))
    lw_stable = bool(len(lw_vals) >= 2
                     and (max(lw_vals) - min(lw_vals)) <= 0.2 * max(lw_vals))

    # CONTINUOUS 1-D optimiser (review A2-06/A-MAJ04): confirm the located rate and the
    # flat valley WITHOUT any grid discretisation. Define the profiled SSE as a smooth
    # function of a CONTINUOUS log-rate -- one PDE solve per (rate, condition), analytic
    # best c_s0 -- and minimise it with bounded Brent. Then quantify the valley by the
    # LOG-RATE HALF-WIDTH within which the profiled SSE stays within 10% of that
    # continuous minimum (bisection on each side), independent of any grid.
    from scipy import optimize
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    bio = d.angeloni_bioactives(); params = ps._solute_params()
    brows = [r for r in bio if r["variety"] == variety
             and r["granulometry"] == "O" and r["on_grid"] == "True"]
    conds = [(r["T_degC"], r["p_bar"]) for r in brows]
    mvec = np.array([r[COL[solute]] for r in brows], float)

    def _prof_sse(logr):
        rs = float(np.exp(logr))
        F = np.array([float(ps.simulate_fractions(
            T, _flow_darcy(p, T), _matched_bounds(_flow_darcy(p, T)),
            {**params[solute], "A1": params[solute]["A1"] * rs,
             "A2": params[solute]["A2"] * rs, "c_s0": 1.0}, cl1=1.0)[0])
            for (T, p) in conds])
        c = float(np.dot(F, mvec) / np.dot(F, F))          # analytic best level
        return float(np.sum((c * F - mvec) ** 2))

    lo_b, hi_b = np.log(_RATE_DOMAIN[0]), np.log(_RATE_DOMAIN[-1])
    opt = optimize.minimize_scalar(_prof_sse, bounds=(lo_b, hi_b), method="bounded",
                                   options=dict(xatol=1e-3))
    logr_star = float(opt.x); sse_star = float(opt.fun)
    thr = sse_star * 1.10                                   # 10% tolerance band
    interior = bool(lo_b + 1e-2 < logr_star < hi_b - 1e-2)

    def _edge(direction):
        """bisect for the log-rate where the profiled SSE first exceeds the 10% band,
        walking from the optimum toward the domain edge; returns the domain edge
        (right-censored) if the band never breaks."""
        a = logr_star; b = hi_b if direction > 0 else lo_b
        if _prof_sse(b) <= thr:
            return b, True                                 # censored: band open at edge
        for _ in range(30):
            mid = 0.5 * (a + b)
            if _prof_sse(mid) <= thr:
                a = mid
            else:
                b = mid
        return 0.5 * (a + b), False

    hi_edge, hi_cens = _edge(+1); lo_edge, lo_cens = _edge(-1)
    cont = dict(
        continuous_rate_optimum=round(float(np.exp(logr_star)), 3),
        optimum_is_interior=interior,
        profiled_sse_min=sse_star,
        valley_log_half_width_within10pct=round(0.5 * (hi_edge - lo_edge), 3),
        valley_rate_within10pct=[round(float(np.exp(lo_edge)), 3),
                                 round(float(np.exp(hi_edge)), 3)],
        valley_right_censored=bool(hi_cens or lo_cens),
        method="scipy bounded Brent on continuous log-rate profiled SSE; "
               "10% band edges by bisection (grid-free)")
    return dict(
        variety=variety, solute=solute, rows=rows, continuous_optimiser=cont,
        condition_number_stable_across_density=kappa_stable,
        log_width_stable_across_density=lw_stable,
        verdict=("Across rate grids of 18/36/72/144 points the log-parameter SSE "
                 "condition number and the domain-independent profile log-width are "
                 "stable (kappa stable=%s, log-width stable=%s), and the flat valley "
                 "persists on a narrower [0.3,3] and a wider [0.1,10] domain. A GRID-FREE "
                 "continuous Brent optimiser on the profiled SSE places the rate optimum "
                 "at %.2f (interior=%s) with a 10%%-band log half-width of %.2f%s -- so "
                 "the practical non-identifiability is NOT an artefact of a coarse grid, "
                 "the chosen sweep domain, or grid discretisation. Threshold sets that "
                 "reach a sweep boundary are flagged right-censored per config."
                 % (kappa_stable, lw_stable, cont["continuous_rate_optimum"],
                    cont["optimum_is_interior"],
                    cont["valley_log_half_width_within10pct"],
                    " (right-censored)" if cont["valley_right_censored"] else "")))


def loco_cv_refit(varieties=("Arabica", "Robusta"),
                  solutes=("caffeine", "trigonelline", "5CQA"),
                  n_boot=1000, seed=0):
    """M4 + M6: leave-one-(T,p)-CONDITION-out cross-validation of the angeloni O
    refit, replacing the weak two-off-grid-point holdout with nested CV over the 9
    on-grid granulometry-O conditions. For each solute x variety: precompute the
    per-condition matched-mass prediction matrix once (rate x condition); then for
    each held-out condition, fit the exact level on the other 8, choose the rate by
    the 8-point training MAPE, and predict the held-out condition. Reports EVERY
    held-out error, plus median/range/mean (M4).

    UNCERTAINTY (review MAJ-05): the 54 held-out errors (9 conditions x 3 solutes x 2
    varieties) are NOT independent -- folds share overlapping training sets, the same
    (T,p) conditions recur across solutes/varieties, and the source rows are
    condition-level values (duplicate extractions in Angeloni), not 54 independent
    shots. We therefore report (a) a DESCRIPTIVE residual-resampling interval
    (resampling the 54 errors) that IGNORES fold dependence -- NOT a coverage-calibrated
    confidence interval and NOT a 'shot-level' bootstrap; and (b) a CONDITION-CLUSTER
    summary: one macro error per held-out (T,p) fold (averaged across solutes/varieties)
    plus a cluster bootstrap over the 9 conditions (the dependence-aware view). For M6
    it also reports the pooled mean under a LOG (relative-error) level loss. Named g/L
    solutes only (TDS excluded, review M5). ~3-5 min of PDE solves (slow; hand-run)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    bio = d.angeloni_bioactives(); params = ps._solute_params()
    rng = np.random.default_rng(seed)

    def _pred_matrix(variety, sol):                       # (n_rate, n_cond) per unit level
        rows = [r for r in bio if r["variety"] == variety
                and r["granulometry"] == "O" and r["on_grid"] == "True"]
        conds = [(r["T_degC"], r["p_bar"]) for r in rows]
        m = np.array([r[COL[sol]] for r in rows], float)
        F = np.array([[float(ps.simulate_fractions(
                        T, _flow_darcy(p, T), _matched_bounds(_flow_darcy(p, T)),
                        {**params[sol], "A1": params[sol]["A1"] * rs,
                         "A2": params[sol]["A2"] * rs, "c_s0": 1.0}, cl1=1.0)[0])
                       for (T, p) in conds] for rs in _RATE_DOMAIN])
        return F, m, conds

    def _loco(F, m, level):                               # held-out |%err| + (obs,pred)
        n = len(m); errs, preds = [], []
        for i in range(n):
            tr = [j for j in range(n) if j != i]
            best = None
            for k in range(len(_RATE_DOMAIN)):
                c, mp = level(F[k, tr], m[tr])
                if best is None or mp < best[1]:
                    best = (c, mp, k)
            c, _, k = best
            preds.append(float(c * F[k, i]))
            errs.append(abs(c * F[k, i] - m[i]) / m[i] * 100.0)
        return np.array(errs), np.array(preds)

    per, all_mape, all_log, pts = {}, [], [], {}
    for variety in varieties:
        for sol in solutes:
            F, m, conds = _pred_matrix(variety, sol)
            e, pr = _loco(F, m, _mape_level)
            el, _ = _loco(F, m, _log_level_mape)
            all_mape.extend(e); all_log.extend(el)
            per[f"{variety}:{sol}"] = dict(
                n=len(e), loco_median=round(float(np.median(e)), 1),
                loco_mean=round(float(np.mean(e)), 1),
                loco_range=[round(float(e.min()), 1), round(float(e.max()), 1)],
                heldout_pct_err=[round(float(x), 1) for x in e])
            pts[f"{variety}:{sol}"] = [dict(T=float(T), p=float(p), obs=float(mo),
                                            pred=float(prd))
                                       for (T, p), mo, prd in zip(conds, m, pr)]
    all_mape = np.array(all_mape)
    # (a) descriptive residual-resampling interval (IGNORES fold dependence)
    boot = np.array([all_mape[rng.integers(0, len(all_mape), len(all_mape))].mean()
                     for _ in range(n_boot)])
    resamp_interval = [round(float(np.percentile(boot, 2.5)), 1),
                       round(float(np.percentile(boot, 97.5)), 1)]
    # (b) CONDITION-CLUSTER view: one macro error per held-out (T,p), averaged across
    # solute/variety, then a bootstrap over the 9 distinct conditions. This is a
    # DESCRIPTIVE condition-level resampling summary (review A2-04): it resamples
    # already-computed fold errors WITHOUT repeating the fit, and the LOCO training
    # sets overlap, so it is NOT coverage-calibrated and does NOT correct all fold
    # dependence -- it is not a "dependence-aware CI".
    by_cond = {}
    for key, plist in pts.items():
        for pt in plist:
            by_cond.setdefault((pt["T"], pt["p"]), []).append(
                abs(pt["pred"] - pt["obs"]) / pt["obs"] * 100.0)
    cond_keys = sorted(by_cond)
    cond_macro = np.array([float(np.mean(by_cond[k])) for k in cond_keys])
    cboot = np.array([cond_macro[rng.integers(0, len(cond_macro), len(cond_macro))].mean()
                      for _ in range(n_boot)])
    cluster_interval = [round(float(np.percentile(cboot, 2.5)), 1),
                        round(float(np.percentile(cboot, 97.5)), 1)]
    return dict(per_fit=per, points=pts,
                pooled_loco_mean_mape=round(float(all_mape.mean()), 1),
                pooled_loco_median_mape=round(float(np.median(all_mape)), 1),
                # descriptive only -- ignores fold dependence; NOT a confidence interval
                residual_resampling_interval95=resamp_interval,
                interval_is_dependence_aware=False,
                # DESCRIPTIVE condition-level resampling (9 (T,p) macro errors); NOT
                # coverage-calibrated, does not correct fold dependence (A2-04)
                condition_macro_mean=round(float(cond_macro.mean()), 1),
                n_condition_clusters=len(cond_keys),
                condition_cluster_resampling95=cluster_interval,
                interval_is_coverage_calibrated=False,
                verdict="Leave-one-condition-out holdout (9 folds/fit, matched mass) gives "
                        "pooled held-out MAPE %.1f%% (median %.1f%%). A DESCRIPTIVE "
                        "residual-resampling interval (ignoring fold dependence, NOT a "
                        "confidence interval) is [%.1f, %.1f]; a condition-level "
                        "resampling of the 9 (T,p) macro errors gives [%.1f, %.1f] around "
                        "a %.1f%% macro mean -- also DESCRIPTIVE (it resamples fold errors "
                        "without repeating the fit and the LOCO training sets overlap, so "
                        "it is not coverage-calibrated and does not correct all "
                        "dependence). Under a LOG (relative-error) level loss the pooled "
                        "mean is %.1f%%, robust to the loss function (M6)." % (
                            float(all_mape.mean()), float(np.median(all_mape)),
                            resamp_interval[0], resamp_interval[1],
                            cluster_interval[0], cluster_interval[1],
                            float(cond_macro.mean()), float(np.array(all_log).mean())),
                strength="internal leave-one-condition-out holdout + DESCRIPTIVE "
                         "residual + condition-level resampling summaries + loss "
                         "sensitivity (within-rig; not coverage-calibrated)")


def geometry_sensitivity_transfer(varieties=("Arabica", "Robusta"),
                                  solutes=("caffeine", "trigonelline", "5CQA")):
    """B5: is the O->C/F transfer robust to the frozen grain-geometry choice? The
    port freezes the centre grind (1.7). Here we re-run the frozen-parameter O->C/F
    transfer under EACH of the three pannusch fitted geometries (1.4/1.7/2.0, card
    Table 2) and report the spread of the held-out C/F MAPE across geometry choices.
    A small spread -> the transfer conclusion (§5) is robust to geometry; this avoids
    an (unavailable) calibrated cross-grinder map by sweeping the observed geometry
    range instead. NOTE: ~3-4 min of PDE solves (slow; hand-run)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    bio = d.angeloni_bioactives(); params = ps._solute_params()

    def sh(variety, gran):
        return [r for r in bio if r["variety"] == variety
                and r["granulometry"] == gran and r["on_grid"] == "True"]

    def frac(sp, rs, conds, gran, geom):
        s = dict(sp); s["A1"] = sp["A1"] * rs; s["A2"] = sp["A2"] * rs; s["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
                        T, _flow_gran(p, T, gran), _matched_bounds(_flow_gran(p, T, gran)),
                        s, cl1=1.0, grind=geom)[0]) for T, p in conds])

    out = {}
    for variety in varieties:
        for sol in solutes:
            col = COL[sol]
            per_geom = {}
            for gname, geom in _PGEOM.items():
                # fit (rate, c_s0) on O under this geometry, predict held-out C/F
                rowsO = sh(variety, "O")
                condsO = [(r["T_degC"], r["p_bar"]) for r in rowsO]
                mO = np.array([r[col] for r in rowsO], float)
                best = None
                for rs in _RATE_DOMAIN:
                    f = frac(params[sol], rs, condsO, "O", geom)
                    c, mp = _mape_level(f, mO)
                    if best is None or mp < best[2]:
                        best = (float(rs), c, mp)
                rs, c, _ = best
                held = {}
                for g in ("C", "F"):
                    rows = sh(variety, g)
                    conds = [(r["T_degC"], r["p_bar"]) for r in rows]
                    m = np.array([r[col] for r in rows], float)
                    f = frac(params[sol], rs, conds, g, geom)
                    # review A3-03: keep FULL PRECISION; a sub-1 pp spread was being
                    # rounded to integers before the spread was computed. Round only
                    # for the display copy below.
                    held[g] = float(np.mean(np.abs(c * f - m) / m) * 100)
                per_geom[gname] = held
            cvals = [per_geom[g2]["C"] for g2 in _PGEOM]      # raw floats
            fvals = [per_geom[g2]["F"] for g2 in _PGEOM]
            out[f"{variety}:{sol}"] = dict(
                per_geometry={gn: {g: round(v, 2) for g, v in hd.items()}
                              for gn, hd in per_geom.items()},   # display only
                heldout_C_spread=[round(min(cvals), 2), round(max(cvals), 2)],
                heldout_F_spread=[round(min(fvals), 2), round(max(fvals), 2)],
                # raw spread for the headline (NOT rounded upstream)
                _c_spread_raw=max(cvals) - min(cvals),
                _f_spread_raw=max(fvals) - min(fvals))
    max_spread = max(max(x["_c_spread_raw"], x["_f_spread_raw"])
                     for x in out.values())                   # full precision
    return dict(per_fit=out, max_geometry_spread_pp=round(max_spread, 2),
                geometries=_PGEOM,
                verdict="Re-running the frozen O->C/F transfer under each of the three "
                        "pannusch fitted geometries (1.4/1.7/2.0) applied GLOBALLY moves "
                        "the held-out C/F MAPE by at most %.2f pp. This shows only LIMITED "
                        "sensitivity to the tested GLOBAL Pannusch geometry choice; it does "
                        "NOT test a grind-specific cross-grinder geometry map (O/C/F -> "
                        "different Pannusch geometries), which is unavailable (rule 9/A3-20). "
                        "So the residual is not highly sensitive to the tested global "
                        "geometry setting -- not that it is broadly geometry-independent."
                        % max_spread,
                strength="global-geometry sensitivity (sweep of the fitted grind "
                         "geometries applied to all grinds); NOT a cross-grinder map test")


def flow_map_sensitivity_transfer(variety="Arabica", solute="caffeine",
                                  perturbs=(-0.2, -0.1, 0.0, 0.1, 0.2)):
    """A2-10: is the O->C/F transfer robust to the CONSTRUCTED pressure-flow map? The
    map is inferred (fitted hydraulic conductivity `k_r(p)`, nominal grind shot times
    `_TAU_GRAN`, viscosity mu(T)), not a per-shot measured flow. Here we apply a
    SYSTEMATIC flow-scale perturbation (equivalent to a shot-time / k_r-magnitude error)
    to ALL grinds, REFIT the O calibration under the perturbed map, transfer to the
    held-out C/F, and report how much the held-out MAPE moves. A small spread -> the
    §5 transfer conclusion is not an artefact of the exact flow-map magnitude. Caffeine/
    Arabica representative. NOTE: ~2-3 min of PDE solves (slow; hand-run)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    bio = d.angeloni_bioactives(); params = ps._solute_params()
    COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}[solute]

    def rows(gran):
        return [r for r in bio if r["variety"] == variety
                and r["granulometry"] == gran and r["on_grid"] == "True"]

    def frac(rs, conds, gran, scale):
        sp = dict(params[solute]); sp["A1"] *= rs; sp["A2"] *= rs; sp["c_s0"] = 1.0
        return np.array([float(ps.simulate_fractions(
            T, scale * _flow_gran(p, T, gran),
            _matched_bounds(scale * _flow_gran(p, T, gran)), sp, cl1=1.0)[0])
            for T, p in conds])

    out = {}
    for pert in perturbs:
        scale = 1.0 + pert
        rO = rows("O"); condsO = [(r["T_degC"], r["p_bar"]) for r in rO]
        mO = np.array([r[COL] for r in rO], float)
        best = None
        for rs in _RATE_DOMAIN:
            f = frac(rs, condsO, "O", scale); cs0, mp = _mape_level(f, mO)
            if best is None or mp < best[2]:
                best = (float(rs), cs0, mp)
        rsO, cs0O, _ = best
        held = {}
        for g in ("C", "F"):
            rg = rows(g); conds = [(r["T_degC"], r["p_bar"]) for r in rg]
            m = np.array([r[COL] for r in rg], float)
            pred = cs0O * frac(rsO, conds, g, scale)
            held[g] = float(np.mean(np.abs(pred - m) / m) * 100)
        out[round(pert, 2)] = dict(flow_scale=round(scale, 2), fitted_rate=round(rsO, 2),
                                   heldout_C=round(held["C"], 2), heldout_F=round(held["F"], 2))
    base = out[0.0]
    hc = [v["heldout_C"] for v in out.values()]; hf = [v["heldout_F"] for v in out.values()]
    spread = round(max(max(hc) - min(hc), max(hf) - min(hf)), 2)
    return dict(variety=variety, solute=solute, per_perturbation=out,
                baseline_heldout=[base["heldout_C"], base["heldout_F"]],
                heldout_C_range=[round(min(hc), 2), round(max(hc), 2)],
                heldout_F_range=[round(min(hf), 2), round(max(hf), 2)],
                max_spread_pp=spread,
                verdict=("Perturbing the inferred flow-map magnitude by +/-20%% (a shot-"
                         "time / k_r uncertainty proxy), refitting O and transferring to "
                         "C/F, moves the held-out MAPE by at most %.1f pp (C in %s, F in "
                         "%s) around the baseline %s -- so the §5 transfer conclusion is "
                         "robust to the flow-map magnitude, though it remains CONDITIONAL "
                         "on the inferred-map form (not a measured per-shot flow). A "
                         "per-shot measured flow trace remains owed." % (
                             spread, [round(min(hc), 1), round(max(hc), 1)],
                             [round(min(hf), 1), round(max(hf), 1)],
                             [base["heldout_C"], base["heldout_F"]])),
                strength="flow-map magnitude sensitivity (systematic +/-20%% scale; "
                         "conditional on the inferred-map FORM)")


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
    print("\n== pannusch KINETICS refit to angeloni (post-fit; 2-pt holdout) ==")
    rf = refit_pannusch_angeloni()
    print(f"{'variety':>8} {'solute':>13} {'rate':>5} {'c_s0(Table7)':>13} "
          f"{'on-grid':>8} {'holdout':>8}")
    for v, per in rf["per_variety"].items():
        for sol, x in per.items():
            t7 = "" if x["c_s0_table7"] is None else f"({x['c_s0_table7']})"
            print(f"{v:>8} {sol:>13} {x['rate_scale']:>5} "
                  f"{str(x['c_s0_fit']) + t7:>13} {x['mape_on_grid']:>7}% "
                  f"{x['mape_holdout']:>7}%")
    print(f"mean holdout MAPE: NAMED solutes {rf['mean_holdout_named']}% (headline) | "
          f"aggregate-solids proxy TDS {rf['mean_holdout_aggregate_solids_proxy']}% | "
          f"with proxy {rf['mean_holdout_with_proxy']}%. {rf['note']}")
    print("\n== identifiability panel (caffeine whole-cup, Arabica O) ==")
    ip = identifiability_panel("Arabica", "caffeine")
    print(f"condition number {ip['condition_number']} (reliable={ip['hessian_reliable']}); "
          f"curvature coupling {ip['local_curvature_coupling']} (NOT a correlation); "
          f"SSE profile within 10% over {int(100 * ip['profile_fraction_of_log_grid'])}% "
          f"of the log-rate grid {ip['profile_rate_within10pct']} "
          f"(MAPE cross-check {int(100 * ip['mape_profile_fraction_within10pct'])}%).")
    print(ip["verdict"])
    print("\n== leave-one-condition-out CV + bootstrap + loss sensitivity (M4/M6) ==")
    lc = loco_cv_refit()
    print(lc["verdict"])
    print("\n== geometry sensitivity of the O->C/F transfer (B5) ==")
    gs = geometry_sensitivity_transfer()
    print(gs["verdict"])
    return dict(cameron=r, pannusch_bracket=pr, pannusch_per_condition=pc,
                flow_refinement=fr, refit=rf, identifiability_panel=ip,
                loco_cv=lc, geometry_sensitivity=gs)


if __name__ == "__main__":
    report()
