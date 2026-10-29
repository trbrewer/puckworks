# Trapped-air prior and comparison conventions

**A qualitative cubic relative-permeability shape was found; no transferable
bound on coffee's residual trapped-air fraction was found in the checked local
sources.** The physical parameter range is `0 <= s0 <= 1`; that range is not
an experimental prior. Here s0 means the gas-filled fraction at zero gauge
pressure, and `S(P) = 1 - s0 * 1.01325 / (P + 1.01325)`. Gauge pressure is in
bar. This assumes Boyle compression of retained gas; it does not measure that
gas, model its dissolution, or distinguish entrained air from generated CO2.

The repository's `sourcing2026.g1_glassbead_analog` evidence is exposed through
the [glass-bead card](../../cards/g1_glassbead_analog.md) and
[existing aggregate table](../../../puckworks/data/g1_glassbead_analog/glassbead_retention_kr.csv).
Yasuda, Katsuragi and Katsura (2025),
[*Liquid water transport model in hydrophilic granular*](https://arxiv.org/html/2501.13361v1#S10),
Appendix B, Eq. 41 and Fig. 18, fit a cubic permeability curve to selected
Topp–Miller glass-bead observations. Its residual saturation is **retained
liquid water**, not trapped air. Eq. 43 approximates the curve by a cubic in
water saturation. This supplies a shape analogy for m=3, not a measured coffee
exponent or a statistical interval for m. The bead medium, drying protocol and
saturation range limit transfer to espresso.

The existing table was inspected locally; the original author's Appendix B was
also checked read-only. Its arXiv posting uses a perpetual non-exclusive
distribution licence, not a Creative Commons data licence. This note contains
original commentary about mathematical facts; it reproduces no source table,
curve, artwork or experimental reading. No new bead data are committed.

Foster et al. (2025),
[*Dynamics of liquid infiltration into an espresso bed using time-resolved
micro-computed tomography*](https://doi.org/10.1063/5.0245167), model compressed
gas in the headspace above the bed. That compartment is distinct from residual
gas in conducting pores. Their sharp-front model assumes full saturation behind
the front and supplies neither a pore-air fraction nor a relative-permeability
exponent. Their discussion explicitly recognizes potentially trapped pore gas,
but does not quantify it. The local original
`/home/tim/foster-radial-001-evidence/source.pdf`, its repository cover sheet
(CC BY-NC-SA 4.0), [card](../../cards/foster2025_2.md) and existing parameter
table were inspected. No numerical prior is extracted from headspace volume or
the fitted total porosity; no source artwork is reproduced or relicensed.

The configured `/home/tim/Documents/data` inventory, the available-data register,
MANIFEST, [G1 retention search target](../../cards/g1_retention_search_target.md),
Egidi's card, and the local Hargarten/Maillé swelling evidence were also checked.
The latter discuss bubbles, degassing and optical limitations without an
identified coffee pore-air fraction or permeability exponent. These bounded
checks do not establish that such measurements do not exist elsewhere.

## Use in this screen

Primary F1/F2 use m=3; m=2 and m=4 are explicit sensitivities, each with matching
timing fits. The requested `F1-PRIOR` and `F2-PRIOR` rows apply the only available
shape constraint, m=3. They are exact repetitions of F1/F2, including their
200 refits, not additional evidence or independent trials. There is no invented
s0 bound based on residual *liquid* saturation. Changing pressure view or m does
not replace the primary result.

W1 uses exponential compaction; WD1 uses the original locked D1 permeability.
W2 and WD2 add the same Boyle term to their respective timing laws. W1/WD1 fit
t0, c and compaction. W2/WD2 have four parameters and are **EXPLORATORY**: the
3.5–6-bar minimum region contains a positive infiltration-time contribution,
so it cannot separately fix t0 without another assumption. No offset is set to
the observed minimum merely to lower the parameter count.

For D1, `phi(P) = phi0 - (1-phi0)*P/Ydry`, with the inherited phi0=0.122.
Let `phi_peak = (4+phi0 - sqrt((4+phi0)^2-24*phi0))/4`. The reported air-free
compaction pressure is `Pstar = Ydry*(phi0-phi_peak)/(1-phi0)`, the maximum of
`P*k_D1(P)`. This is an exact reparameterization; it does not replace D1's
permeability by an exponential. D1 timing fits require positive permeability
over the declared 0–14 bar forcing domain. Other bounds are broad numerical
search limits, not priors from these sources: t0=0–120 s, c=0.0001–10000,
timing compaction scale up to 100 bar, s0=0–1; hydraulic scale/Mc bounds are
inherited from B0. F1/F2 retain the inherited compaction bounds after conversion.

The requested **like-with-like consistency check** uses the maximum of
`P*k(P)*kr(P)` for air models, and `P*k(P)` for models without air. Its timing
counterpart is the minimum of the matching timing law. The delivered-mass term
is excluded from both extrema. Exponential compaction scales and D1 air-free
peak scales are also reported separately in the CSVs. F2 is checked against
WD2, and the exponential W2 comparison is reported additionally. The full-model
endpoint peak is a separate, nominal-condition statistic using held-out
predictions and retains the original 5–7-bar requirement.

All coefficients used to score a held-out pressure come from its training
fold. Endpoint-refitted C4/D1 supply Mc to F1/F2 within that fold; F1/F2 then
fit only scale, compaction and s0. T2 fits only flow scale and Mc while fixing
compaction and s0 from its training-fold timing fit. Neither measured delay nor
predicted delay enters the hydraulic equation or its state initialization.
Full-cohort coefficients are descriptive estimates only; their 95% intervals
use 200 whole-brew refits, with both timing and flow calibrations repeated.

For T2, comparing its timing-fixed coefficients back to timing would be true by
construction. The reported consistency check instead uses the independently
flow-fitted C4/D1/F1/F2 counterpart, named in the table along with its interval.
T2 transfers based on four-parameter timing models remain exploratory. The
primary F1/F2 models still require all five requested PASS criteria, including
overlap with their matching timing conductance-peak interval.

Reproduce with the existing analysis module:

```bash
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 python -m puckworks.analysis.pressure_peak_stage_b0 \
  --air-screen --ewp /path/to/espresso-whole-pull --raw /path/to/Waszkiewicz/upstream \
  --workers 32 --refits 200
```

Seed: 20261101. Delay RMSE and endpoint RMSE average the within-condition brew
RMSEs, preserving the B0 comparison convention. Timing and endpoint predictions
use leave-one-pressure-out folds; parameter intervals and conductance extrema
come from descriptive full-cohort refits. Loss comparisons use 1000 paired
condition-then-brew resamples; parameter, response and trend intervals use 200
within-condition whole-brew refits. Endpoint integration and the last-30-s trend
observer are checked on finer grids. The B0c onset means are reproduced exactly
from its unchanged detector and checked against ONSET.csv before fitting.

Waszkiewicz aggregates in both CSVs credit Waszkiewicz et al. (2025),
[Zenodo 18046315](https://zenodo.org/records/18046315), CC-BY-4.0. Individual
onsets, native traces and local fit checkpoints are not committed. All new
prior prose is original attributed commentary; source licences are not changed.
