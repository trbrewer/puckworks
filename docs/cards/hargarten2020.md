# Model card: Hargarten 2020 coffee-particle swelling & erosion

**Paper/thesis:** Hargarten, V.B.; Kuhn, M.; Briesen, H. "Swelling properties of roasted
coffee particles." J. Sci. Food Agric. 100(11), 2020. DOI 10.1002/jsfa.10440 (open access,
CC BY-NC). Reprinted as Article 1 (§4.1, Appendix B.1) of Pannusch (V.B.), PhD dissertation,
TU Munich, 2024. Note: first author V.B. Hargarten is the same person as V.B. Pannusch
(Article 3 → `pannusch2024.md`); cite as Hargarten 2020 per the published name.
**Stage(s):** bed_dynamics (swelling/erosion during wetting); grind (dry→wet PSD shift) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
An empirical characterization — **not a predictive model** — of how roasted coffee particles
change size when wetted, and of the fines released during wetting. Two mechanisms are
disentangled: (1) **swelling**, an isotropic ~15 % diameter increase of coarse particles from
capillary water uptake and hydration/expansion of insoluble cell-wall polysaccharides
(holocellulose); and (2) **particle erosion**, the detachment of surface-adhering fines
(<40 µm) into the water, which inflates the measured fine fraction and, unless controlled for,
corrupts a d4,3-based swelling estimate. Bulk particle-size distributions (PSD, laser
diffraction, dry vs. wet) and single-particle microscopy (time-resolved, flow cell) are used
across grinding degrees, two roasts (medium/light), and two temperatures (25/80–90 °C). The
registry value is data + three qualitative constraints on the constant-porosity assumption:
swelling saturates the intragranular pores before extraction, occurs on the shot timescale,
and (with erosion) tends to **reduce** permeability during extraction.

## Governing equations
The paper proposes no constitutive/predictive equation. The four numbered relations are
**measurement definitions** for the reported quantities; transcribe them only as the
definitions behind the extractable data, not as an implementable swelling law.

Eq. 1 (relative diameter increase): Δd_rel = (d_f − d_0)/d_0 · 100 %.
Applied per volume-distribution quantile d_10,3, d_16,3, d_50,3, d_84,3, d_90,3, d_99,3.

Eq. 2 (projection-area-equivalent diameter, microscopy): d_proj = √(4 A_proj / π).

Eq. 3 (aspect ratio, shape descriptor): AR = d_F,min / d_F,max (min/max Feret diameters).

Eq. 4 (progress of swelling, time-resolved): Progress(t) = (d(t) − d_0)/(d_f − d_0) · 100 %,
with d_f = d_proj at 20 min after wetting onset.

Symbols: d_0 dry (initial) diameter, d_f final (swollen, steady-state) diameter, d(t) diameter
at time t, d_{q,3} the q-percent quantile of the volume (index 3) distribution, d4,3 De
Brouckere volume-moment mean, A_proj particle projection area, d_F,min/d_F,max minimum/maximum
Feret diameters.

## Parameters
All values **measured** (the study reports no fitted or nominal parameters). These are the
empirical anchors a future swelling/erosion closure would be calibrated against.

| symbol | value | units | source |
| --- | --- | --- | --- |
| Δd_rel (medium roast, outliers excluded) | 15 ± 4 | % | measured (laser diffraction) |
| Δd_rel (medium roast, full dataset) | 15 ± 7 | % | measured |
| Δd_rel (light roast, outliers excluded) | 15 ± 3 | % | measured |
| Δd_rel (light roast, full dataset) | 13 ± 10 | % | measured |
| Δd_rel vs. initial diameter (slope, medium) | −2.95×10⁻³ (p = 0.291, n.s.) | % µm⁻¹ | measured (regression + ANOVA) |
| Δd_rel vs. initial diameter (slope, light) | −2.54×10⁻³ (p = 0.498, n.s.) | % µm⁻¹ | measured |
| Progress after 30 s (medium, 80/25 °C) | 83 / 82 | % | measured (Table 2) |
| Progress after 30 s (light, 80/25 °C) | 71 / 59 | % | measured (Table 2) |
| Progress after 4 min (medium, 80/25 °C) | 109 / 111 | % | measured (Table 2)¹ |
| Progress after 4 min (light, 80/25 °C) | 101 / 108 | % | measured (Table 2)¹ |
| dry PSD modes (non-sieved, medium) | ~20–30 (fine), ~400 (coarse) | µm | measured |
| wet PSD modes (non-sieved, medium, 90 °C) | 12 (fine), 330 (coarse) | µm | measured² |
| aspect ratio (measured particles) | 0.6–0.8, unchanged by swelling | 1 | measured |
| grinding degrees (Mahlkönig EK43) | 2.0 fine / 5.0 medium / 8.0 coarse | dial (1–11) | measured |

¹ Values >100 % arise because Eq. 4 normalizes to the 20-min diameter, which carries
experimental error; read as "steady state effectively reached by 4 min," not literal overshoot.
² The wet fine mode shift to 12 µm and coarse mode to 330 µm mixes true swelling with
erosion-driven repopulation of the fine bins; the authors treat the sieved-fraction Δd_rel
(15 %) as the erosion-corrected swelling value.

## Calibration and validation offered by the source
This is a measurement study, so "validation" = internal statistical support and reconciliation
with prior literature, not model-vs-data error. **Erosion** (fine fraction increases dry→wet;
coarse fraction decreases) is confirmed by two-sample t-test and Mann–Whitney U-test at the
1 % level (Table A1), and shown to **strengthen with temperature** (25→90 °C, Table A1).
**Swelling magnitude** (~15 %) is established by laser diffraction on sieved fractions (erosion
excluded by pre-sieving/air-jet/washing) and reconciles the wide prior spread (7 %–23 %) by
attributing the discrepancies to uncontrolled erosion and moisture/dispersant differences.
**Independence from initial size and roasting degree** is supported by non-significant
regression slopes (Table A2) and non-significant roast comparisons (Table A3). **Isotropy** is
supported by an unchanged aspect ratio during swelling (Table A4, mostly n.s.).

Stated weakly by the authors themselves: single-particle **microscopy could not verify the PSD
swelling magnitude** — per-particle final swelling scattered too widely (attributed to
individual pore/fibre structure, composition, gas-bubble artefacts), so image analysis is
called "an inappropriate method for the quantification of total swelling." Time-dependency
conclusions therefore rest on the qualitative envelope of noisy single-particle curves, not a
fitted rate. Only two coffees (one medium, one 100 % arabica light) and one water quality
(demineralized) were tested; **no pressure** was applied (the flow cell is near-ambient),
which the authors flag as a gap for espresso specifically.

## Assumptions and validity range
- **Ambient/low pressure only.** The effect of the ~9 bar espresso pressure on swelling
  dynamics is explicitly **not covered** and flagged for future work — the single most
  important silence for puckworks.
- **Two roasts, demineralized water.** Water alkalinity/mineral content (known to affect
  swelling and percolation time, Rivetti et al.) is deliberately excluded; robusta and darker
  roasts untested.
- **Steady-state swelling defined at 20 min**; sub-30-s kinetics are coarse (first microscopy
  frame at 10 s) and the "60–80 %/30 s, complete/4 min" statement is a population-level
  envelope, not a rate constant.
- **Silent on the swelling→permeability quantitative link.** The paper argues swelling +
  erosion both *decrease* permeability and that swelling may *offset* the porosity rise from
  dissolution (supporting a constant-porosity idealization), but gives **no** k(swelling) or
  porosity(t) relation — direction only, no magnitude.
- **Erosion mass not quantified.** Fines release is shown as a PSD-bin shift and temperature
  trend, not as an eroded-mass fraction or a migration/deposition model.
- Microscopy restricted to 400–1000 µm coarse particles (fines unmeasurable individually), so
  the *fine*-fraction time behaviour is inferred, not directly measured.

## Interface mapping
Inputs consumed: none at runtime (offline empirical study). Conceptually keyed to GrindState
(PSD, fines_fraction) and roast/temperature.
Outputs produced: no contract fields directly. Informs, as **calibration priors**:
BedState.porosity / k_m2 / kappa (swelling and erosion both push permeability down during the
shot; swelling offsets dissolution-driven porosity gain) and GrindState (the dry→wet PSD map,
i.e. ~15 % coarse growth + fines repopulation).

Couplings: **offline calibration provider only** — no runtime solver here. It supplies the
empirical targets a bed_dynamics swelling/erosion closure (see backlog) must reproduce, and a
concrete justification for the preinfusion/constant-porosity idealizations used by the
saturated extraction cards. Any runtime use requires pairing with an actual model (Mo 2022
swelling, Mo 2021 / Ellero–Navarini erosion) that this data would calibrate.

## Extractable data
Open-access article (CC BY-NC); **no raw-data repository is stated**, so numeric series must be
digitized from the figures/tables (values themselves are printed for the scalar summaries).
- **Table 2** → data/hargarten2020_progress.csv: progress of swelling at 30 s and 4 min for
  medium/light roast × 80/25 °C (8 values). Directly transcribable.
- **Table 1**: sieve-fraction definitions F/S/M/L and laser-diffraction lens measuring ranges
  per grinding degree (2.0/5.0/8.0 on EK43) — needed to interpret the sieved-fraction PSDs.
- **Figures 2, 3, 5**: dry vs. wet volume PSDs (non-sieved medium at 25/90 °C; sieved medium
  F/S/M/L; sieved light F/S/M) — the swelling+erosion mode/cumulative shifts. Digitizable; the
  highest-value curves for a swelling/erosion closure.
- **Figures 4, 6**: Δd_rel vs. initial particle diameter (medium; light) — the size-independence
  evidence.
- **Figures 7, 10**: single-particle Δd_rel(t) and Progress(t) over the first 5 min, with the
  listed initial diameters (medium: 608/519/675/585/543/914 µm; light: 652/626/462/665/653/547/
  472/589/520/568/592 µm) at 80 and 25 °C — noisy but the only time-resolved series.
- **Figure 9**: aspect ratio vs. time (isotropy evidence).
- **Tables A1–A4**: t-test / Mann–Whitney / regression / ANOVA results (erosion significance,
  temperature effect, size- and roast-independence, shape invariance).

## Overlaps and conflicts
- **bed_dynamics backlog — kappa(t)=kappa0·f(P,eps,E) (compaction/swelling) and mass-conserving
  mobile-fines transport:** this is the primary target. Hargarten supplies the empirical anchors
  for *both* halves — a ~15 % isotropic swelling magnitude with a shot-timescale onset, and a
  temperature-enhanced fines-erosion source term — that any such closure must reproduce.
  Complement, not competitor (it has no model).
- **mo2023.microCT-SPH (flow, packing) + Mo 2021/2022:** direct complement. Mo 2023's
  post-extraction bottom-high porosity gradient is attributed to pressure-dependent erosion (Mo
  2021 SPH erosion model); Mo 2022 is a swelling model. Hargarten is the ambient-pressure
  *measurement* companion those models would be calibrated against — and its "no-pressure"
  caveat is exactly the regime Mo 2023 extends. The Hargarten card and the Mo 2021/2022 intake
  flagged in `mo2023.md` should be picked up together if the bed_dynamics backlog is opened.
- **pannusch2024.extraction (constant-porosity assumption):** Hargarten is Article 1 of the same
  thesis and the empirical basis pannusch2024 cites for ~15 % coarse-particle growth + erosion.
  It both *supports* constant porosity (swelling offsets dissolution) and *undercuts* it (erosion
  + swelling change permeability) — a genuine tension pannusch2024 acknowledges but does not model.
- **foster2025.infiltration (infiltration, runtime):** complementary. Foster models the wetting
  front / first drip; Hargarten shows that within that same wetting window the grains are
  simultaneously swelling (~60–80 % of final size by 30 s) and shedding fines — a bed-state
  change Foster's sharp-front dry-bed model does not carry. Motivates the preinfusion step both
  rely on.
- **brewer2026.streamtube (bed_dynamics) Rung-B fines migration:** Hargarten gives an
  independent, measured *source* of mobile fines (erosion during wetting, temperature-scaled),
  complementing brewer's hypothesis-generating migration treatment.

## Implementation estimate
Effort **S**: no equations to implement; work is transcribing Table 2 and digitizing the PSD
and time-course figures into data/, plus recording the scalar anchors (15 % swelling; 30 s/4 min
timescale; temperature-erosion sign). No code, no solver, no fit to reproduce. Dependency: only
becomes runtime-relevant when paired with an actual swelling/erosion model (Mo 2021/2022) to
calibrate — this card is the target data for that future intake, not the model itself. Gate for
any downstream closure: reproduce the sign and rough magnitude of the dry→wet PSD shift and the
temperature-dependent fines increase (Table A1), and the ~15 % isotropic coarse-particle growth.

VERDICT: data-only — measured empirical anchors (≈15 % isotropic swelling, 30 s/4 min onset, temperature-enhanced fines erosion) for the bed_dynamics swelling/mobile-fines backlog, but figure-embedded data with no predictive model and no pressure regime — effort S.
