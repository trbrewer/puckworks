# Supplementary material

<!-- Generated from the archived result records. Do not edit by hand. -->

**Separating Extractable Content from Extraction Rate in Espresso Models: Limits of Whole-Cup Measurements and the Value of Time-Resolved Data**

Every item here is cited by the main text. Items are numbered sequentially within each type: Supplementary Methods S1–S2, Supplementary Note S1, Supplementary Tables S1–S7 and Supplementary Figures S1–S4.

---

### Supplementary Methods S1

**Identifiability definitions and construction of the objective family.**

*Structural* identifiability asks whether parameters are uniquely determined by noise-free,
continuously observed data under a given observation map. It is a property of the model and the
observation map alone, decided analytically, and it is not what this paper measures.

*Practical* identifiability asks whether the parameters are localized by the data actually
available: a finite design, finite noise, a chosen objective and a bounded parameter domain. This
paper evaluates practical localization only. Structural identifiability of the full model under the
relevant observation maps is not assessed, and nothing here should be read as a claim about it in
either direction. Because a practical statement is conditional on all four of those, every such claim
in this paper is scoped to the tested model, observation map, parameter domain and objective, and
the formal term is used only as shorthand for that scoped statement.

The near-optimal sets reported throughout are *declared threshold sets* on a profiled objective,
not confidence regions: no explicit likelihood or noise model is specified, so no calibrated
coverage is claimed. Where a set reaches the boundary of the tested rate domain it is reported as
censored, because its width is then a property of the domain rather than of the data.

The compensation studied here is the two-parameter case of the broader phenomenon of sloppiness, in
which model behaviour depends on a few stiff parameter combinations while remaining nearly
invariant along many sloppy ones. Sloppiness and practical non-identifiability are related but not
equivalent; the profile is reported directly rather than inferring localization from eigenvalue
spectra.

**The objective family.** The rate multiplier is profiled on a 29-point geometric
grid spanning 0.15–6.5. At each candidate rate the solid-inventory level is optimized **for the
objective being profiled**, not once under a common least-squares fit: ordinary least squares for
the sum-of-squares objective, weighted least squares with weights \(1/y_i^2\) for relative-L2, and
iteratively reweighted least squares (IRLS) for Huber. Each curve is therefore an objective-specific
profile — a one-dimensional section through that objective's own joint minimum, rather than one
least-squares section rescored under three different outer losses. Each level solve is exact for its
objective (closed-form for the first two, converged IRLS for the third), so no alternating search is
involved. Three objectives are evaluated at every grid point:

1. *Unweighted concentration-scale sum of squares*, the primary objective; level by ordinary least
   squares, \(c^\ast = \sum_i f_i y_i / \sum_i f_i^2\).
2. *Relative L2*, which divides each residual by its observation, so every observation contributes
   equally in proportional terms and small concentrations are not down-weighted; level by weighted
   least squares, \(c^\ast = \sum_i w_i f_i y_i / \sum_i w_i f_i^2\) with \(w_i = 1/y_i^2\).
3. *Huber*, with 1.345 * 1.4826 * MAD of the residuals at the SSE optimum (95%-efficiency tuning), per panel. This limits the influence of large residuals without
   discarding them; level by IRLS, reweighting \(w_i = \min(1, \delta/|r_i|)\) to convergence.

A near-optimal set at threshold t is the set of profiled grid points whose objective lies within a
factor (1 + t) of the profiled minimum. Thresholds of 2, 5, 10 and 20 % are reported so that the
headline 10 % figure can be seen as one point in a monotone family rather than a chosen cut.

---

### Supplementary Methods S2

**Endpoint and external-trajectory processing.**

*Collection endpoint.* The source campaign reports a beverage **mass** of 40 ± 2 g, and the model
stops at a matched collected mass: the integration terminates at `t_end = M_target / Q`, where `Q`
is the source's flow column. That column is published in mL s⁻¹ but is consumed by the source model
as a mass flow in g s⁻¹, so the stopping rule returns the time at which `M_target` **grams** have
been collected. Density enters the solver when the flow is converted to a superficial velocity and
when the outlet concentration is volume-averaged; it does not convert the stopping rule into a
volume target. Every reported analysis is repeated at 38, 40 and 42 g, which is the campaign's own
declared collection tolerance rather than an invented bracket. The spread across the three endpoints
is a sensitivity analysis over that tolerance; it is not a propagated measurement uncertainty, and
should not be read as an uncertainty interval on any measurement.

One ambiguity is inherited rather than resolved. The source's flow column carries a volumetric label
and a mass consumption, and the two cannot both be right. The source's arithmetic is preserved
because every frozen parameter used here was estimated under it; if instead the published label is
correct, the realised cup is about 2 % smaller than stated, which lies inside the ±2 g window swept
above.

Two distinct estimands are reported at the three endpoints, and they are kept apart deliberately.
The first is the blind discrepancy of the source model at the optimal grind, which measures how far
an uncalibrated prediction sits from the measurement. The second is the complete transfer benchmark
of Supplementary Table S3: fit inventory and rate on the nine optimal-grind conditions at the
endpoint, freeze the calibration, predict every held-out coarse and fine observation at the same
endpoint, refit the level-only comparator at the same endpoint, and repeat the paired clustered
resampling. An endpoint-induced shift common to both predictors cancels in the model-minus-comparator
contrast even when it materially moves the blind residual, so a single reported sensitivity would
be misleading for one estimand or the other.

Estimand of the transfer benchmark: pooled held-out MAPE of the frozen optimal-grind mechanistic calibration MINUS that of the optimal-grind-trained level-only constant, both evaluated at the same matched-mass endpoint, over the declared held-out coarse/fine corpus

*External trajectory.* The external dissolved-solids series is a time-resolved trajectory measured
on different equipment from the primary campaign, at 93.0 °C and 9.0 bar.
It is used as a shape stress test, not as rate validation. Three processing choices are each swept
because none is determined by the published record: the time offset between the machine's start
signal and the first collected fraction; whether the first fraction is retained or dropped, since
it is the one most affected by that offset; and the loss used to score the fit. Rates swept:
0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0.

Two losses are reported because they weight the trajectory differently. *Profiled MAPE* weights
every fraction by the reciprocal of its observation, so the small early dissolved-solids bins
dominate it. *nRMSE* is the root-mean-square residual after a least-squares level, expressed as a
percentage of the mean observation, so bins are weighted by absolute residual instead. The full
sensitivity is Supplementary Table S4.

---

### Supplementary Note S1

**Dimensional audit of the orthogonal same-campaign inventory assay.**

This is the audit the main text refers to when it states that the assay and the model's fitted
inventory are not demonstrably commensurate. The intersection of the measured dry-coffee assay with
the profiled inventory curve equates two quantities in mg mL⁻¹ whose physical volume bases are not
shown to match, and the assay's basis alone is ambiguous by roughly a factor of three — far larger
than the ±10 % perturbation that was propagated. The valley passing near an independently measured
inventory of the same order of magnitude is a real and useful *qualitative* result; the specific
implied rate is not a secure quantitative constraint.

#### The two quantities being equated

| Quantity | Source | Value (caffeine) | Stated units | Provenance |
|---|---|---|---|---|
| `pannusch2024` `c_s0` | fitted to Schmieder fractions | **10.80** | mg mL⁻¹ | **fitted** — volume basis not independently stated; cup conc. is exactly linear in `c_s0` via the solver normalisation `cl1`, so its absolute scale is entangled with the fit |
| Angeloni Table 7 `C₀^s` | R&G dry-coffee assay | **12 540 mg L⁻¹ → 12.54 mg mL⁻¹** | `mg/L (= mg/kg, 1 kg = 1 L assumed)` | **measured** dry-coffee assay in mg kg⁻¹, reinterpreted as mg L⁻¹ under ρ = 1 g mL⁻¹ |

The reported intersection numeric conversion is arithmetically correct; the **basis identification** is the unverified step.

#### The conversion, from first principles

The assay is *mass of solute per mass of dry roast-and-ground coffee* (mg kg⁻¹). To compare it with a
model solid-phase concentration *per unit volume* (mg mL⁻¹) requires a density/volume basis:

    C_vol [mg mL⁻¹] = assay [mg kg⁻¹] · ρ [kg L⁻¹] / 1000        (per unit volume of coffee, density ρ)

or, on a per-bed-volume basis,

    C_bed [mg mL⁻¹] = assay [mg kg⁻¹] · m_dose [kg] / V_bed [mL]

The `1 kg = 1 L` assumption is exactly the choice **ρ = 1.0 g mL⁻¹** — a value that matches neither
the bulk density of R&G coffee nor its roasted-particle (skeletal) density.

#### Basis-sensitivity of the caffeine Table 7 value

Using assay = 12 540 mg kg⁻¹, dose = 20 g, and the Angeloni bed geometry R = 29.25 mm, H = 13.88 mm
(⇒ V_bed = πR²H = 37.3 cm³), ε_O = 0.305 (⇒ solid volume V_bed·(1−ε) = 25.9 cm³):

| Basis | ρ or volume | caffeine `c_s0` [mg mL⁻¹] |
|---|---|---|
| **`1 kg = 1 L` (assumed)** | ρ = 1.0 g mL⁻¹ | **12.54** |
| roasted-particle / skeletal density | ρ ≈ 1.3 g mL⁻¹ | ~16.3 |
| R&G bulk density | ρ ≈ 0.38 g mL⁻¹ | ~4.8 |
| per mL of **bulk bed** | 20 g ÷ 37.3 mL | ~6.7 |
| per mL of **solid phase** | 20 g ÷ 25.9 mL | ~9.7 |

Defensible bases span roughly **4.8–16.3 mg mL⁻¹ (≈ 3.4×)**. The typical densities used above are
order-of-magnitude literature values for roasted coffee (bulk ≈ 0.30–0.45 g cm⁻³; particle/skeletal
≈ 1.2–1.4 g cm⁻³); the conclusion does **not** depend on their exact values — even the narrowest
plausible pair (bulk 0.38 vs the assumed 1.0) already differs by ~2.6×, i.e. ≫ the ±10 % propagated.

#### Why the numeric rate is not secure

The intersection reads the rate where `c*(rate) = C₀^s`. Sliding `C₀^s` across 4.8–16.3 mg mL⁻¹
moves the intersection far along the profiled valley — well outside the reported 0.60–1.76 band, and
potentially off the tested rate domain — so **"rate ≈ 0.95" is an artefact of the ρ = 1.0 choice**,
not a measured constraint. Compounding this, `pannusch2024`'s `c_s0` is itself **fitted** with an
unanchored volume basis, so even the *correct* physical basis for the assay is not known to coincide
with the model's. The near-agreement of the two numbers (10.80 vs 12.54) is suggestive but, given the
~3.4× basis ambiguity, cannot carry quantitative weight.

#### What survives (the qualitative claim)

An independently measured solid inventory of the **same order of magnitude** as the profiled valley
is consistent with the valley and demonstrates the *design lesson*: an orthogonal inventory
measurement **could** break the inventory–rate compensation that the beverage endpoint alone cannot.
That is the defensible, useful statement — and it is unchanged by the unit-basis problem. What is not
defensible is presenting Table 7 as a numerical tie-breaker that fixes the rate at ≈ 0.95.

---

### Supplementary Table S1

**Fitted parameters and boundary flags for every solute × variety panel.**

The rate multiplier is profiled over 0.15–6.5 on a 29-point geometric grid under the primary
unweighted sum-of-squares objective; the solid-inventory level at each rate is the ordinary
least-squares minimizer for that objective (the other two objectives use their own level solvers —
see Supplementary Methods S1). "Minimum on boundary" flags a panel whose profiled optimum sits at an edge
of the tested domain, in which case the point estimate is a property of the domain. The 10 %
near-optimal range is likewise censored where it reaches an edge.

| variety | solute | conditions | rate at minimum | minimum on boundary | 10 % near-optimal range | range censored |
|---|---|---:|---:|---|---|---|
| Arabica | caffeine | 9 | 0.659 | no | 0.385–6.500 | upper |
| Arabica | trigonelline | 9 | 3.794 | no | 1.292–6.500 | upper |
| Arabica | 5CQA | 9 | 6.500 | yes | 1.935–6.500 | upper |
| Robusta | caffeine | 9 | 0.196 | no | 0.150–0.440 | lower |
| Robusta | trigonelline | 9 | 0.440 | no | 0.225–2.533 | none |
| Robusta | 5CQA | 9 | 0.150 | yes | 0.150–6.500 | lower, upper |

**Local curvature at the joint optimum.** Computed for the two panels shown in main-text Figure 2,
on natural-log parameters, by central finite differences. The sloppy direction is the unit
eigenvector of the smallest eigenvalue, in (ln rate, ln inventory) coordinates; a direction near
the antidiagonal is the inventory–rate compensation seen directly.

| variety | solute | rate at optimum | inventory level (mg mL⁻¹) | condition number | Hessian eigenvalues | sloppy direction | curvature coupling |
|---|---|---:|---:|---:|---|---|---:|
| Arabica | caffeine | 0.659 | 13.491 | 1.93e+03 | 0.264, 509 | (-0.978, +0.208) | -0.994 |
| Arabica | trigonelline | 3.794 | 5.334 | 3.62e+03 | 0.0585, 212 | (-1.000, +0.026) | -0.839 |


---

### Supplementary Table S2

**The complete objective and threshold family: all six solute × variety panels, three objective
families, four near-optimal thresholds.**

Rate domain 0.15–6.5 on a 29-point geometric grid. The count `k/29` is the number of tested rate
points inside the near-optimal set; the denominator is printed so the fraction cannot be read
without it. Censoring flags record whether the set reaches the tested lower or upper boundary, in
which case its width is a property of the tested domain rather than of the data. Objective
construction is Supplementary Methods S1.

| variety | solute | objective | threshold | points in set | fraction | rate low | rate high | log width | rate at minimum | minimum on boundary | set censored |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Arabica | caffeine | sse | 2 % | 6/29 | 0.207 | 0.504 | 0.987 | 0.673 | 0.659 | no | none |
| Arabica | caffeine | sse | 5 % | 11/29 | 0.379 | 0.440 | 1.692 | 1.346 | 0.659 | no | none |
| Arabica | caffeine | sse | 10 % | 22/29 | 0.759 | 0.385 | 6.500 | 2.827 | 0.659 | no | upper |
| Arabica | caffeine | sse | 20 % | 23/29 | 0.793 | 0.336 | 6.500 | 2.961 | 0.659 | no | upper |
| Arabica | caffeine | relative_l2 | 2 % | 5/29 | 0.172 | 0.504 | 0.863 | 0.538 | 0.576 | no | none |
| Arabica | caffeine | relative_l2 | 5 % | 8/29 | 0.276 | 0.440 | 1.130 | 0.942 | 0.576 | no | none |
| Arabica | caffeine | relative_l2 | 10 % | 19/29 | 0.655 | 0.385 | 4.340 | 2.423 | 0.576 | no | none |
| Arabica | caffeine | relative_l2 | 20 % | 24/29 | 0.828 | 0.294 | 6.500 | 3.096 | 0.576 | no | upper |
| Arabica | caffeine | huber | 2 % | 19/29 | 0.655 | 0.576 | 6.500 | 2.423 | 0.863 | no | upper |
| Arabica | caffeine | huber | 5 % | 20/29 | 0.690 | 0.504 | 6.500 | 2.557 | 0.863 | no | upper |
| Arabica | caffeine | huber | 10 % | 21/29 | 0.724 | 0.440 | 6.500 | 2.692 | 0.863 | no | upper |
| Arabica | caffeine | huber | 20 % | 23/29 | 0.793 | 0.336 | 6.500 | 2.961 | 0.863 | no | upper |
| Arabica | trigonelline | sse | 2 % | 9/29 | 0.310 | 2.214 | 6.500 | 1.077 | 3.794 | no | upper |
| Arabica | trigonelline | sse | 5 % | 11/29 | 0.379 | 1.692 | 6.500 | 1.346 | 3.794 | no | upper |
| Arabica | trigonelline | sse | 10 % | 13/29 | 0.448 | 1.292 | 6.500 | 1.615 | 3.794 | no | upper |
| Arabica | trigonelline | sse | 20 % | 15/29 | 0.517 | 0.987 | 6.500 | 1.884 | 3.794 | no | upper |
| Arabica | trigonelline | relative_l2 | 2 % | 10/29 | 0.345 | 1.935 | 6.500 | 1.211 | 3.316 | no | upper |
| Arabica | trigonelline | relative_l2 | 5 % | 12/29 | 0.414 | 1.479 | 6.500 | 1.481 | 3.316 | no | upper |
| Arabica | trigonelline | relative_l2 | 10 % | 14/29 | 0.483 | 1.130 | 6.500 | 1.750 | 3.316 | no | upper |
| Arabica | trigonelline | relative_l2 | 20 % | 16/29 | 0.552 | 0.863 | 6.500 | 2.019 | 3.316 | no | upper |
| Arabica | trigonelline | huber | 2 % | 8/29 | 0.276 | 2.533 | 6.500 | 0.942 | 6.500 | yes | upper |
| Arabica | trigonelline | huber | 5 % | 10/29 | 0.345 | 1.935 | 6.500 | 1.211 | 6.500 | yes | upper |
| Arabica | trigonelline | huber | 10 % | 13/29 | 0.448 | 1.292 | 6.500 | 1.615 | 6.500 | yes | upper |
| Arabica | trigonelline | huber | 20 % | 15/29 | 0.517 | 0.987 | 6.500 | 1.884 | 6.500 | yes | upper |
| Arabica | 5CQA | sse | 2 % | 3/29 | 0.103 | 4.966 | 6.500 | 0.269 | 6.500 | yes | upper |
| Arabica | 5CQA | sse | 5 % | 6/29 | 0.207 | 3.316 | 6.500 | 0.673 | 6.500 | yes | upper |
| Arabica | 5CQA | sse | 10 % | 10/29 | 0.345 | 1.935 | 6.500 | 1.211 | 6.500 | yes | upper |
| Arabica | 5CQA | sse | 20 % | 14/29 | 0.483 | 1.130 | 6.500 | 1.750 | 6.500 | yes | upper |
| Arabica | 5CQA | relative_l2 | 2 % | 4/29 | 0.138 | 4.340 | 6.500 | 0.404 | 6.500 | yes | upper |
| Arabica | 5CQA | relative_l2 | 5 % | 7/29 | 0.241 | 2.898 | 6.500 | 0.808 | 6.500 | yes | upper |
| Arabica | 5CQA | relative_l2 | 10 % | 10/29 | 0.345 | 1.935 | 6.500 | 1.211 | 6.500 | yes | upper |
| Arabica | 5CQA | relative_l2 | 20 % | 15/29 | 0.517 | 0.987 | 6.500 | 1.884 | 6.500 | yes | upper |
| Arabica | 5CQA | huber | 2 % | 3/29 | 0.103 | 4.966 | 6.500 | 0.269 | 6.500 | yes | upper |
| Arabica | 5CQA | huber | 5 % | 6/29 | 0.207 | 3.316 | 6.500 | 0.673 | 6.500 | yes | upper |
| Arabica | 5CQA | huber | 10 % | 10/29 | 0.345 | 1.935 | 6.500 | 1.211 | 6.500 | yes | upper |
| Arabica | 5CQA | huber | 20 % | 14/29 | 0.483 | 1.130 | 6.500 | 1.750 | 6.500 | yes | upper |
| Robusta | caffeine | sse | 2 % | 6/29 | 0.207 | 0.150 | 0.294 | 0.673 | 0.196 | no | lower |
| Robusta | caffeine | sse | 5 % | 7/29 | 0.241 | 0.150 | 0.336 | 0.808 | 0.196 | no | lower |
| Robusta | caffeine | sse | 10 % | 9/29 | 0.310 | 0.150 | 0.440 | 1.077 | 0.196 | no | lower |
| Robusta | caffeine | sse | 20 % | 18/29 | 0.621 | 0.150 | 6.500 | 3.769 | 0.196 | no | lower, upper |
| Robusta | caffeine | relative_l2 | 2 % | 6/29 | 0.207 | 0.150 | 0.294 | 0.673 | 0.225 | no | lower |
| Robusta | caffeine | relative_l2 | 5 % | 8/29 | 0.276 | 0.150 | 0.385 | 0.942 | 0.225 | no | lower |
| Robusta | caffeine | relative_l2 | 10 % | 10/29 | 0.345 | 0.150 | 0.504 | 1.211 | 0.225 | no | lower |
| Robusta | caffeine | relative_l2 | 20 % | 23/29 | 0.793 | 0.150 | 6.500 | 3.769 | 0.225 | no | lower, upper |
| Robusta | caffeine | huber | 2 % | 6/29 | 0.207 | 0.150 | 0.294 | 0.673 | 0.196 | no | lower |
| Robusta | caffeine | huber | 5 % | 7/29 | 0.241 | 0.150 | 0.336 | 0.808 | 0.196 | no | lower |
| Robusta | caffeine | huber | 10 % | 9/29 | 0.310 | 0.150 | 0.440 | 1.077 | 0.196 | no | lower |
| Robusta | caffeine | huber | 20 % | 18/29 | 0.621 | 0.150 | 6.500 | 3.769 | 0.196 | no | lower, upper |
| Robusta | trigonelline | sse | 2 % | 6/29 | 0.207 | 0.336 | 0.659 | 0.673 | 0.440 | no | none |
| Robusta | trigonelline | sse | 5 % | 11/29 | 0.379 | 0.294 | 1.130 | 1.346 | 0.440 | no | none |
| Robusta | trigonelline | sse | 10 % | 19/29 | 0.655 | 0.225 | 2.533 | 2.423 | 0.440 | no | none |
| Robusta | trigonelline | sse | 20 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.440 | no | lower, upper |
| Robusta | trigonelline | relative_l2 | 2 % | 8/29 | 0.276 | 0.440 | 1.130 | 0.942 | 0.576 | no | none |
| Robusta | trigonelline | relative_l2 | 5 % | 15/29 | 0.517 | 0.336 | 2.214 | 1.884 | 0.576 | no | none |
| Robusta | trigonelline | relative_l2 | 10 % | 24/29 | 0.828 | 0.294 | 6.500 | 3.096 | 0.576 | no | upper |
| Robusta | trigonelline | relative_l2 | 20 % | 27/29 | 0.931 | 0.196 | 6.500 | 3.500 | 0.576 | no | upper |
| Robusta | trigonelline | huber | 2 % | 8/29 | 0.276 | 0.336 | 0.863 | 0.942 | 0.504 | no | none |
| Robusta | trigonelline | huber | 5 % | 15/29 | 0.517 | 0.294 | 1.935 | 1.884 | 0.504 | no | none |
| Robusta | trigonelline | huber | 10 % | 26/29 | 0.897 | 0.225 | 6.500 | 3.365 | 0.504 | no | upper |
| Robusta | trigonelline | huber | 20 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.504 | no | lower, upper |
| Robusta | 5CQA | sse | 2 % | 12/29 | 0.414 | 0.150 | 0.659 | 1.481 | 0.150 | yes | lower |
| Robusta | 5CQA | sse | 5 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.150 | yes | lower, upper |
| Robusta | 5CQA | sse | 10 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.150 | yes | lower, upper |
| Robusta | 5CQA | sse | 20 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.150 | yes | lower, upper |
| Robusta | 5CQA | relative_l2 | 2 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.440 | no | lower, upper |
| Robusta | 5CQA | relative_l2 | 5 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.440 | no | lower, upper |
| Robusta | 5CQA | relative_l2 | 10 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.440 | no | lower, upper |
| Robusta | 5CQA | relative_l2 | 20 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.440 | no | lower, upper |
| Robusta | 5CQA | huber | 2 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.336 | no | lower, upper |
| Robusta | 5CQA | huber | 5 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.336 | no | lower, upper |
| Robusta | 5CQA | huber | 10 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.336 | no | lower, upper |
| Robusta | 5CQA | huber | 20 % | 29/29 | 1.000 | 0.150 | 6.500 | 3.769 | 0.336 | no | lower, upper |

**Reading.** The objective minimum is interior in 13 of 18 panel × objective cells, so
the interior minimum of the illustrative Arabica-caffeine panel is *not* a universal feature. The
10 % near-optimal set reaches a tested boundary in 16 of 18 cells. The breadth of the
near-optimal set is therefore robust to the objective, while the location of the point minimum is
not.


---

### Supplementary Table S3

**Endpoint propagation: the complete transfer-versus-comparator benchmark at 38, 40 and 42 g.**

For each endpoint the whole procedure is repeated — fit inventory and rate on the nine
optimal-grind conditions at that endpoint, freeze the calibration, predict all held-out coarse and
fine observations at the same endpoint, refit the optimal-grind-trained level-only comparator at the
same endpoint, and repeat the clustered resampling of the paired loss under every declared scheme.
Processing is described in Supplementary Methods S2.

<!-- paper-a:transfer-endpoint-table-supp:begin -->
<!-- paper-a:transfer-corpus schema=4 n_records=44 n_observations=132 manifest_sha256=fe46b65becbd5c421e929de3c4847eba0630e82bf08cc0c6856718cdd55907f8 -->

Corpus: complete held-out C/F corpus (on-grid + off-grid), 44 held-out records × 3 named solutes = 132 observations. No coarse/fine record is excluded. Held-out record identifiers: A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, A31, A32, A33, R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30, R31, R32, R33.

| endpoint | model pooled MAPE (%) | comparator (%) | paired difference (pp) | cond_in_variety (pp) | sample_in_variety_grind (pp) | cond_in_group (pp) | group (pp) | primary zero relation | model worse on | relative pooled-MAPE reduction (%) |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 38 g | 8.39 | 8.83 | −0.447 | [−0.884, −0.042] | [−0.802, −0.097] | [−0.798, −0.085] | [−0.940, −0.060] | excludes zero on the negative side | 61 of 132 | 4.98 |
| 40 g | 8.44 | 8.83 | −0.394 | [−0.829, +0.004] | [−0.742, −0.053] | [−0.740, −0.039] | [−0.863, −0.024] | contains zero | 62 of 132 | 4.42 |
| 42 g | 8.41 | 8.83 | −0.425 | [−0.891, +0.006] | [−0.804, −0.053] | [−0.792, −0.051] | [−0.883, −0.035] | contains zero | 60 of 132 | 4.76 |

**Reading.** The effect size is stable: −0.447 to −0.394 pp across 38, 40 and 42 g, a spread of 0.053 pp — an order of magnitude smaller than the ≈ 5 pp movement in the blind optimal-grind residual over the same endpoints, which is what one expects when both predictors are re-derived at each endpoint so that a shift common to both cancels. The sign never changes and the model remains worse on roughly half the held-out observations at every endpoint. At the canonical draw count the primary clustered range contains zero at 40 g and 42 g; excludes zero on the negative side at 38 g. Because the estimand is pooled MAPE for the mechanistic model minus pooled MAPE for the O-trained level-only comparator in percentage points, negative values favour the mechanistic model: across the sweep the most favourable bound is −0.891 pp and the least favourable is +0.006 pp, so at their unfavourable end these ranges concede the model no advantage at all. These are fixed-predictor clustered sensitivity ranges, without calibrated coverage and without a predeclared practical margin, so their positions determine neither superiority, non-inferiority, equivalence, nor absence of skill: this analysis does not establish whether the observed pooled MAPE difference is reproducible or practically useful, and it does not establish that the difference is absent. The final column is a descriptive relative error reduction, 100 x (comparator − model) / comparator computed from the full-precision pooled values, not an inferential measure; positive values favour the mechanistic model.

**Scope of the Monte Carlo audit.** All displayed ranges use the canonical draw count. A multi-seed estimate of Monte Carlo variability exists for **one** target only — 40 g, cond_in_variety, primary fitting loss — where the lower- and upper-bound standard errors are approximately 0.000520 and 0.000466 pp and the upper bound's sign is stable across 20 independent seeds. The 38 g and 42 g bounds, the three secondary schemes and the alternative fitting loss were **not** separately audited, and none of them inherits that value; only the multi-seed precision audit is absent, not the canonical range itself. The audit measures numerical approximation and confers no coverage interpretation.
<!-- paper-a:transfer-endpoint-table-supp:end -->

**Per group.** Macro MAPE for each variety × solute group at each endpoint.

| endpoint | group | model macro MAPE (%) | comparator macro MAPE (%) | difference (pp) |
|---|---|---:|---:|---:|
| 38 g | Arabica:5CQA | 12.42 | 13.96 | -1.54 |
| 38 g | Arabica:caffeine | 7.97 | 8.72 | -0.75 |
| 38 g | Arabica:trigonelline | 6.39 | 6.46 | -0.07 |
| 38 g | Robusta:5CQA | 8.57 | 8.95 | -0.38 |
| 38 g | Robusta:caffeine | 7.58 | 7.48 | +0.10 |
| 38 g | Robusta:trigonelline | 7.37 | 7.43 | -0.06 |
| 40 g | Arabica:5CQA | 12.48 | 13.96 | -1.48 |
| 40 g | Arabica:caffeine | 8.11 | 8.72 | -0.61 |
| 40 g | Arabica:trigonelline | 6.47 | 6.46 | +0.01 |
| 40 g | Robusta:5CQA | 8.61 | 8.95 | -0.34 |
| 40 g | Robusta:caffeine | 7.59 | 7.48 | +0.11 |
| 40 g | Robusta:trigonelline | 7.38 | 7.43 | -0.05 |
| 42 g | Arabica:5CQA | 12.55 | 13.96 | -1.41 |
| 42 g | Arabica:caffeine | 7.87 | 8.72 | -0.85 |
| 42 g | Arabica:trigonelline | 6.42 | 6.46 | -0.04 |
| 42 g | Robusta:5CQA | 8.65 | 8.95 | -0.30 |
| 42 g | Robusta:caffeine | 7.58 | 7.48 | +0.10 |
| 42 g | Robusta:trigonelline | 7.38 | 7.43 | -0.05 |

The level-only comparator's pooled MAPE is 8.83 % at ALL THREE endpoints, and that is a correctness check rather than a coincidence: the comparator is fitted to MEASURED concentrations, which do not depend on where the solver terminates. Only the mechanistic predictor moves with the endpoint. If the comparator had moved too, the pipeline would not be doing what this analysis claims.

**Not the same quantity as the blind-residual sweep.** This is NOT the same quantity as `endpoint_mass_sensitivity`, which reports the blind optimal-grind per-condition residual. Both predictors are re-derived at each endpoint here, so a shift common to both cancels -- which is exactly why the ~5 pp movement in the blind residual does not by itself imply that the model-versus-comparator conclusion is endpoint-dependent.


---

### Supplementary Table S4

**External dissolved-solids trajectory under both losses, for every time-alignment and first-bin
choice.**

Conditions and loss definitions are given in Supplementary Methods S2.

| case | time offset (s) | first bin | min MAPE (%) | best rate (MAPE) | range ratio (MAPE) | min nRMSE (%) | best rate (nRMSE) | range ratio (nRMSE) | cup range ratio |
|---|---|---|---|---|---|---|---|---|---|
| offset0s_all_bins | 0 | included | 30.80 | 0.4 | 1.87 | 56.58 | 0.25 | 1.30 | 1.00 |
| offset0s_no_first_bin | 0 | dropped | 26.81 | 0.4 | 2.07 | 63.27 | 0.25 | 1.29 | 1.00 |
| offset2s_all_bins | 2 | included | 32.32 | 0.4 | 1.80 | 62.84 | 0.25 | 1.23 | 1.00 |
| offset2s_no_first_bin | 2 | dropped | 28.18 | 0.4 | 1.98 | 70.02 | 0.25 | 1.22 | 1.00 |
| offset4s_all_bins | 4 | included | 35.23 | 0.25 | 1.64 | 67.43 | 0.25 | 1.20 | 1.00 |
| offset4s_no_first_bin | 4 | dropped | 31.25 | 0.25 | 1.77 | 74.93 | 0.25 | 1.19 | 1.00 |

**Reading.** Under the absolute-residual loss the rate preference is SHALLOWER (range ratio 1.19-1.30 vs 1.64-2.07 under MAPE), the minimum residual is much larger (57-75 % vs 27-35 %), and the preferred rate moves to 0.25 -- the LOWER BOUNDARY of the swept rate set, so it is censored. The shallow preference reported under MAPE is therefore partly an early-bin percentage-error effect, and the panel supports less than the MAPE-only reporting implied.

The cup range ratio is 1.00 in every case. That is algebraic, not empirical: with one integrated
scalar and one free multiplicative level, the model matches the scalar exactly at every rate.


---

### Supplementary Table S5

**Convergence of the spatial discretisation and the integration tolerance.**

This is convergence of the **spatial discretisation and integration tolerance**, which is a
different quantity from the rate-parameter-grid convergence reported in the main text. It is
included because the paper's temporal-information result depends on the shape of the outlet
trajectory, so the numerics producing that shape are load-bearing.

Numerical scheme: five-point biased-upwind advection on a uniform axial grid; Dirichlet inlet c_l(z=0)=0; stiff BDF integration with a supplied Jacobian sparsity pattern and a numerically estimated Jacobian.

Panel: Arabica:caffeine, granulometry O, 9 conditions.
Deviations are measured against the finest cell tested. **Scope of this table:**
one panel (Arabica:caffeine, optimal grind, 9 conditions), the listed whole-cup/fraction/profile outputs, and the tested node x tolerance domain. Nothing outside that scope is certified by it.

| axial nodes | rel/abs tolerance | whole cup | early | middle | late | rate at minimum | range ratio | dev. cup (%) | dev. late (%) | dev. range ratio (%) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1e-05 | 4.55880 | 7.38355 | 3.98797 | 2.30487 | 0.884 | 1.4268 | 0.0001 | 0.0004 | 0.0011 |
| 100 | 1e-06 | 4.55880 | 7.38352 | 3.98800 | 2.30488 | 0.884 | 1.4269 | 0.0001 | 0.0002 | 0.0016 |
| 100 | 1e-07 | 4.55880 | 7.38352 | 3.98800 | 2.30488 | 0.884 | 1.4268 | 0.0000 | 0.0000 | 0.0001 |
| 200 | 1e-05 | 4.55881 | 7.38358 | 3.98797 | 2.30490 | 0.884 | 1.4265 | 0.0003 | 0.0006 | 0.0204 |
| 200 | 1e-06 | 4.55880 | 7.38352 | 3.98800 | 2.30488 | 0.884 | 1.4268 | 0.0000 | 0.0001 | 0.0004 |
| 200 | 1e-07 | 4.55880 | 7.38352 | 3.98800 | 2.30488 | 0.884 | 1.4268 | 0.0000 | 0.0000 | 0.0001 |
| 400 | 1e-05 | 4.55882 | 7.38346 | 3.98809 | 2.30491 | 0.884 | 1.4266 | 0.0004 | 0.0013 | 0.0174 |
| 400 | 1e-06 | 4.55880 | 7.38353 | 3.98800 | 2.30488 | 0.884 | 1.4268 | 0.0000 | 0.0001 | 0.0009 |
| 400 | 1e-07 | 4.55880 | 7.38352 | 3.98800 | 2.30488 | 0.884 | 1.4268 | 0.0000 | 0.0000 | 0.0000 |

Concentrations are in mg mL⁻¹ on the model's internal basis; deviations are relative to the finest
cell.

**Reading.** The spatial discretisation and integration tolerance are converged at the production configuration by a wide margin. Across three axial resolutions (100, 200 and 400 nodes) × three solver tolerances (1e-5, 1e-6, 1e-7), the whole-cup concentration varies by at most 0.0004 %, the late fraction — the most discretisation-sensitive of the three sub-intervals — by at most 0.0013 %, and the profile range ratio by at most 0.0204 %. The location of the profiled-objective minimum is the same (0.884) in all nine cells. Within this panel the result is therefore not an artefact of the numerics: the Arabica-caffeine optimal-grind profile, including the breadth and the boundary-reaching extent of its near-optimal set, is reproduced across every tested cell. This is a REPRESENTATIVE-PANEL check, and its scope is exactly that. It does not certify the other five variety x solute panels, the other two objective families, the endpoint-propagation benchmark, the coarse/fine transfer result or the clustered resampling, and the near-optimal set's boundary flag was not itself carried as a convergence output. The paper's identifiability conclusion rests on those analyses, of which this table checks the numerics of one. Even 100 axial nodes reproduces the 400-node answer, so the production grid of 200 is already beyond what these outputs require. This is convergence of the discretisation only; it is not evidence about the accuracy of the continuum model itself.

Worst-case relative deviation across all nine cells: whole cup 0.0004 %, late
fraction 0.0013 %, profile range ratio 0.0204 %. The profiled
minimum location is identical in every cell.

**Solver diagnostics.** SciPy emitted six RuntimeWarnings during the sweep (four 'overflow encountered in multiply', two 'invalid value encountered in multiply'; two unique messages), all from `scipy.integrate._ivp.common.num_jac` — the numerical Jacobian estimator. The solver supplies a Jacobian sparsity pattern but not an analytic Jacobian, so SciPy estimates the entries by finite differences, and its step-size heuristic can overflow on the stiffest cells. They are recorded rather than suppressed.

That they do not affect the reported values now rests on evidence independent of cross-cell agreement, which two configurations exercising the same numerical path could satisfy while both were wrong. Across all 1458 profiled solves in the nine cells, every integration terminated successfully, every stored state was finite, the accumulated volume and cumulative mass were monotone, and concentrations stayed physical — the worst interior liquid value was +4.47e-07 and the worst solid value -4.53e-09 (a negligible undershoot of the kind an upwind advection scheme produces, not a failed integration). The inlet node is excluded from the positivity check: it carries the Dirichlet condition, which the right-hand side imposes on a zeroed copy, so the stored value there is unconstrained and physically meaningless. These checks cover the solution at the requested output times, not every internal BDF step.

Re-running the sweep with this instrumentation reproduced every previously archived cell value exactly, so the numbers below are confirmed rather than replaced.


---

### Supplementary Table S6

<!-- paper-a:transfer-scheme-table:begin -->
<!-- paper-a:transfer-corpus schema=4 n_records=44 n_observations=132 manifest_sha256=fe46b65becbd5c421e929de3c4847eba0630e82bf08cc0c6856718cdd55907f8 -->

**Table S6. Resampling design.** Cluster keys, strata, cluster census, ranges and widths for every declared scheme, at the canonical draw count. Exact cluster-by-cluster membership under every scheme — the sample records, grinds and named-solute observations in each cluster — is archived in the machine-readable endpoint-propagation record rather than reproduced here; Table S7 lists the held-out records with their primary cluster. Predictors are fixed in every scheme: no model, level parameter or comparator is refitted inside a draw.

| scheme | role | strata | cluster key | clusters | cluster sizes (obs × n) | range at 40 g (pp) | width (pp) |
|---|---|---|---|---:|---|---|---:|
| `cond_in_variety` | primary conservative sensitivity | variety | `variety`, `temperature_degC`, `pressure_bar` | 26 | 3×8, 6×18 | [−0.829, +0.004] | 0.833 |
| `sample_in_variety_grind` | design aligned secondary sensitivity | variety, grind | `sample_id` | 44 | 3×44 | [−0.742, −0.053] | 0.689 |
| `cond_in_group` | secondary sensitivity | variety, solute | `variety`, `solute`, `temperature_degC`, `pressure_bar` | 78 | 1×24, 2×54 | [−0.740, −0.039] | 0.702 |
| `group` | secondary coarse sensitivity | — | `variety`, `solute` | 6 | 22×6 | [−0.863, −0.024] | 0.839 |

Monte Carlo audit of one target only — 40 g, cond_in_variety, primary fitting loss: 20 independent seeds at B = 200,000 each. Upper bound mean +0.0039 pp (SD 0.0010, range +0.0022 to +0.0056); lower bound mean −0.8293 pp (SD 0.0012). The **upper** bound's sign is stable across seeds; no sign-stability flag is archived for the lower bound, which lies far from zero. Implied Monte Carlo standard errors at the canonical B = 1,000,000 are 0.000520 pp on the lower bound and 0.000466 pp on the upper — reported separately rather than as one symmetric figure, since they are two different estimators. This is numerical approximation error only and confers no coverage interpretation.
<!-- paper-a:transfer-scheme-table:end -->


---

### Supplementary Table S7

<!-- paper-a:transfer-corpus-manifest:begin -->
<!-- paper-a:transfer-corpus schema=4 n_records=44 n_observations=132 manifest_sha256=fe46b65becbd5c421e929de3c4847eba0630e82bf08cc0c6856718cdd55907f8 -->

**Table S7. Held-out coarse/fine corpus membership.** All 44 sample records scored by the headline benchmark. Each contributes the same 3 named-solute observations (caffeine, trigonelline, 5CQA), giving 132 observations. No record is excluded. The lookup comparator is undefined on the 8 off-grid records, so it is reported only on its own 108-observation support.

| sample | variety | grind | T (°C) | p (bar) | on grid? | lookup defined? | primary cluster |
|---|---|---|---:|---:|---|---|---|
| A12 | Arabica | C | 93.4 | 9 | yes | yes | `Arabica\|93.4\|9` |
| A13 | Arabica | C | 93.4 | 6 | yes | yes | `Arabica\|93.4\|6` |
| A14 | Arabica | C | 93.4 | 12 | yes | yes | `Arabica\|93.4\|12` |
| A15 | Arabica | C | 98 | 9 | yes | yes | `Arabica\|98\|9` |
| A16 | Arabica | C | 98 | 12 | yes | yes | `Arabica\|98\|12` |
| A17 | Arabica | C | 98 | 6 | yes | yes | `Arabica\|98\|6` |
| A18 | Arabica | C | 88 | 9 | yes | yes | `Arabica\|88\|9` |
| A19 | Arabica | C | 88 | 12 | yes | yes | `Arabica\|88\|12` |
| A20 | Arabica | C | 88 | 6 | yes | yes | `Arabica\|88\|6` |
| A21 | Arabica | C | 89 | 10 | **no** | **no** | `Arabica\|89\|10` |
| A22 | Arabica | C | 97 | 7 | **no** | **no** | `Arabica\|97\|7` |
| A23 | Arabica | F | 93.4 | 9 | yes | yes | `Arabica\|93.4\|9` |
| A24 | Arabica | F | 93.4 | 6 | yes | yes | `Arabica\|93.4\|6` |
| A25 | Arabica | F | 93.4 | 12 | yes | yes | `Arabica\|93.4\|12` |
| A26 | Arabica | F | 98 | 12 | yes | yes | `Arabica\|98\|12` |
| A27 | Arabica | F | 98 | 6 | yes | yes | `Arabica\|98\|6` |
| A28 | Arabica | F | 98 | 9 | yes | yes | `Arabica\|98\|9` |
| A29 | Arabica | F | 88 | 9 | yes | yes | `Arabica\|88\|9` |
| A30 | Arabica | F | 88 | 12 | yes | yes | `Arabica\|88\|12` |
| A31 | Arabica | F | 88 | 6 | yes | yes | `Arabica\|88\|6` |
| A32 | Arabica | F | 90 | 8 | **no** | **no** | `Arabica\|90\|8` |
| A33 | Arabica | F | 95 | 11 | **no** | **no** | `Arabica\|95\|11` |
| R12 | Robusta | C | 93.4 | 9 | yes | yes | `Robusta\|93.4\|9` |
| R13 | Robusta | C | 93.4 | 12 | yes | yes | `Robusta\|93.4\|12` |
| R14 | Robusta | C | 93.4 | 6 | yes | yes | `Robusta\|93.4\|6` |
| R15 | Robusta | C | 88 | 9 | yes | yes | `Robusta\|88\|9` |
| R16 | Robusta | C | 88 | 12 | yes | yes | `Robusta\|88\|12` |
| R17 | Robusta | C | 88 | 6 | yes | yes | `Robusta\|88\|6` |
| R18 | Robusta | C | 98 | 9 | yes | yes | `Robusta\|98\|9` |
| R19 | Robusta | C | 98 | 12 | yes | yes | `Robusta\|98\|12` |
| R20 | Robusta | C | 98 | 6 | yes | yes | `Robusta\|98\|6` |
| R21 | Robusta | C | 97 | 7 | **no** | **no** | `Robusta\|97\|7` |
| R22 | Robusta | C | 89 | 10 | **no** | **no** | `Robusta\|89\|10` |
| R23 | Robusta | F | 93.4 | 9 | yes | yes | `Robusta\|93.4\|9` |
| R24 | Robusta | F | 93.4 | 12 | yes | yes | `Robusta\|93.4\|12` |
| R25 | Robusta | F | 93.4 | 6 | yes | yes | `Robusta\|93.4\|6` |
| R26 | Robusta | F | 88 | 9 | yes | yes | `Robusta\|88\|9` |
| R27 | Robusta | F | 88 | 12 | yes | yes | `Robusta\|88\|12` |
| R28 | Robusta | F | 88 | 6 | yes | yes | `Robusta\|88\|6` |
| R29 | Robusta | F | 98 | 6 | yes | yes | `Robusta\|98\|6` |
| R30 | Robusta | F | 98 | 9 | yes | yes | `Robusta\|98\|9` |
| R31 | Robusta | F | 98 | 12 | yes | yes | `Robusta\|98\|12` |
| R32 | Robusta | F | 95 | 11 | **no** | **no** | `Robusta\|95\|11` |
| R33 | Robusta | F | 90 | 8 | **no** | **no** | `Robusta\|90\|8` |
<!-- paper-a:transfer-corpus-manifest:end -->


---

### Supplementary Figure S1

![Supplementary Figure S1](figures/fig3_holdouts.png)

**Figure S1. Leave-one-condition-out evaluation within the Angeloni optimal-grind design.** Each fold holds out one of nine temperature–pressure conditions within a coffee-variety × solute group, refits the target inventory and rate multiplier on the remaining eight conditions, and predicts the held-out concentration at the matched 40 g endpoint. Panel (a) compares observed and predicted concentrations; panels (b) and (c) show signed held-out residuals against temperature and pressure. Across two varieties and three named solutes, the analysis contains 54 held-out predictions. Reported resampling intervals are descriptive condition-level summaries of already-computed folds and do not repeat the nonlinear fit or remove fold dependence. Evidence tier: within-campaign cross-condition holdout, not independent-machine validation.

---

### Supplementary Figure S2

![Supplementary Figure S2](figures/fig5_joint_residual.png)

**Figure S2. In-sample compatibility of a shared inventory–rate pair across grinds.** Residuals are shown by coffee variety, solute, and grind after fitting one shared solid-inventory level and one shared Sherwood rate multiplier to all included Angeloni conditions. The comparison reports the cost of sharing against separate per-grind fits and reduced level-only baselines, together with any rate-boundary flag. The shared mechanistic fit reconstructs the pooled data at approximately 6.4% macro-MAPE versus approximately 4.9% for separate per-grind fits; this is an in-sample parameter-sharing penalty, not held-out transfer. Evidence tier: same-campaign compatibility diagnostic.

---

### Supplementary Figure S3

![Supplementary Figure S3](figures/fig7_per_group_diagnostics.png)

**Figure S3. Per-group residual diagnostics at the matched 40 g endpoint.** Each of the eight variety × observable groups contains nine Angeloni temperature–pressure conditions, all evaluated at the matched 40 g collected-mass endpoint. **Panel (a)** compares *blind* source-model MAPE — the model applied with no target-specific inventory adjustment — with MAPE after *matching* the orthogonal same-campaign roasted-and-ground inventory assay. Matching is possible only for caffeine and trigonelline, the two solutes the assay reports; the remaining groups are marked “NA” at the baseline rather than drawn as zero-height bars, which would read as zero error. Arrows mark whether matching improved or worsened each group. **Panel (b)** reports the model–data association of the corresponding response summaries **across the nine operating conditions**; this compares conditions and is **not** a temporal trajectory. Inventory matching improves one analyte and worsens another, so the residual cannot be interpreted as a pure inventory offset. Correlations are descriptive associations, not held-out skill measures, and with only nine conditions per group and eight groups they should be read as indicative rather than estimated with useful precision. Evidence tier: within-campaign diagnostic.

---

### Supplementary Figure S4

![Supplementary Figure S4](figures/fig8_residuals_vs_conditions.png)

**Figure S4. Blind source-model residuals versus temperature and pressure before target-level fitting.** Signed residuals, `(prediction − measurement)/measurement`, are plotted for each coffee-variety × solute group across the nine optimal-grind conditions at the matched 40 g endpoint. Colour denotes variety and marker denotes solute. Group-level offsets motivate a target-specific level recalibration, but the plot does not show whether within-group temperature–pressure structure remains after that level is fitted. No uncertainty interval is implied by point density. Evidence tier: pre-fit source-to-target discrepancy diagnostic.
