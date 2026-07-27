# Paper A — submission-ready figure captions

These captions are written to stand alone from the main text. They preserve the manuscript's evidence-tier discipline and should replace repository-facing caption shorthand during venue conversion.

**Main versus supplementary.** The second review asked for four to five main figures, with the diagnostics moved to a supplement. The main set carries the three findings and the study design; everything that supports rather than states a finding is supplementary. **Presentation numbers differ from the producer identifiers, which are unchanged** — the file stems remain the keys in `puckworks.figures_paper_a`, so no result is renamed by this reordering.

**No embedded figure number.** The rendered images previously carried their producer number inside the image (`Fig 4 — …`, `Fig 6 — …`). Uploaded under the presentation numbering in the table below, an embedded "Fig 4" would have contradicted its own caption — producer `fig4_transfer` is presentation Figure 3, and producer `fig3_holdouts` is Figure S1. The generators now emit a short descriptive panel heading and **no figure number**; numbering is supplied by the caption system alone. `tests/test_figure_exports.py` fails if a number is reintroduced into an image title.

| presentation | producer / file stem | placement | states |
|---|---|---|---|
| Figure 1 | `fig1_design` | **main** | study design and dataset roles |
| Figure 2 | `fig2_objective_surface` | **main** | finding 1 — weak separation |
| Figure 3 | `fig4_transfer` | **main** | finding 2 — no resolvable gain over the null |
| Figure 4 | `fig6_fraction_vs_endpoint` | **main** | finding 3 — temporal resolution localizes the rate |
| Figure S1 | `fig3_holdouts` | supplement | within-campaign cross-condition holdout detail |
| Figure S2 | `fig5_joint_residual` | supplement | in-sample shared-parameter compatibility |
| Figure S3 | `fig7_per_group_diagnostics` | supplement | per-group residual diagnostics |
| Figure S4 | `fig8_residuals_vs_conditions` | supplement | pre-fit residual structure |

---

## Main figures

### Figure 1 (`fig1_design`)

**Figure 1. Study design, observation operators, and evidence tiers.** The source model was calibrated previously to fraction-resolved multi-solute extraction kinetics from Schmieder et al. The present analysis maps its output to a 40 mL matched-volume proxy for the 40 g Angeloni cup, profiles a target-specific solid-inventory level and a shared Sherwood rate multiplier on the optimal-grind (O) conditions, and then evaluates: leave-one-condition-out prediction within O; frozen O→coarse/fine (C/F) transfer within the Angeloni campaign; comparison to the campaign’s roasted-and-ground inventory assay; in-sample localization on the source fraction campaign; and an independent second-rig, time-resolved TDS trajectory from Waszkiewicz et al. Arrows show the actual data and parameter dependency, not analysis order: all four branches descend from the source calibration, and the external trajectory does **not** inherit the Angeloni recalibration — it freezes the source kinetics and profiles a target-specific level. The inventory assay connects laterally to the recalibration as an orthogonal same-campaign measurement, not as a validation step after the cross-grind holdout. “Independent” refers only to the external campaign; the cross-grind and leave-one-condition-out tests share machine, coffee, and campaign context.

### Figure 2 (`fig2_objective_surface`)

**Figure 2. Profiled inventory–rate objective for Angeloni optimal-grind endpoints.** For caffeine and trigonelline, the model is evaluated at nine O conditions for each coffee variety (18 condition means per solute) using the matched 40 mL endpoint operator. At every tested Sherwood rate multiplier, the solid-inventory level is reoptimized and the unweighted concentration-scale sum of squared errors (SSE) is recorded; the surface is shown relative to its minimum. The curve marks the profiled optimum, the shaded band spans the defensible mass-to-volume bases for the orthogonal roasted-and-ground inventory assay from the same campaign — it is an illustrative basis range, **not** a quantitative model constraint, because the assay's volume basis is undefended and the model's own inventory basis is not independently anchored — and the local log-parameter Hessian diagnostic is reported at the numerical minimum to two significant figures. The 10%-above-minimum profile extends from approximately 0.4 to the upper tested rate boundary, so its upper extent is right-censored. The Hessian condition number and inverse-curvature coupling describe local objective geometry, not a confidence interval or statistical correlation, because no measurement likelihood is specified. Evidence tier: in-campaign practical-identifiability diagnostic.

### Figure 3 (`fig4_transfer`)

**Figure 3. Within-campaign cross-grind prediction after target-specific calibration.** For each variety–solute group, the inventory and Sherwood rate multiplier are fitted only to the nine optimal-grind conditions and then frozen while predicting the corresponding coarse and fine conditions at the 40 mL matched-volume proxy. Panels compare observed and predicted concentrations by condition and summarize error by target grind. The benchmark is an O-trained level-only constant: one concentration level fitted on O, with no temperature, pressure, flow, or kinetic response. The pooled transfer comparison contains 108 held-out condition–solute predictions. The mechanistic model yields 8.2% pooled MAPE versus 8.6% for the constant and is worse on 50 of 108 points; error bars/envelopes, where shown, propagate the declared discrete set of O-fit rates within 10% of the minimum, not a continuous confidence region. Evidence tier: within-campaign cross-grind holdout with a trained null.

### Figure 4 (`fig6_fraction_vs_endpoint`)

**Figure 4. Rate-profile comparison across three evidence tiers.** Panels (a–c) compare empirical fraction-resolved profiles from the Schmieder calibration campaign with the same model’s simulated sampled aggregate and exact whole-cup endpoint for caffeine, trigonelline, and 5-CQA. Simulated exact-cup bands are mean ±1 SD across 20 random seeds and quantify Monte Carlo variability, not experimental uncertainty. Panel (d) profiles a target-specific level against an independent Waszkiewicz TDS trajectory; the shaded band spans declared time-alignment/first-bin choices, while the single integrated cup is **not estimable** — one scalar observation paired with one profiled level is matched exactly at every rate — and is therefore drawn as a flat reference line rather than as a zero-error curve, which would read as perfect prediction. The external trajectory has a shallow minimum near rate multiplier 0.4 with approximately 27% minimum MAPE. Evidence tiers are, respectively, in-sample source-campaign localization, same-model simulation, and independent external shape test; they should not be pooled as equivalent validation.

---

## Supplementary figures

### Figure S1 (`fig3_holdouts`)

**Figure S1. Leave-one-condition-out evaluation within the Angeloni optimal-grind design.** Each fold holds out one of nine temperature–pressure conditions within a coffee-variety × solute group, refits the target inventory and rate multiplier on the remaining eight conditions, and predicts the held-out concentration at the matched 40 mL endpoint. Panel (a) compares observed and predicted concentrations; panels (b) and (c) show signed held-out residuals against temperature and pressure. Across two varieties and three named solutes, the analysis contains 54 held-out predictions. Reported resampling intervals are descriptive condition-level summaries of already-computed folds and do not repeat the nonlinear fit or remove fold dependence. Evidence tier: within-campaign cross-condition holdout, not independent-machine validation.

### Figure S2 (`fig5_joint_residual`)

**Figure S2. In-sample compatibility of a shared inventory–rate pair across grinds.** Residuals are shown by coffee variety, solute, and grind after fitting one shared solid-inventory level and one shared Sherwood rate multiplier to all included Angeloni conditions. The comparison reports the cost of sharing against separate per-grind fits and reduced level-only baselines, together with any rate-boundary flag. The shared mechanistic fit reconstructs the pooled data at approximately 6.4% macro-MAPE versus approximately 4.9% for separate per-grind fits; this is an in-sample parameter-sharing penalty, not held-out transfer. Evidence tier: same-campaign compatibility diagnostic.

### Figure S3 (`fig7_per_group_diagnostics`)

**Figure S3. Per-group blind and inventory-matched residual diagnostics at the optimal grind.** Each variety × observable group contains nine Angeloni temperature–pressure conditions evaluated at the 40 mL proxy endpoint. Panel (a) compares blind source-model MAPE with MAPE after matching the independent inventory assay where available; panel (b) reports the model–data correlation across conditions. Inventory matching can improve one analyte and worsen another, so the residual cannot be interpreted as a pure inventory offset. Correlations are descriptive associations across operating conditions, not temporal correlations or held-out skill measures. Evidence tier: within-campaign diagnostic.

### Figure S4 (`fig8_residuals_vs_conditions`)

**Figure S4. Blind source-model residuals versus temperature and pressure before target-level fitting.** Signed residuals, `(prediction − measurement)/measurement`, are plotted for each coffee-variety × solute group across the nine optimal-grind conditions at the matched 40 mL endpoint. Colour denotes variety and marker denotes solute. Group-level offsets motivate a target-specific level recalibration, but the plot does not show whether within-group temperature–pressure structure remains after that level is fitted. No uncertainty interval is implied by point density. Evidence tier: pre-fit source-to-target discrepancy diagnostic.
