"""Smoke tests for Phase 0 dataset loaders (DoD: loader smoke tests).

These assert structure and a few card-anchored values; they are NOT validation
gates (no model runs here).
"""
import numpy as np

from puckworks import data as pwdata


def test_waszkiewicz_traces_11_pressures():
    t = pwdata.waszkiewicz_traces()
    pressures = sorted(k for k in t if k != "columns")
    assert pressures == pwdata.WASZ_PRESSURES_BAR
    # each pressure has aligned columns and a plausible flow-rate channel
    for p in pressures:
        q = t[p]["mass_flow_rate__g_per_s"]
        assert q.size > 100 and np.isfinite(q).any()
    assert "basket_pressure__bar" in t["columns"]


def test_cameron_fig5_grind_deviation():
    rows = pwdata.cameron2020_fig5_grind_deviation()
    assert [r["gs"] for r in rows] == [1.1, 1.3, 1.5]         # the three Fig-5 grinds
    assert [r["rel_deviation"] for r in rows] == [0.131, 0.061, 0.026]
    assert all(0 < r["rel_deviation"] < 1 for r in rows)      # fractions, not percents


def test_waszkiewicz_static_calibration_matches_card():
    c = pwdata.waszkiewicz_static_calibration()
    # card: (Q_c, P_c) = (1.90 g/s, 12 bar)
    assert abs(c["P_c_bar"] - 12.39) < 0.1
    assert abs(c["Q_c_g_per_s"] - 1.897) < 0.01


def test_waszkiewicz_tds_fractions():
    f = pwdata.waszkiewicz_tds_fractions()
    assert f["time_s"].size == 12
    assert f["time_s"][0] == 2.5 and f["time_s"][-1] == 57.5
    assert 0 < np.nanmax(f["tds_pct"]) < 30


def test_waszkiewicz_constants_and_brewer():
    k = pwdata.waszkiewicz_constants()
    assert abs(k["dose__g"] - 18.5) < 0.01
    assert abs(k["mu__Pas"] - 3.15e-4) < 1e-6
    b = pwdata.waszkiewicz_brewer_quadratic()
    assert set(b) == {"a", "b", "c"} and b["a"] > 0


def test_waszkiewicz_psd_shape():
    psd = pwdata.waszkiewicz_psd()
    assert psd["size_um"].size == 48
    assert psd["volume_pct"].shape[1] == 48
    assert psd["volume_pct"].shape[0] >= 1


# --- schmieder2023 (0.1) ---
def test_schmieder_table_a1_matches_card():
    rows = pwdata.schmieder_kinetics_fit_avg()
    assert len(rows) == 60  # 15 exp x 4 components
    e7 = [r for r in rows if r["exp"] == 7 and r["component"] == "caffeine"][0]
    # card central point: caffeine c0=9.71, lambda=23.09
    assert abs(e7["c0"] - 9.70981) < 1e-4
    assert abs(e7["lambda_g"] - 23.09434) < 1e-4


def test_schmieder_reps_and_cupmasses():
    reps = pwdata.schmieder_kinetics_fit_reps()
    assert len(reps) == 192  # 48 exp-rep x 4 components
    comps = {r["component"] for r in reps}
    assert comps == {"trigonelline", "caffeine", "5-CQA", "TDS"}
    cups = pwdata.schmieder_cup_masses()
    assert len(cups) == 612  # 48 exp-rep x 4 comp x 3 BR
    assert {r["brew_ratio"] for r in cups} == {"1/1", "1/2", "1/3"}


def test_wadsworth_grindmap_table1():
    rows = pwdata.wadsworth_grindmap_table1()
    assert len(rows) == 22  # 2 coffees x 11 settings
    assert {r["coffee"] for r in rows} == {"Guayacan", "Tumba"}
    # S = <R><R2>/<R3> reconstructs the reported S column (moments consistent)
    r = rows[0]
    S = r["R_mean_m"] * r["R2_mean_m2"] / r["R3_mean_m3"]
    assert abs(S - r["S_polydispersivity"]) < 5e-3


def test_liang_figures_load():
    f3 = pwdata.liang_fig3_tds()
    assert len(f3) > 20 and "TDS_percent" in f3[0]
    f4 = pwdata.liang_fig4_E()
    assert {r["measurement"] for r in f4} == {"equilibrium", "oven_drying"}
    assert len(pwdata.liang_fig5_cupping()) > 0


def test_moroney_figures_load():
    f6 = pwdata.moroney_fig6()
    assert len(f6) > 5 and f6[0]["c_h_nondimensional"] > 0.9  # starts saturated
    t1 = {r["symbol"]: r["value"] for r in pwdata.moroney_table1()}
    assert float(t1["a2"]) == 5.139 and float(t1["a3"]) == 0.473


def test_grudeva_data_load():
    p = {r["symbol"]: r for r in pwdata.grudeva_params()}
    assert "kappa" in p and "ADJUDICATED" in p["kappa"]["classification"]
    v = pwdata.grudeva_vial_stats()
    assert len(v) == 16
    total = sum(r["solubles_mean_g"] for r in v)
    assert 2.5 < total < 3.5  # ~3 g total solubles per shot


def test_pannusch_table2_load():
    t = {r["solute"]: r for r in pwdata.pannusch_table2()}
    assert set(t) == {"caffeine", "trigonelline", "5CQA", "tds"}
    assert abs(t["caffeine"]["K_ref"] - 0.81) < 1e-9
    assert t["trigonelline"]["gamma"] == -431


def test_foster_machine_mode():
    from puckworks.models.foster2025 import machine_mode as fm
    p = {r["symbol"]: r for r in pwdata.foster2025_params()}
    assert abs(p["t_shift"]["value"] - 0.796) < 1e-9
    s_p, t_p_model, Q_p = fm.ponding()
    assert 0 < s_p < 1e-3 and Q_p > 0            # ponding front sub-mm, flow>0
    t_p, t_s = fm.reported_times()
    assert abs(t_p - 0.823) < 0.01 and abs(t_s - 6.669) < 0.02
    # Fig 15 flow-minimum + figure loaders
    q_min, t_min = fm.flow_minimum()
    assert abs(q_min - 0.181) < 0.02 and abs(t_min - 2.0) < 0.3
    assert len(pwdata.foster_fig15_flow()) > 100
    assert any(r["s_data_mm"] != "" for r in pwdata.foster_fig12_14_curves())


def test_mo2023_and_egidi_load():
    fr = pwdata.mo2023_forchheimer()
    assert len(fr) == 24 and {r["type"] for r in fr} == {"E", "H", "M", "F"}
    assert len(pwdata.mo2023_fig8a()) > 5
    eg = pwdata.egidi_table2()
    assert len(eg) == 12
    ey = [r["EY [%]"] for r in eg]
    assert 19.0 <= min(ey) and max(ey) <= 23.0


def test_schmieder_raw_fractions_and_rsm():
    frac = pwdata.schmieder_raw_fractions()
    assert len(frac) == 288 and frac[0]["fraction"] == 1.0
    rsm = pwdata.schmieder_rsm()
    assert len(rsm) == 12  # 4 components x 3 BR
    # spot-check a transcribed coefficient (Trigonelline BR 1/1 beta0 = 185.8)
    t11 = [r for r in rsm if r["component"] == "Trigonelline"
           and r["brew_ratio"] == "1/1"][0]
    assert abs(t11["beta0"] - 185.8) < 1e-6


def test_romancorrochano2017_intake():
    # Table 6.1 tamped permeability: 12 beds, literature 1e-14..1e-13 band,
    # coarser grind -> higher kappa at every density (robust physical signal).
    k = pwdata.roman_tamped_kappa()
    assert len(k) == 12
    kv = [r["kappa_m2"] for r in k]
    assert 1e-14 <= min(kv) and max(kv) <= 1e-12
    order = ["PsiB", "PsiC", "PsiD", "PsiE"]
    for rho in (360.0, 400.0, 480.0):
        seq = [next(r["kappa_m2"] for r in k
                    if r["grind"] == g and r["rho_bed_kg_m3"] == rho) for g in order]
        assert all(seq[i] < seq[i + 1] for i in range(3))
    # Deff map + partition K(T) monotone in T
    assert len(pwdata.roman_deff()) == 10
    ktab = pwdata.roman_partition_K()
    kbyT = {r["T_degC"]: r["K"] for r in ktab}
    assert kbyT[20.0] < kbyT[50.0] < kbyT[80.0]
    # Fig 7.4 parameter-free bed MPE: 15 conditions, med-MW <= 14.5%
    f74 = pwdata.roman_fig74_espresso()
    assert len(f74) == 15
    assert max(r["MPE_med_MW_pct"] for r in f74) <= 14.5


def test_mo2023_2_intake():
    # Table 1 granulometry (4 powders) + Table 2 k0
    g = pwdata.mo2_granulometry()
    assert {r["powder"] for r in g} == {"E", "H", "M", "F"}
    k0 = {r["powder"]: r["k0_m2"] for r in pwdata.mo2_k0()}
    # Carman-Kozeny closed form reproduces Table 2 from Table 1 (exact)
    eps, n = 0.17, 0.5
    pref = eps ** (3 + 2 * n) / (72.0 * (1 - eps) ** 2)
    for r in g:
        k_pred = pref * (r["d_32_um"] * 1e-6) ** 2
        assert abs(k_pred - k0[r["powder"]]) / k0[r["powder"]] < 0.03
    # Figs 6-9 fixed-flow data: yield rises with M_c, strength falls
    ys = pwdata.mo2_yield_strength()
    e2 = sorted([r for r in ys if r["powder"] == "E" and r["q_mL_s"] == 2],
                key=lambda r: r["M_c_g"])
    assert e2[0]["yield_pct"] < e2[-1]["yield_pct"]
    assert e2[0]["strength_pct"] > e2[-1]["strength_pct"]
    # Fig 3a swelling decay present at s_m=3.6%
    f = [r for r in pwdata.mo2_fig3a_qdecay() if r["s_m_pct"] == 3.6]
    assert len(f) > 50


def test_romancorrochano_y0_ceiling():
    rows = pwdata.roman_y0_extractable()
    y0 = {r["grind"]: r["y0_pct"] for r in rows if r["method"] == "dilute"}
    # §5.5 nested ceiling: y0(PsiA) > Cameron > Liang
    from puckworks.models.liang2021 import desorption as lg
    assert y0["PsiA"] / 100.0 > lg.cameron_inventory_ceiling() > lg.K_EMAX_1L
    # P3 #4 size-exclusion: monotone decrease along coarsening ladder
    order = ["PsiA", "PsiB", "PsiE", "PsiF", "PsiG", "PsiH"]
    seq = [y0[g] for g in order]
    assert all(seq[i] > seq[i + 1] for i in range(len(seq) - 1))


def test_fasano2000_partI_intake():
    # Cor 8.2 structural check: q_inf(p0) nonmonotone, peak tracks beta knee
    f86 = pwdata.fasano_fig8_6()
    f87 = pwdata.fasano_fig8_7()
    for s in ("beta1", "beta2"):
        pts = sorted((r["p0"], r["q"]) for r in f86 if r["series"] == s)
        ip = max(range(len(pts)), key=lambda i: pts[i][1])
        assert ip > 0 and pts[-1][1] < pts[ip][1]        # nonmonotone
        b = sorted((r["q"], r["beta"]) for r in f87 if r["series"] == s)
        assert b[0][1] > b[-1][1]                        # beta decreasing
    # Fig 8.4 reversal: inverted segment replays a big peak, resume stays low
    rows = pwdata.fasano_fig8_4()
    pk = lambda seg: max(r["discharge_ml_s"] for r in rows if r["segment"] == seg)
    assert pk(1) > 10 and pk(3) > 10 and pk(2) < pk(1) / 2


def test_romancorrochano_extraction_model():
    import numpy as np
    from puckworks.models.romancorrochano2017 import extraction as rx
    # sphere solver reproduces the Crank analytic release
    R, Deff = 1e-4, 2.5e-10
    t = np.array([1.0, 5.0, 20.0])
    assert np.max(np.abs(rx.crank_release(Deff, R, t)
                         - rx.sphere_release(Deff, R, t, N=100))) < 1e-3
    # stirred vessel -> partition equilibrium 1/(1+pore_to_bath/K)
    tt = np.linspace(0, 600, 80)
    _, f = rx.stirred_vessel(Deff, R, K=0.6, pore_to_bath=0.2, t_eval=tt)
    assert abs(f[-1] - 1.0 / (1 + 0.2 / 0.6)) < 0.02
    # bed conserves mass and yield rises monotonically
    b = rx.bed_lumped(Deff=2.5e-10, R=5e-5, K=0.6, Q=1.5e-6, eps_bed=0.4,
                      V_bed=5e-5, t_eval=np.linspace(0, 40, 150))
    assert np.all(np.abs(b["mass_balance"] - 1.0) < 0.02)
    assert np.all(np.diff(b["yield_frac"]) >= -1e-9)


def test_mo2023_2_swelling_model():
    import numpy as np
    from puckworks.models.mo2023_2 import swelling as sw
    # closed-form max swelling (Eq 8)
    assert abs(sw.s_max(0.1) - 3.57) < 0.05
    # Fig 3a flow decay: reproduces per-powder ratio + coarser-throttles-less order
    ratios = {pw: sw.flow_decay_ratio(pw) for pw in ("E", "H", "M", "F")}
    assert ratios["E"] < ratios["H"] < ratios["M"] < ratios["F"]
    assert abs(ratios["E"] - 0.0481) / 0.0481 < 0.2
    # swelling shrinks porosity and flow decays monotonically
    fd = sw.flow_decay("E", np.linspace(0, 60, 30))
    assert fd["eps_b"][-1] < 0.10 and np.all(np.diff(fd["q_rel"]) <= 1e-9)


def test_fasano_partI_freeboundary_model():
    import numpy as np
    from puckworks.models.fasano2000_partI import fines_migration as fm
    b1 = fm.beta_from_fig87("beta1")
    r = fm.simulate(1.0, b1)
    assert np.all(np.abs(r["mass_balance"] - 1.0) < 0.01)   # Eq 8.33
    assert np.all(np.diff(r["q"]) <= 1e-6)                   # Lemma 8.3 monotone
    assert np.all(r["s"] >= fm.s_min() - 1e-6)               # Lemma 8.1
    # nonmonotone q_inf(p0) with interior peak (Fig 8.6 shape)
    p0 = np.arange(0.2, 1.21, 0.2)
    Q = fm.q_infinity_curve(p0, b1)
    ip = int(np.argmax(Q))
    assert 0 < ip < len(p0) - 1 and Q[ip] > Q[0] and Q[ip] > Q[-1]


def test_mo2023_2_swelling_insensitivity():
    from puckworks.models.mo2023_2 import extraction as ex
    r = ex.swelling_insensitivity(powder="M", q_list=(2, 4))
    # fixed-q: swelling barely changes yield (Fig 2)
    assert r["fixedq_max_rel_diff"] < 0.05
    # but fixed-dP throttles hard (Fig 3a) -- the headline contrast
    assert r["fixeddp_flow_ratio"] < 0.2
    assert all(v["rises_with_Mc"] for v in r["per_flow"].values())


def test_angeloni2023_inventories():
    r = pwdata.angeloni_inventories()
    assert len(r) == 16
    assert {x["variety"] for x in r} == {"Arabica", "Robusta"}
    cf_a = [x["C0_s_mg_L"] for x in r if x["variety"] == "Arabica" and x["species"] == "CF"][0]
    assert cf_a == 12540.0


def test_angeloni2023_66shot_intake():
    bio = pwdata.angeloni_bioactives()
    assert len(bio) == 66 and {r["variety"] for r in bio} == {"Arabica", "Robusta"}
    assert abs([r for r in bio if r["sample"] == "A1"][0]["CF"] - 5.27) < 1e-9
    # 54 on-grid + 12 off-grid
    ong = sum(1 for r in bio if r["on_grid"] == "True")
    assert ong == 54 and len(bio) - ong == 12
    assert len(pwdata.angeloni_total_solids()) == 66
    assert len(pwdata.angeloni_lipids()) == 66


def test_schulman_baskets():
    b = pwdata.schulman_baskets()
    assert len(b) == 14
    vst18 = [x for x in b if x["basket"] == "VST 18"][0]
    assert abs(vst18["A_h_mm2"] - 69.3) < 1e-6 and vst18["grid"] == "H"


def test_mo2023_2_coupled_bed():
    from puckworks.models.mo2023_2 import coupled_bed as cb
    m = cb.fig8_metrics()
    assert m["mass_balance_floor"] > 0.90        # mass-conserving
    assert m["within_bars"] >= 5                  # beats reduced 4/9
    assert m["shape_spread_pct"] < 60             # beats reduced 110%


def test_bruno_roasted_composition():
    r = pwdata.bruno_roasted_composition()
    assert len(r) == 40                       # 10 compounds x 4 origins
    compounds = {x["compound"] for x in r}
    assert {"Caffeine", "Trigonelline", "Lipids"} <= compounds
    cf = {x["origin"]: float(x["mean"]) for x in r if x["compound"] == "Caffeine"}
    # card-anchored: Robusta (Nicaragua/Indonesia) ~2x Arabica (Mexico/Rwanda)
    assert abs(cf["Mexico"] - 8491.40) < 0.01
    assert cf["Nicaragua"] > 1.5 * cf["Mexico"]
    assert pwdata.bruno_roasted_composition_wide()[0]["unit"] == "mg/kg"


def test_khomyakov_kinematic_viscosity():
    r = pwdata.khomyakov_kinematic_viscosity()
    assert len(r) == 60                       # 10 solids x 6 temps
    solids = sorted({float(x["dry_solids_percent_w_w"]) for x in r})
    assert min(solids) == 15.0                # DOMAIN GUARD: >= 15 wt% (above espresso TDS)
    # physical consistency: nu DECREASES with T at fixed solids; INCREASES with solids at fixed T
    for f in solids:
        by_T = sorted(((float(x["temperature_C"]), float(x["kinematic_viscosity_mm2_s"]))
                       for x in r if float(x["dry_solids_percent_w_w"]) == f))
        vals = [v for _, v in by_T]
        assert all(a > b for a, b in zip(vals, vals[1:]))   # monotone down in T
    for T in sorted({float(x["temperature_C"]) for x in r}):
        by_f = sorted(((float(x["dry_solids_percent_w_w"]), float(x["kinematic_viscosity_mm2_s"]))
                       for x in r if float(x["temperature_C"]) == T))
        vals = [v for _, v in by_f]
        assert all(a < b for a, b in zip(vals, vals[1:]))   # monotone up in solids


def test_hargarten2020_loaders():
    prog = pwdata.hargarten_swelling_progress()
    assert len(prog) == 8                          # 2 roasts x 2 temps x 2 times
    assert {r["roast"] for r in prog} == {"medium", "light"}
    # 30 s < 4 min progress for every series (swelling monotone toward steady state)
    by_key = {}
    for r in prog:
        by_key.setdefault((r["roast"], r["T_C"]), {})[int(r["time_s"])] = float(r["progress_pct"])
    for series in by_key.values():
        assert series[30] < series[240]
    anchors = pwdata.hargarten_scalar_anchors()
    dd = [float(a["value"]) for a in anchors if a["quantity"] == "swelling_dd_rel"]
    assert dd and all(12 <= v <= 16 for v in dd)   # ~15% swelling anchor


def test_telisromero2001_measured_tables():
    t1 = pwdata.telisromero_table1_eta()
    t2 = pwdata.telisromero_table2_Kn()
    assert len(t1) == 24 and len(t2) == 27
    # bilinear interpolator reproduces a measured Table-1 node exactly
    assert abs(pwdata.telisromero_eta_measured(295.0, 76.0) - 2.81e-3) < 1e-9


def test_ellero2019_digitized_figures():
    # FIGURE-DIGITIZED SPH simulation (qualitative); NOT raw coffee data.
    assert len(pwdata.ellero_fig2_forcing()) == 10
    assert len(pwdata.ellero_fig2_ref8_markers()) == 38          # experimental overlay markers
    re2 = pwdata.ellero_fig2_reynolds()
    assert set(re2) >= {"theta=0.000", "theta=0.005", "theta=0.006"}
    assert max(re2["theta=0.005"]["y"]) > 8.0                    # inverse discharge starts high
    # fig3 direct discharge: fines migration drives an order-of-magnitude flow
    # decay (Re ~10 -> ~1) and DEEPENS monotonically with theta (fines fraction)
    re3 = pwdata.ellero_fig3_reynolds()
    y58 = re3["theta=0.0058"]["y"]
    assert max(y58) > 8.0 and min(y58) < 2.0
    mins = [min(re3[k]["y"]) for k in ("theta=0.0020", "theta=0.0050", "theta=0.0056", "theta=0.0058")]
    assert all(a > b for a, b in zip(mins, mins[1:]))            # deeper decay as theta rises
    # card's central claim: release rate Dr dominates -> final content rises with Dr
    dr = pwdata.ellero_fig4_caffeine_Dr()
    finals = {k: v["y"][-1] for k, v in dr.items()}
    assert finals["Dr=0.0200"] > finals["Dr=0.0050"] > finals["Dr=0.0010"]


def test_schmieder_cup_masses_malformed_rows_are_explicit_design_summaries():
    """review B5-07: the Schmieder-derived cup-mass CSV carries 36 rows that lack the
    primary predictors/outcome (grind, cup mass, concentration). They must NOT vanish
    silently through downstream filtering — they are exp-15 'DoE Corner Point'
    design-summary rows, and this test pins that contract so a filtering/imputation
    change cannot let malformed records enter an analysis unnoticed."""
    import csv
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "puckworks/data/schmieder2023/cup_masses.csv"
    rows = list(csv.DictReader(open(p)))
    def complete(r):
        return (r.get("grind_level", "").strip() and r.get("mass_in_cup", "").strip()
                and r.get("conc_in_cup", "").strip())
    valid = [r for r in rows if complete(r)]
    bad = [r for r in rows if not complete(r)]
    assert len(valid) == 576, f"expected 576 complete run rows, got {len(valid)}"
    assert len(bad) == 36, f"expected 36 malformed/design-summary rows, got {len(bad)}"
    # every malformed row is an explicitly-tagged exp-15 corner-point design summary
    assert {r["exp"] for r in bad} == {"15.0"}
    assert {r["doe_role"] for r in bad} == {"DoE Corner Point"}
    # the valid rows are the coherent 4 components x 3 brew ratios x 48 runs
    assert len({r["component"] for r in valid}) == 4
    assert len({r["brew_ratio"] for r in valid}) == 3


def test_pocketscience2024_intake():
    """pocketscience2024 data-only intake: 12-condition edge/center EY summary + LRR
    scalars load, carry the card's SIGN structure, and are declared in the MANIFEST.
    (No gate against the source; this guards the transcription + manifest contract.)"""
    import csv
    import os

    edge = pwdata.pocketscience_edge_ey()
    assert len(edge) == 12
    need = {"basket", "shot_style", "grinder", "puck_screen", "dispersion_block",
            "ey_center_pct", "ey_edge_pct", "edge_yield_loss_pct", "outer_mass_frac_of_dose"}
    assert need <= set(edge[0].keys())

    def _cell(basket, shot, screen, block):
        m = [r for r in edge if r["basket"] == basket and r["shot_style"] == shot
             and r["puck_screen"] == screen and r["dispersion_block"] == block]
        assert len(m) == 1, (basket, shot, screen, block)
        return m[0]

    # card gate-design point: the worst edge loss is the traditional basket + traditional
    # shot + NO screen; a modern basket + screen + turbo shot is near zero.
    worst = _cell("VST18", "traditional", "N", "teflon")
    best = _cell("Sworks", "turbo", "Y", "teflon")
    assert float(worst["edge_yield_loss_pct"]) < -25.0        # strong under-extraction
    assert abs(float(best["edge_yield_loss_pct"])) < 3.0       # near even
    # label-erratum: outer fraction is outer-to-TOTAL (0.31 VST18, 0.34 Sworks)
    assert abs(float(worst["outer_mass_frac_of_dose"]) - 0.31) < 1e-9
    assert abs(float(best["outer_mass_frac_of_dose"]) - 0.34) < 1e-9

    lrr = pwdata.pocketscience_lrr()
    assert len(lrr) == 2
    assert all(3.0 < float(r["lrr_g_per_g"]) < 3.6 for r in lrr)

    # both datasets declared in the manifest (rule 5)
    mp = os.path.join(os.path.dirname(__file__), "..", "puckworks", "data", "MANIFEST.csv")
    with open(mp, newline="", encoding="utf-8") as fh:
        ids = {row["dataset_id"] for row in csv.DictReader(fh)}
    assert "pocketscience2024/edge_ey_condition_means" in ids
    assert "pocketscience2024/lrr_scalars" in ids


def test_mckeonaloe2022_basket_intake():
    """mckeonaloe2022 basket open-area + hole geometry (data-only, G9 seed): 4 rows
    (2 baskets x 2 faces) load, carry the card's structure, and are in the MANIFEST.
    Single-specimen hobbyist imaging -- guards the transcription + manifest contract."""
    import csv
    import os

    rows = pwdata.mckeonaloe_baskets()
    assert len(rows) == 4
    need = {"basket", "face", "open_area_pct", "mean_hole_diam_um", "std_hole_diam_um"}
    assert need <= set(rows[0].keys())

    by = {(r["basket"], r["face"]): r for r in rows}
    # VST has a markedly smaller open area than the Wafo Classic on both faces.
    assert by[("VST", "exit")]["open_area_pct"] < by[("Wafo_Classic", "exit")]["open_area_pct"]
    assert by[("VST", "coffee")]["open_area_pct"] < by[("Wafo_Classic", "coffee")]["open_area_pct"]
    # both baskets taper wider on the coffee face (exit face is flow-limiting):
    for b in ("Wafo_Classic", "VST"):
        assert by[(b, "coffee")]["mean_hole_diam_um"] >= by[(b, "exit")]["mean_hole_diam_um"]

    mp = os.path.join(os.path.dirname(__file__), "..", "puckworks", "data", "MANIFEST.csv")
    with open(mp, newline="", encoding="utf-8") as fh:
        ids = {row["dataset_id"] for row in csv.DictReader(fh)}
    assert "mckeonaloe2022/basket_open_area_geometry" in ids


def _manifest_ids():
    import csv
    import os
    mp = os.path.join(os.path.dirname(__file__), "..", "puckworks", "data", "MANIFEST.csv")
    with open(mp, newline="", encoding="utf-8") as fh:
        return {row["dataset_id"] for row in csv.DictReader(fh)}


def test_moroney2019_table2_intake():
    """moroney2019 Table 2 (data-only) + cooper2021 author-confirmed errata: 6 configs
    load, and the corrected columns satisfy h_sl_corrected = h_sl_reported/965.3 and
    D_v = h_sl_corrected * d_s (the ~10^3 fix), declared in the MANIFEST."""
    rows = pwdata.moroney2019_table2()
    assert len(rows) == 6
    need = {"config", "grind", "model", "d_s_m", "alpha_s", "c_s0_kgm3",
            "h_sl_reported_ms", "h_sl_corrected_ms", "D_v_m2s"}
    assert need <= set(rows[0].keys())
    for r in rows:
        # Erratum B: corrected = reported / rho_l(90C) = reported / 965.3
        assert abs(r["h_sl_corrected_ms"] - r["h_sl_reported_ms"] / 965.3) \
            < 0.02 * r["h_sl_corrected_ms"]
        # Erratum A: species-split diffusivity D_v = h_sl_corrected * d_s
        assert abs(r["D_v_m2s"] - r["h_sl_corrected_ms"] * r["d_s_m"]) < 0.02 * r["D_v_m2s"]
    cs0 = {r["grind"]: r["c_s0_kgm3"] for r in rows}
    assert cs0["fine"] == 358.587 and cs0["coarse"] == 305.0
    assert "moroney2019/table2" in _manifest_ids()


def test_ribes2020_radial_ey_intake():
    """ribes2020 (data-only): 3 conditions x 3 zones; the baseline outer ring under-
    extracts vs center, and a V60 paper filter BELOW the puck largely removes the
    outer deficit. Slide-grade; guards the transcription + MANIFEST contract."""
    rows = pwdata.ribes2020_radial_ey()
    assert len(rows) == 9
    need = {"condition", "tamper_base", "bottom_paper_filter", "zone",
            "r_inner_mm", "r_outer_mm", "zone_ey_pct", "shot_ey_pct"}
    assert need <= set(rows[0].keys())

    def _ey(cond, zone):
        m = [r for r in rows if r["condition"] == cond and r["zone"] == zone]
        assert len(m) == 1, (cond, zone)
        return float(m[0]["zone_ey_pct"])

    assert _ey("baseline", "outer") < _ey("baseline", "center")            # outer deficit
    assert _ey("bottom_filter", "outer") > _ey("baseline", "outer") + 5    # paper flattens
    assert _ey("convex_tamper", "outer") < _ey("baseline", "outer")        # convex worsens
    assert "ribes2020/radial_ey" in _manifest_ids()


def test_ribes2021_radial_ey_intake():
    """ribes2021 (data-only): 4 conditions x 3 zones; the outer ring under-extracts
    without a contact screen above the puck, and a screen flattens it, on both VST and
    Pullman baskets. Slide-grade; guards transcription + MANIFEST."""
    rows = pwdata.ribes2021_radial_ey()
    assert len(rows) == 12
    for basket in ("vst_20g", "pullman_20g"):
        def _ey(scr, zone):
            m = [r for r in rows if r["basket"] == basket
                 and r["contact_screen"] == scr and r["zone"] == zone]
            assert len(m) == 1, (basket, scr, zone)
            return float(m[0]["zone_ey_pct"])
        assert _ey("no", "outer") < _ey("no", "center")               # outer deficit
        assert _ey("yes", "outer") > _ey("no", "outer")               # screen flattens
    assert "ribes2021/radial_ey" in _manifest_ids()


def test_romancorrochano2015_table2_intake():
    """romancorrochano2015 Table 2 (data-only): tamped-bed permeability K (m^2) with SD
    and Tukey groups, 4 grinds x 3 bulk densities; K falls as the bed is packed denser
    within a grind. Declared in the MANIFEST."""
    rows = pwdata.romancorrochano2015_table2()
    assert len(rows) == 12
    need = {"grind", "bulk_density_kgm3", "permeability_m2", "permeability_sd_m2", "tukey_group"}
    assert need <= set(rows[0].keys())
    for grind in ("A", "B", "C", "D"):
        by_rho = {r["bulk_density_kgm3"]: r for r in rows if r["grind"] == grind}
        assert set(by_rho) == {360.0, 400.0, 480.0}
        # the most-consolidated (480 kg/m^3) bed has the lowest K within each grind
        # (the 360->400 trend is non-monotonic for the coarsest grind D — kept as-is)
        assert by_rho[480.0]["permeability_m2"] == min(r["permeability_m2"] for r in by_rho.values())
        assert all(r["permeability_sd_m2"] > 0 for r in by_rho.values())   # SD retained
    assert "romancorrochano2015/table2" in _manifest_ids()


def test_gagne2021_grinder_arm_intake():
    """gagne2021 (data-only): grinder-arm EY/retention/temperature/resistance contrasts;
    the low-fines EG-1+SSP arm reads a higher EY than the Niche arm (raw and VST-filtered).
    The 11 .shot traces are a separate acquisition target. Declared in the MANIFEST."""
    rows = pwdata.gagne2021_grinder_arm_summary()
    assert len(rows) == 14
    need = {"quantity", "grinder_arm", "value", "uncertainty", "units", "n", "read_method"}
    assert need <= set(rows[0].keys())

    def _val(quantity, arm):
        m = [r for r in rows if r["quantity"] == quantity and r["grinder_arm"] == arm]
        assert len(m) == 1, (quantity, arm)
        return float(m[0]["value"])

    assert _val("raw_ey", "eg1_ssp_ulf") > _val("raw_ey", "niche")
    assert _val("vst_filtered_ey", "eg1_ssp_ulf") > _val("vst_filtered_ey", "niche")
    assert {r["read_method"] for r in rows} <= {"measured", "figure"}
    assert "gagne2021/grinder_arm_summary" in _manifest_ids()


def test_gagne2021_shots_intake():
    """gagne2021 raw DE1 .shot traces: all 11 shots parse into aligned espresso_*
    channels with monotone elapsed time and plausible pressure, declared in the
    MANIFEST. (Raw machine-logged hydraulics; no gate against the source.)"""
    shots = pwdata.gagne2021_shots()
    assert len(shots) == 11
    for sid, ch in shots.items():
        n = len(ch["espresso_elapsed"])
        assert n > 100, sid                                       # a real shot
        assert all(len(ch[c]) == n for c in ch), sid             # all channels aligned
        el = ch["espresso_elapsed"]
        assert (el[1:] >= el[:-1] - 1e-9).all(), sid             # elapsed non-decreasing
        assert 0.0 <= float(ch["espresso_pressure"].max()) < 15.0, sid   # bar, plausible
    assert "gagne2021/shots" in _manifest_ids()


def test_khamitova2020_tamping_intake():
    """khamitova2020 tamping-resolved chemistry (data-only): four compound tables +
    the ground-coffee assay load, carry the 10/15/20/30 kgF tamping columns with RSD,
    and rank caffeine > nicotinic acid; declared in the MANIFEST."""
    tab = pwdata.khamitova2020_tamping()
    assert set(tab) == {"total_cqa", "caffeine", "trigonelline", "nicotinic_acid", "ground_coffee"}
    cqa = tab["total_cqa"]
    assert len(cqa) == 9                                          # pressure x temperature grid
    for tf in ("10", "15", "20", "30"):
        assert f"{tf}kgF_mg_per_ml" in cqa[0] and f"{tf}kgF_RSD_pct" in cqa[0]
    # caffeine is the most concentrated compound, nicotinic acid the least (per condition)
    caf = tab["caffeine"][0]["20kgF_mg_per_ml"]
    nic = tab["nicotinic_acid"][0]["20kgF_mg_per_ml"]
    assert caf > nic
    assert "khamitova2020/tamping" in _manifest_ids()


def test_smrke2024_figures_intake():
    """smrke2024 digitized figures (data-only): the figure set loads; the core Fig 3
    EY-vs-time (46 pts across added-fines levels) and the Supp Fig S1 per-shot flow
    profiles carry their expected columns; declared in the MANIFEST."""
    figs = pwdata.smrke2024_figures()
    assert "fig3_ey_vs_time" in figs and "figS1_flow_profiles" in figs
    fig3 = figs["fig3_ey_vs_time"]
    assert len(fig3) == 46
    assert {"extraction_time_s", "extraction_pct", "series"} <= set(fig3[0].keys())
    s1 = figs["figS1_flow_profiles"]
    assert len(s1) > 1000
    assert {"time_s", "flow_rate_g_per_s"} <= set(s1[0].keys())
    assert "smrke2024/figures" in _manifest_ids()


def test_sobolik2002_rheology_intake():
    """sobolik2002 (calibration-provider): the viscosity/conductivity artifact set
    loads; Table 1 has 11 concentration rows, the Eq. (4) viscosity line is positive,
    and the digitized figures carry an evidence_strength column; MANIFEST-declared."""
    art = pwdata.sobolik2002_rheology()
    assert len(art) == 12
    assert len(art["table1_kappa_coeffs"]) == 11                 # 11 mass fractions
    eq4 = art["viscosity_concentrated_eq4"]
    assert "mu_Pa_s" in eq4[0]
    assert all(float(r["mu_Pa_s"]) > 0 for r in eq4[:20])
    assert "evidence_strength" in art["viscosity_concentrated_fig2"][0]   # digitized -> labelled
    assert "sobolik2002/rheology" in _manifest_ids()


def test_moroney2015_data_intake():
    """moroney2015 primary Philips dataset (data-only): the parameter tables +
    digitized figures load (each past its `#` provenance header); Table 1 carries the
    measured c_sat=212.4, kappa=3.1 and Table 2 the Delta_p/L permeability anchors;
    the provenance manifest labels every file. MANIFEST-declared."""
    art = pwdata.moroney2015_data()
    assert {"table1_batch_params", "table2_cylindrical_params", "provenance_manifest"} <= set(art)
    t1 = {r["parameter"]: r for r in art["table1_batch_params"]}
    assert t1["c_sat"]["JK_drip_filter"] == 212.4 and t1["c_sat"]["Cimbali_20"] == 212.4
    assert t1["kappa"]["JK_drip_filter"] == 3.1                      # measured Kozeny-Carman factor
    assert t1["c_s"]["JK_drip_filter"] == 1400.0
    t2 = {r["parameter"]: r for r in art["table2_cylindrical_params"]}
    assert t2["Delta_p"]["JK_drip_filter"] == 230000.0 and t2["Delta_p"]["Cimbali_20"] == 65000.0
    assert t2["L"]["JK_drip_filter"] == 0.0405                       # bed height (permeability anchor)
    prov = art["provenance_manifest"]
    assert len(prov) == 12 and {r["evidence_strength"] for r in prov} <= {"MEASURED", "ESTIMATED"}
    assert "moroney2015/data" in _manifest_ids()
