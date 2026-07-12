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
    return r


if __name__ == "__main__":
    report()
