# Paper A — INTERNAL figure map and caption source

> **This file is not a submission deliverable.** It is the repository's figure bookkeeping: which
> producer renders which presentation figure, why the numbering differs, and the authored caption
> text. It deliberately contains producer identifiers, module paths, test paths and review history,
> none of which an editor should receive.
>
> The **upload-ready** captions are generated from this file into
> `docs/submission/PAPER_A_JFE_FIGURE_CAPTIONS.md` by `tools/paper_a_figure_captions.py`, and that
> is the file the package manifest lists. Round-10 P2-1: this document was previously titled
> "submission-ready figure captions" while opening with three paragraphs of review and test
> narration — a file named for one purpose and written for another is an upload risk, and calling it
> submission-ready is what made that risk invisible.

**Main versus supplementary.** An earlier round of review asked for four to five main figures, with
the diagnostics moved to a supplement. The main set carries the three findings and the study design;
everything that supports rather than states a finding is supplementary. **Presentation numbers differ
from the producer identifiers, which are unchanged** — the file stems remain the keys in
`puckworks.figures_paper_a`, so no result is renamed by this reordering.

**No embedded figure number.** The rendered images once carried their producer number inside the
image (`Fig 4 — …`, `Fig 6 — …`). Uploaded under the presentation numbering in the table below, an
embedded "Fig 4" would have contradicted its own caption — producer `fig4_transfer` is presentation
Figure 3, and producer `fig3_holdouts` is Figure S1. The generators now emit a short descriptive
panel heading and **no figure number**; numbering is supplied by the caption system alone.
`tests/test_figure_exports.py` fails if a number is reintroduced into an image title.

| presentation | producer / file stem | placement | states |
|---|---|---|---|
| Figure 1 | `fig1_design` | **main** | study design and dataset roles |
| Figure 2 | `fig2_objective_surface` | **main** | finding 1 — weak separation |
| Figure 3 | `fig4_transfer` | **main** | finding 2 — a small observed gain over the level-only comparator that the analysis does not establish as useful |
| Figure 4 | `fig6_fraction_vs_endpoint` | **main** | finding 3 — temporal resolution localizes the rate |
| Figure S1 | `fig3_holdouts` | supplement | within-campaign cross-condition holdout detail |
| Figure S2 | `fig5_joint_residual` | supplement | in-sample shared-parameter compatibility |
| Figure S3 | `fig7_per_group_diagnostics` | supplement | per-group residual diagnostics |
| Figure S4 | `fig8_residuals_vs_conditions` | supplement | pre-fit residual structure |

---

## Main figures

### Figure 1 (`fig1_design`)

**Figure 1. Study design, observation operators, and evidence tiers.** The source model was calibrated previously to fraction-resolved multi-solute extraction kinetics from Schmieder et al. The present analysis maps its output to the matched 40 g Angeloni cup endpoint, profiles a target-specific solid-inventory level and a shared Sherwood rate multiplier on the optimal-grind (O) conditions, and then evaluates: leave-one-condition-out prediction within O; frozen O→coarse/fine (C/F) transfer within the Angeloni campaign; comparison to the campaign’s roasted-and-ground inventory assay; in-sample localization on the source fraction campaign; and an independent second-rig, time-resolved TDS trajectory from Waszkiewicz et al. Single-headed arrows show the actual data and parameter dependency, not analysis order: all four branches descend from the source calibration, and the external trajectory does **not** inherit the Angeloni recalibration — it freezes the source kinetics and profiles a target-specific level. Within the Angeloni branch the two holdouts are **parallel, not sequential**, because they use different calibration instances: the leave-one-condition-out analysis refits on eight of the nine optimal-grind conditions per fold and predicts the omitted one, whereas the cross-grind analysis fits all nine once and freezes that single calibration before any coarse/fine response is scored. The cross-grind holdout therefore does **not** consume the leave-one-condition-out output. The inventory assay connects by a double-headed link to the recalibration as an orthogonal same-campaign comparison, not as a dependency and not as a validation step after the cross-grind holdout. “Independent” refers only to the external campaign; the cross-grind and leave-one-condition-out tests share machine, coffee, and campaign context.

### Figure 2 (`fig2_objective_surface`)

**Figure 2. Profiled inventory–rate objective for Angeloni Arabica optimal-grind endpoints.** Both panels are **Arabica**: for caffeine and trigonelline, the model is evaluated at the nine Arabica O conditions (nine condition means per solute) using the matched 40 g endpoint operator. The corresponding Robusta panels, and the 5-CQA panels of both varieties, are reported in Supplementary Tables S1 and S2 rather than plotted here. At every tested Sherwood rate multiplier, the solid-inventory level is reoptimized and the unweighted concentration-scale sum of squared errors (SSE) is recorded; the surface is shown relative to its minimum. The curve marks the profiled optimum, the shaded band spans the defensible mass-to-volume bases for the orthogonal roasted-and-ground inventory assay from the same campaign — it is an illustrative basis range, **not** a quantitative model constraint, because the assay's volume basis is undefended and the model's own inventory basis is not independently anchored — and the local log-parameter Hessian diagnostic is reported at the numerical minimum to two significant figures. The 10%-above-minimum profile extends from approximately 0.4 to the upper tested rate boundary, so its upper extent is right-censored. The Hessian condition number and inverse-curvature coupling describe local objective geometry, not a confidence interval or statistical correlation, because no measurement likelihood is specified. Evidence tier: in-campaign practical-identifiability diagnostic.

### Figure 3 (`fig4_transfer`)

<!-- paper-a:transfer-caption:begin -->
<!-- paper-a:transfer-corpus schema=4 n_records=44 n_observations=132 manifest_sha256=fe46b65becbd5c421e929de3c4847eba0630e82bf08cc0c6856718cdd55907f8 -->

**Figure 3. Within-campaign cross-grind prediction after target-specific calibration.** For each variety–solute group, the inventory and Sherwood rate multiplier are fitted only to the nine optimal-grind conditions and then frozen while predicting the corresponding coarse and fine conditions at the matched 40 g endpoint. Panels compare observed and predicted concentrations by condition and summarize error by target grind. The comparator is an O-trained level-only constant: one concentration level fitted on O, with no temperature, pressure, flow, or kinetic response. The plotted comparison is the **complete held-out coarse/fine corpus**: 44 sample records × 3 named solutes = **132 observations**, including the 8 off-grid records. Pooled MAPE is **8.44%** for the mechanistic model versus **8.83%** for the constant, and the model has the larger absolute percentage error on **62 of 132** observations. A matched-grid subset of 108 observations is retained only as a **secondary sensitivity**, and is the support on which the same-(T,p) lookup comparator is defined; it is not the plotted headline corpus. Error bars/envelopes, where shown, propagate the declared discrete set of O-fit rates within 10 % of the minimum, not a continuous confidence region. Any clustered intervals shown are fixed-predictor dependence sensitivities, not calibrated confidence intervals. Evidence tier: within-campaign cross-grind holdout against a trained level-only comparator.
<!-- paper-a:transfer-caption:end -->

### Figure 4 (`fig6_fraction_vs_endpoint`)

**Figure 4. Rate-profile comparison across three evidence tiers.** Panels (a–c) compare empirical fraction-resolved profiles from the Schmieder calibration campaign with the same model’s simulated sampled aggregate and exact whole-cup endpoint for caffeine, trigonelline, and 5-CQA. Simulated exact-cup bands are mean ±1 SD across 20 random seeds and quantify Monte Carlo variability, not experimental uncertainty. Panel (d) profiles a target-specific level against an independent Waszkiewicz TDS trajectory; the shaded band spans declared time-alignment/first-bin choices, while the single integrated cup is **not estimable** — one scalar observation paired with one profiled level is matched exactly at every rate — and is therefore drawn as a flat reference line rather than as a zero-error curve, which would read as perfect prediction. The external trajectory has a shallow minimum near rate multiplier 0.4 with approximately 27% minimum MAPE. Evidence tiers are, respectively, in-sample source-campaign localization, same-model simulation, and independent external shape test; they should not be pooled as equivalent validation.

---

## Supplementary figures

### Figure S1 (`fig3_holdouts`)

**Figure S1. Leave-one-condition-out evaluation within the Angeloni optimal-grind design.** Each fold holds out one of nine temperature–pressure conditions within a coffee-variety × solute group, refits the target inventory and rate multiplier on the remaining eight conditions, and predicts the held-out concentration at the matched 40 g endpoint. Panel (a) compares observed and predicted concentrations; panels (b) and (c) show signed held-out residuals against temperature and pressure. Across two varieties and three named solutes, the analysis contains 54 held-out predictions. Reported resampling intervals are descriptive condition-level summaries of already-computed folds and do not repeat the nonlinear fit or remove fold dependence. Evidence tier: within-campaign cross-condition holdout, not independent-machine validation.

### Figure S2 (`fig5_joint_residual`)

**Figure S2. In-sample compatibility of a shared inventory–rate pair across grinds.** Residuals are shown by coffee variety, solute, and grind after fitting one shared solid-inventory level and one shared Sherwood rate multiplier to all included Angeloni conditions. The comparison reports the cost of sharing against separate per-grind fits and reduced level-only baselines, together with any rate-boundary flag. The shared mechanistic fit reconstructs the pooled data at approximately 6.4% macro-MAPE versus approximately 4.9% for separate per-grind fits; this is an in-sample parameter-sharing penalty, not held-out transfer. Evidence tier: same-campaign compatibility diagnostic.

### Figure S3 (`fig7_per_group_diagnostics`)

**Figure S3. Per-group residual diagnostics at the matched 40 g endpoint.** Each of the eight variety × observable groups contains nine Angeloni temperature–pressure conditions, all evaluated at the matched 40 g collected-mass endpoint. **Panel (a)** compares *blind* source-model MAPE — the model applied with no target-specific inventory adjustment — with MAPE after *matching* the orthogonal same-campaign roasted-and-ground inventory assay. Matching is possible only for caffeine and trigonelline, the two solutes the assay reports; the remaining groups are marked “NA” at the baseline rather than drawn as zero-height bars, which would read as zero error. Arrows mark whether matching improved or worsened each group. **Panel (b)** reports the model–data association of the corresponding response summaries **across the nine operating conditions**; this compares conditions and is **not** a temporal trajectory. Inventory matching improves one analyte and worsens another, so the residual cannot be interpreted as a pure inventory offset. Correlations are descriptive associations, not held-out skill measures, and with only nine conditions per group and eight groups they should be read as indicative rather than estimated with useful precision. Evidence tier: within-campaign diagnostic.

### Figure S4 (`fig8_residuals_vs_conditions`)

**Figure S4. Blind source-model residuals versus temperature and pressure before target-level fitting.** Signed residuals, `(prediction − measurement)/measurement`, are plotted for each coffee-variety × solute group across the nine optimal-grind conditions at the matched 40 g endpoint. Colour denotes variety and marker denotes solute. Group-level offsets motivate a target-specific level recalibration, but the plot does not show whether within-group temperature–pressure structure remains after that level is fitted. No uncertainty interval is implied by point density. Evidence tier: pre-fit source-to-target discrepancy diagnostic.
