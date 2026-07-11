# Model card: Wadsworth 2026 grinder transfer function

**Paper:** Wadsworth et al., R. Soc. Open Sci. 13, 252031 (2026). DOI 10.1098/rsos.252031 (§3.2, §4.1, figs. 2–3, table 1)
**Stage(s):** grind · **Kind:** calibration (informs GrindState priors; no runtime coupling)
**Status:** card-only

## Scope and mechanism
Empirical map from grinder dial setting G to the mean grain radius ⟨R⟩ (linear, argued
from burr-gap physics) plus the observed relation between G and polydispersivity S.
Measured by Camsizer X2 dynamic image analysis (dry dispersion) on 22 samples: two
coffees (Tumba/Rwanda, Guayacán/Colombia) × 11 Mahlkönig settings. Both relations are
observed to be variety/roast-independent for these coffees, supporting a
grinder-dominated transfer function. Optionally chains to a porosity prior via a prior
glass-bead tamping fit (flagged below as not coffee-validated).

## Governing equations
1. Grind map (their §4.1, fig. 3a): ⟨R⟩ = βG + R₀
   G grinder setting [—]; ⟨R⟩ mean radius of the area-equivalent-circle distribution [m];
   R₀ the extrapolated radius at G = 0 [m].
2. Polydispersivity definition (their §2.3): S = ⟨R⟩⟨R²⟩/⟨R³⟩, S = 1 monodisperse,
   S → 0 highly polydisperse. S(G) rises from ~0.46–0.55 at G = 1 to ~0.77–0.78 at
   G = 11 (fig. 3b, table 1); no functional fit is provided — use table 1 directly.
3. Optional porosity prior (their §2.5, imported from their ref. [8], glass beads
   tamped at 3 N — NOT refit to coffee): φ = γ₃(1 − S)^γ₄.
No simplifications made; note the paper also proposes ⟨R³⟩/⟨R²⟩ as an alternative
characteristic size (moments are in table 1), which we do not adopt by default.

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| β | (5.8050 ± 0.1004) × 10⁻⁵ | m per setting | fitted (22 samples, both coffees) |
| R₀ | (1.3797 ± 0.0678) × 10⁻⁴ | m | fitted (same) |
| γ₃ | 0.375 | — | fitted (glass beads, prior work; assumed for coffee) |
| γ₄ | −0.116 | — | fitted (glass beads, prior work; assumed for coffee) |
| S(G) | table 1 values | — | measured (per sample) |

> **Correction (2026-07-11):** β and R₀ above were previously printed as
> 4.3505×10⁻⁵ / 1.0160×10⁻⁴ — a transcription typo. An OLS refit of Table 1 ⟨R⟩
> vs G (all 22 samples) gives β = 5.8050×10⁻⁵ m/setting, R₀ = 1.3797×10⁻⁴ m
> (R² = 0.994); the old values gave a slope ~1.33× too shallow to span the
> measured 192–818 µm range. Moment columns are self-consistent
> (S = ⟨R⟩⟨R²⟩/⟨R³⟩ reproduces the reported S). See
> `puckworks/data/wadsworth2026/PROVENANCE.md`.

## Calibration and validation offered by the source
Linear fit quality is shown graphically (fig. 3a) with tight parameter uncertainties;
no R² reported. Variety-independence is an observation across exactly two coffees of
similar roast, not a tested claim. The φ(S) step is validated only on glass beads in
the source it comes from; this paper explicitly does not dwell on it and did not
control packing. Distribution-shape finding: bimodal (fines peak 1–10 µm) at G 1–3,
monomodal at G 4–11 — relevant as data, not modeled.

## Assumptions and validity range
- Grinder-specific: Mahlkönig, this burr set and calibration; the authors state the
  map depends on "calibration, burr set and manufacturer". Do not port dial values to
  the EK43 dial range in Cameron 2020 without re-fitting.
- Valid over G 1–11, ⟨R⟩ ≈ 192–818 µm (measured); extrapolation below G = 1
  (espresso-finest territory) is unsupported, and R₀ is an extrapolation artifact,
  not a physical floor.
- Fresh grounds; silent on staling/moisture effects on grind output (their §6 flags
  these as open).
- φ(S) chain is a double extrapolation for tamped coffee (material + tamp force).

## Interface mapping
Inputs consumed: grind.setting. Outputs produced: GrindState.mean_radius_m prior;
S → BedState.porosity prior via eq. 3 (weak, flagged); PSD moments available for
GrindState.fines_fraction / boulder_radius_m estimation from the published PSDs.
Coupling: offline calibration provider only. Adapter: dial-space conversion required
per grinder before comparison with cameron2020 (EK43 dial 1.1–2.3).

## Extractable data
High value: the published open-access zip contains all 22 full grain-size
distributions (R, R_min, R_max) — directly serves the backlog item "grind: PSD models
beyond bimodal; grinder transfer functions" and gives real fines-fraction inputs for
brewer2026.pack_generator. Table 1 moments (⟨R⟩, ⟨R²⟩, ⟨R³⟩, S) are already in
data/wadsworth2026_table1.csv. Minor erratum to record on transcription: the §6
swelling example states 8.1 × 10¹⁷ m², clearly a typo for 8.1 × 10⁻¹⁷ m².

## Overlaps and conflicts
- Complements wadsworth2026.permeability: closes the chain G → ⟨R⟩ → s_p → k
  (their eq. 5.3) so the registered component can be driven from a dial setting.
- Complements cameron2020 grind stage (microstructure tables keyed to EK43 dial):
  competing grinder-specific maps; neither supersedes the other — they motivate a
  grinder-transfer-function abstraction in the grind stage.
- Feeds brewer2026.pack_generator with measured PSDs instead of synthetic bimodal
  assumptions; the bimodal→monomodal transition at G 3–4 is a real-data constraint on
  the fines sub-voxel treatment.

## Implementation estimate
Trivial code (one linear map + table lookup); the work is data transcription of the
PSD zip and a dial-space adapter design. Gate: reproduce β, R₀ from table 1 ⟨R⟩ values;
check S(G) monotonicity against table 1.

VERDICT: calibration-provider — a grinder-specific two-parameter map whose real value is the 22 published PSDs feeding GrindState and pack_generator priors — effort S
