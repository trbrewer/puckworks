# Model card: Puelles Bulnes 2025 — brew-time two-factor ANOVA (moka / French press / drip)

**Paper/thesis:** M. E. Puelles Bulnes, V. A. A. Espinoza, A. L. Atoche Puelles, "Experimental Evaluation of Coffee Extraction Times: Integrating Statistical Analysis in Engineering Education," *23rd LACCEI International Multi-Conference* (Mexico City, 2025). DOI 10.18687/LACCEI2025.1.1.2342. ISBN 978-628-96613-1-6.
**Stage(s):** none (nominally *observables*, as a secondary-data candidate only) · **Kind:** n/a (would be calibration at best)
**Status:** **reviewed 2026-07-25 — SKIP.** Pedagogical two-factor ANOVA on total brew time for three *non-espresso* methods, no physical model, and a single unit-ambiguous time table whose method labels are transposed between the data and the post-hoc. Nothing maps to a puckworks contract; the non-espresso reference role is held by gloess2013. No component, no gate, no data: **this card is the record.**

## Scope and mechanism
No process model. This is a classroom design-of-experiments exercise: a balanced two-factor fixed-effects ANOVA on the **total preparation time** of a full carafe brewed by three *non-espresso* methods — Italian moka ("evaporation"), French press ("immersion"), and gravity drip ("filtration") — crossed with three anonymized Peruvian ground-coffee brands, at 20 g dose each, two replicates per cell (18 runs). The response is a single scalar wall-clock time per run; no chemistry, EY, TDS, flow rate, pressure, grind, or transient is measured. The "model" (Eq. 1) is the generic linear ANOVA decomposition, not a coffee-extraction model. Nothing here is espresso and nothing is a mechanism; the paper's own stated purpose is pedagogical (teaching DOE, F-tests, and residual diagnostics).

## Governing equations
Transcribed as printed; these are the standard balanced two-way ANOVA relations, implemented by any stats package (the authors used SPSS).

**(Eq. 1)** Cell-means model:
`Y_ijk = μ + τ_i + β_j + (τβ)_ij + ε_ijk`, `i = 1..a`, `j = 1..b`, `k = 1..n`
- `Y_ijk` — observed prep time in cell (i,j), replicate k
- `μ` — grand mean
- `τ_i` — effect of level i of Factor A (brewer / extraction method)
- `β_j` — effect of level j of Factor B (coffee brand)
- `(τβ)_ij` — A×B interaction effect
- `ε_ijk` — residual (measurement/random error)
- `a = 3` (methods), `b = 3` (brands), `n = 2` (replicates), `N = abn = 18`

**(Eq. 2)** Sum-of-squares partition:
`SCT = SCA + SCB + SCAB + SCE`
(total = Factor A + Factor B + interaction + residual).

Degrees of freedom (Table 1): A → a−1 = 2; B → b−1 = 2; A×B → (a−1)(b−1) = 4; error → ab(n−1) = 9; total → abn−1 = 17.
Mean squares MC = SC/gl; F-statistics FA = MCA/MCE, FB = MCB/MCE, FAB = MCAB/MCE, tested against F-critical at α = 0.05. No term simplified away; there are no terms beyond the textbook model.

## Parameters
No model parameters exist. The table records the fitted ANOVA quantities and the fixed experimental conditions. All times are **secondary/measured** by the authors; **units are not stated in the paper** — magnitudes (≈2.5–5.4 for full-carafe moka/press/drip) are consistent only with **minutes**, recorded here as inferred.

| symbol | value | units | source (measured/fitted/nominal/assumed) |
| --- | --- | --- | --- |
| dose (each method) | 20 | g | nominal (fixed condition) |
| water (drip) | 250 | mL | nominal |
| water T (drip, press final) | 100 | °C | nominal |
| brand factor B, F-stat | F = 0.098, p = 0.908 | — | fitted (not significant) |
| brewer factor A, F-stat | F = 26.520, p ≈ 0.000 | — | fitted (highly significant) |
| A×B interaction, F-stat | F = 0.389, p = 0.812 | — | fitted (not significant) |
| SS: brewer (CAFETERA) | 9.565 (gl 2, MC 4.782) | min² (inferred) | fitted |
| SS: brand (CAFE) | 0.035 (gl 2, MC 0.018) | min² (inferred) | fitted |
| SS: interaction | 0.281 (gl 4, MC 0.070) | min² (inferred) | fitted |
| SS: error (residual) | 1.623 (gl 9, MC 0.180) | min² (inferred) | fitted |
| model R² | 0.994 (adj. 0.989) | — | fitted |
| Tukey diff. Italian−drip | −1.7633, 95% CI [−2.4479, −1.0788], p < 0.001 | min (inferred) | fitted |
| Tukey diff. Italian−French | −1.1250, 95% CI [−1.8095, −0.4405], p = 0.003 | min (inferred) | fitted |
| Tukey diff. French−drip | −0.6383, 95% CI, p = 0.067 (DMS p = 0.029) | min (inferred) | fitted |
| grind size / PSD | not provided | — | — |
| bed geometry, porosity, k, tamp | not provided (non-espresso methods) | — | — |
| EY, TDS, flow rate, temperature trace | not provided | — | — |

## Calibration and validation offered by the source
Nothing physical is validated — there is no model to validate. The only "validation" is the ANOVA's own assumption checks on 18 residuals: Shapiro–Wilk p = 0.998 (normality), plus visual homoscedasticity and independence checks off the residual scatter matrix. These attest that the F-tests are internally admissible; they say nothing about any transport or extraction mechanism. Result: brewer method is significant (p ≈ 0.000), brand and interaction are not (p = 0.908, p = 0.812). The R² = 0.994 is trivially high because prep time is almost entirely set by which apparatus is used.

**Internal inconsistency (flagged, not resolved):** the raw data (Table 3) and the post-hoc/narrative disagree on which method is slowest. Table 3 cell means are moka ≈ 2.98, drip ≈ 4.10, French press ≈ 4.74 (French press slowest). But Table 5 Tukey/DMS and the conclusions report **drip** as slowest and French press intermediate (moka−drip = −1.7633 → drip ≈ 4.74; moka−French = −1.1250 → French ≈ 4.10). The numeric magnitudes match; only the "Por Filtro" and "Francesa" labels are transposed between Table 3 and the analysis/marginal-means figure. One of the two labelings is wrong. This does not affect the puckworks verdict but disqualifies the times as clean data without resolving the swap against the source SPSS output.

## Assumptions and validity range
- **Non-espresso, so out of the puckworks domain from the start**: moka is a stovetop percolator, French press is immersion, drip is gravity filtration. No 9-bar puck flow, no basket, no bed.
- Single scalar response (total time); silent on EY, TDS, flow, temperature, grind, porosity, and every transient the registry models.
- Fixed 20 g dose; drip fixed at 250 mL / 100 °C; other water volumes not fully specified per method (French press "¾ full"); no dose/grind/temperature sweep — no parameter dependence is resolvable.
- Brands anonymized ("Café 1/2/3"), roast/origin/grind undisclosed; the non-significant brand effect cannot be attributed.
- n = 2 per cell, 9 error df; adequate for the classroom F-test, thin for any quantitative time model.
- Times have **no stated units**; minutes inferred. Do not import without confirming.
- The Table 3 ↔ Table 5 method-label transposition (above) is unresolved.

## Interface mapping
Inputs consumed: none usable — the fixed conditions (dose 20 g; drip 250 mL, 100 °C) map loosely to **BedState.dose_kg** and **MachineState** temperature, but for brewers puckworks does not simulate. Outputs produced: a single non-espresso brew time that has no home in **ShotResultState.t_shot_s** (which is espresso shot time). No adapter reconciles a moka/press/drip carafe time with an espresso shot. **No runtime coupling and no offline calibration chain**: there is nothing to calibrate a k, kappa, or sigma prior against.

## Extractable data
- **Table 3** — 18 brew times (3 brands × 3 methods × 2 reps). The only numeric asset, but for non-espresso methods, unit-ambiguous, and internally mislabeled (see above). No espresso consumer.
- **Table 4** (ANOVA table) and **Table 5** (Tukey/DMS comparisons) — derived statistics, not transcribable data.
- Raw data / code: none published; the tables are the only record. No supplementary material.

## Overlaps and conflicts
- **gloess2013 (dominates, and already registered as the non-espresso intake):** Gloess covers nine methods including moka (Bia) and French press (Bo) with endpoint chemistry (TS, °Brix, pH, titratable acidity, caffeine, CQA, aroma) and a trained sensory panel on one characterized coffee — vastly richer than a single unitless time, and it already carries the caveat that its non-espresso methods are out of the espresso domain. Puelles adds nothing Gloess lacks.
- **mystkowska2024 / andueza2007 (same class — skipped non-espresso/no-model intakes):** consistent precedent; those at least carry per-species chemistry. This paper carries only a time.
- **Backlog "observables":** the open slot wants temperature effects and measurement kernels *for espresso*; a moka/press/drip carafe time does not feed it.
- No conflict with any registered component (cameron2020, brewer2026.*, wadsworth2026, foster2025): it models nothing they model and shares no material or regime.

## Implementation estimate
None warranted. No model to port, no gate to build, no data slot filled — the sole numeric table is non-espresso, unit-ambiguous, method-mislabeled, and superseded as a non-espresso reference by gloess2013.

VERDICT: skip — a pedagogical two-factor ANOVA on total brew time for three *non-espresso* methods (moka/French press/drip), with no physical model, no espresso, no EY/TDS/flow/grind, a single unit-ambiguous time table whose method labels are internally transposed between the data and the post-hoc, and nothing that maps to a puckworks contract; the non-espresso reference role is already held by gloess2013 — effort –
