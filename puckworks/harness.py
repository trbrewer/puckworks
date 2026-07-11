"""harness.py — P1 extraction comparison harness (ROADMAP item 2.1 / Sprint 8).

NOT a physics model: an orchestration + reporting layer that runs the registered
extraction components on matched inputs against the shared gate datasets, reports
per-dataset residuals WITH validation-strength tags, and surfaces the P1
normalization hazards (c_sat, soluble-inventory reference, dissolution law, flow
input) as explicit config fields that must NEVER be silently merged (CLAUDE.md
rule 6; ROADMAP §5.4 c_sat, §P1 hazards table, ledger A5).

The interpretive workup (which model wins, P3 hypothesis file 2.3) is the CHAT
half of the sprint; this module provides the numbers.
"""
import numpy as np

# --- P1 normalization hazards (surfaced, never silently merged) ----------
# Each extraction lineage carries its own soluble-inventory reference and
# saturation concentration. These are CONFIG, reported per-model in any harness
# output; merging them would be the mega-model failure mode (rule 6, §5.4).
P1_HAZARDS = {
    "cameron2020": dict(c_sat_kg_m3=212.4, inventory="per-bed-volume (c_s0=118/phi_s)",
                        dissolution="nonlinear surface", flow="pressure/flux table"),
    "grudeva_thesis": dict(c_sat_kg_m3=170.0, inventory="per-grain (incl. internal pores)",
                           dissolution="linear capped transfer", flow="fixed q / P-derived"),
    "grudeva_paper": dict(c_sat_kg_m3=224.0, inventory="per-grain (incl. internal pores)",
                          dissolution="linear capped transfer", flow="fixed q / P-derived"),
    "moroney2016": dict(c_sat_kg_m3=212.4, inventory="per-bed-volume",
                        dissolution="two-timescale asymptotic", flow="constant dP"),
    "egidi2024": dict(c_sat_kg_m3=212.4, inventory="c0=200 kg/m3 per grain",
                      dissolution="quadratic-in-surface", flow="prescribed constant q"),
    "pannusch2024": dict(c_sat_kg_m3=None, inventory="per-solute c_s0",
                         dissolution="Sherwood-correlated linear", flow="measured Q(t)+T(t)"),
}


def csat_values():
    """The distinct c_sat config values in play (§5.4). Returns the sorted set of
    non-null values — the harness reports these side by side, never merged."""
    return sorted({h["c_sat_kg_m3"] for h in P1_HAZARDS.values()
                   if h["c_sat_kg_m3"] is not None})


# --- extraction-vs-dataset comparison (with validation-strength tags) ----
def extraction_comparison():
    """Run the gated extraction models against their validation datasets and
    return per-model residuals tagged by validation strength (ROADMAP §0)."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.models.grudeva2025 import reduced as gr
    from puckworks.models.liang2021 import desorption as lg
    from puckworks import data as d
    out = {}

    # pannusch -> Schmieder multi-solute kinetics (post-fit reconstruction)
    m = ps.mape_all()
    out["pannusch2024/schmieder_kinetics"] = dict(
        metric="MAPE_%", value={k: round(v, 2) for k, v in m.items()},
        strength="post-fit reconstruction")

    # grudeva -> C1 vial masses (post-fit reconstruction)
    r = gr.make_coffee(N=120, Nt=600)
    stats = d.grudeva_vial_stats()
    exp_total = sum(s["solubles_mean_g"] for s in stats[3:])
    out["grudeva2025/vial_masses"] = dict(
        metric="total_solubles_g", value=round(r["total_solubles_g"], 2),
        reference_g=round(exp_total, 2), strength="post-fit reconstruction")

    # liang -> equilibrium ceiling vs cameron inventory ceiling (§5.5)
    out["liang2021/ceiling_vs_cameron"] = dict(
        metric="EY_ceiling", liang=lg.K_EMAX_1L,
        cameron=round(lg.cameron_inventory_ceiling(), 3),
        strength="independent (distinct quantities, K<1)")
    return out


# --- §5.6 dissolution-speed discriminator --------------------------------
def dissolution_speed_test():
    """§5.6: near-instant dissolution (Waszkiewicz, TDS timescale set by flow)
    vs diffusion-limited boulders (Cameron). Discriminator on the Waszkiewicz
    5-s TDS fractions: instant dissolution => solubles present from t=0 => TDS is
    HIGH in the first fraction (early/peak ~ 1); a diffusion-limited population
    would release slowly => low-then-rising TDS (early/peak << 1)."""
    from puckworks import data as d
    f = d.waszkiewicz_tds_fractions()
    tds = f["tds_pct"]
    early = float(tds[0]); peak = float(np.nanmax(tds))
    ratio = early / peak
    # boulder-diffusion timescale (grudeva boulders a=2.29e-4 m, D_s=2.3e-10)
    tau_diff = (2.29e-4) ** 2 / (np.pi ** 2 * 2.3e-10)
    return dict(early_to_peak=round(ratio, 3), early_tds_pct=round(early, 2),
                peak_tds_pct=round(peak, 2), tau_boulder_diffusion_s=round(tau_diff, 1),
                favors="near-instant dissolution" if ratio > 0.8 else "diffusion-limited")
