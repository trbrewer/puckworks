# Private-chain aggregate results — 2026-10-28

The four aggregate rows below are copied exactly from the owner's local
`puckworks_private_results_summary.md`. No analysis was rerun for this publication.
All analyses are retrospective and target-exposed; intervals omit important
measurement, selection and new-population uncertainty. Judgements concern the
named contrasts, not practical adequacy or physical validation. “Blocked” means
the ranking cannot be resolved; computation completed. No practical
tie/equivalence is established.

**Metric:** #381/#382/#384: equal-coffee log RMSE; #383: balanced mean
mass-weighted shot RMSE (mg/g). **Δ A/B = loss(A) − loss(B); negative favours A.**
Brackets are paired conditional 95% intervals.

| Task / PR | Question | Arms: primary metric | Contrast: Δ [95% interval] | Repository verdict; judgement | Aggregate publication? |
|---|---|---|---|---|---|
| SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001<br>#381 | Does calibrated percolation beat empirical radius scaling across coffees? | W3 0.501988; E3 0.637759; N 0.688707 | W3/E3: -0.135770 [-0.799868, -0.009126]<br>W3/N: -0.186719 [-0.406336, 0.575132] | W3_LOWER_CONDITIONAL_LOG_LOSS<br>**clear win versus E3 only; versus N unresolved** | yes — CC BY 4.0 table; attribution and changes |
| SCI-MD-WADSWORTH-MEASURED-SURFACE-PERMEABILITY-001<br>#382 | Does measured surface outperform radius for held-coffee permeability? | S3 0.154177; E3 0.637759; W3 0.501988; N 0.688707 | S3/E3: -0.483582 [-1.641002, -0.249074] | S3_LOWER_CONDITIONAL_LOG_LOSS_THAN_E3<br>**clear win for S3 in log loss; absolute preference unresolved** | yes — CC BY 4.0 table; attribution and changes |
| SCI-MD-TRIGONELLINE-RECIPE-CAMPAIGN-TRANSFER-001<br>#383 | Do recipe features improve trigonelline prediction across campaigns? | R18 0.139577; Q18 0.145199; D0 0.134550; K0 0.729503 | R18/Q18: -0.005622 [-0.016809, 0.009933]<br>R18/D0: +0.005027 [0.000153, 0.013193] | RECIPE_MASS_COMPARISON_UNRESOLVED; RECIPE_NOT_SELECTED<br>**clear loss versus D0; Q18 comparison unresolved** | yes — CC BY-NC 3.0; noncommercial with attribution |
| SCI-MD-WADSWORTH-PERCOLATION-KC-TRANSFER-001<br>#384 | Does calibrated percolation outperform Kozeny–Carman across coffees? | PER1 0.269076; KC1 0.243713; N 0.688707; S3 0.154177 | PER1/KC1: +0.025363 [-0.000113, 0.073089] | CALIBRATED_SHAPE_COMPARISON_UNRESOLVED<br>**blocked — shape ranking unresolved** | yes — CC BY 4.0 table; attribution and changes |

**Arms:** W3 = calibrated percolation; E3 = empirical radius/porosity;
S3 = empirical surface/porosity; N = constant. PER1/KC1 = one-coefficient
percolation/Kozeny–Carman. D0 = mass-shape model; R18/Q18 add recipe/quadratic-mass
features; K0 = constant.

## Source attribution and licence notes

**Wadsworth (#381, #382, #384):** Fabian B. Wadsworth et al. (2026),
[A model for the permeability of coffee pucks validated using X-ray computed
micro-tomography](https://doi.org/10.1098/rsos.252031), *Royal Society Open Science*
13, 252031, Table 1. © 2026 The Authors;
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes made by Puckworks: the existing Table 1 transcription was used for
retrospective held-coffee model fitting and comparison, producing aggregate
losses, differences and conditional uncertainty intervals. These derived results
are rounded for display in the local summary and copied unchanged above.
The Wadsworth-derived rows retain CC BY 4.0 attribution.

**Trigonelline (#383):** Verena Pannusch, Benedikt Schmieder, Lara Vannieuwenhuyse,
Mirjana Minceva and Heiko Briesen (2023),
[Mendeley Data repository for the model-based espresso brewing control chart,
version 1](https://data.mendeley.com/datasets/y2tz67f6ry/1),
DOI [10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1).
Source licence: [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/).
Puckworks derived the retrospective campaign-transfer aggregate comparison;
the displayed row is copied unchanged from the local summary.
The trigonelline-derived row retains attribution and **non-commercial** use
under CC BY-NC 3.0; it is not relicensed under the repository's code licence.

This file contains aggregate results only; no source rows, figures or private
bundles are redistributed.

## Results held privately

| Task | Repository verdict | Availability |
|---|---|---|
| SCI-MD-POCKETSCIENCE-CUP-TDS-001 | M_CONDITIONAL_RESEARCH_REUSE | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-POOLED-SCALING-001 | POOLED_SCALING_CONDITIONALLY_BETTER | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-CROSS-BASKET-TDS-001 | P_TRANSFER_ADDED_VALUE_OVER_N | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-CROSS-STYLE-TDS-001 | P_CROSS_STYLE_ADDED_VALUE_OVER_N | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-CROSS-DISPERSION-TDS-001 | CROSS_DISPERSION_COMPARISON_UNRESOLVED | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-AFFINE-TDS-001 | M_LOWER_THAN_AFFINE | numbers held privately pending source permission |
| SCI-MD-POCKETSCIENCE-GRUDEVA-WINDOW-TDS-001 | N_LOWER_WINDOW_TRANSFER_LOSS | numbers held privately pending source permission |
| SCI-MD-PERTICARINI-HELD-COFFEE-TDS-001 | DURATION_PRESSURE_COMPARISON_UNRESOLVED | numbers held privately pending source permission |
