# SCI-MD-MORONEY-TRANSFER-001 — executed result

**CALIBRATION_INADEQUATE.** All ten tested conservative transport/startup families
fail the deep-condition cumulative-delivery budget, including both deterministic
starts and all three coherent readout variants. Numerical checks qualify, and the
original-source observation contract is resolved. The central deep fits also
miss the outlet budget. Consequently this comparison does **not** independently
establish failure of deep-to-shallow transfer, or a mechanistic transfer advantage.
Do not prioritize EWP integration of this tested formulation on this evidence.
The executable analysis and qualified observations remain useful; any future
revision must address the demonstrated deep joint-observable mismatch before
making a transfer claim. No successor is executed or automatically authorized.

This result supersedes the earlier source-blocked preparation. That preparation,
its rejected pre-scoring review and accepted unscored closeout remain in Git and
the review directory as history. The supplied original PDF resolved the named
figure-object gate; missing experimental replicates and wetting history did not
prevent execution of the bounded conditional test.

## Decisions and numerical results

The pre-scoring review accepted 5 mg/g mass-weighted outlet RMSE and 1.0 dry-dose
EY percentage point maximum cumulative-delivery error as engineering budgets.
These are decision tolerances, not measurement uncertainty. Central results below
use each family's best **deep-only** start. No family is selected by shallow fit.
Outlet columns are mg/g; delivery columns are dry-dose EY percentage points.

| Candidate | Deep outlet | Deep delivery | Shallow outlet | Shallow delivery |
|---|---:|---:|---:|---:|
| dose_uniform_0 | 5.495 | 2.901 | 1.689 | 3.852 |
| dose_uniform_0.5 | 5.696 | 2.911 | 6.667 | 3.849 |
| dose_uniform_1 | 5.954 | 3.374 | 14.140 | 10.805 |
| dose_linear_0.5 | 5.635 | 2.880 | 3.681 | 3.665 |
| dose_linear_1 | 5.808 | 2.870 | 6.597 | 4.038 |
| hydraulic_uniform_0 | 5.388 | 2.985 | 2.871 | 3.085 |
| hydraulic_uniform_0.5 | 5.524 | 2.759 | 5.544 | 3.641 |
| hydraulic_uniform_1 | 5.762 | 3.362 | 8.514 | 5.155 |
| hydraulic_linear_0.5 | 5.551 | 2.940 | 4.019 | 3.496 |
| hydraulic_linear_1 | 5.772 | 2.907 | 5.251 | 3.967 |
| N_M | 6.128 | 4.249 | 8.702 | 11.073 |
| N_T | 6.128 | 4.249 | 8.762 | 6.477 |

All central mechanistic deep fits fail both budgets. Across the entire finite
family, including source readout, admitted starts and empirical numerical
allowances, deep outlet error spans 3.296–6.043 mg/g and deep delivery error
2.185–5.074 EY pp. Thus cumulative calibration failure is robust within the
frozen family, even where a perturbed outlet score passes. Optimizer convergence
is not calibration adequacy. Neither empirical baseline meets deep adequacy.

Shallow errors are descriptive conditional predictions because deep calibration
has failed. Their finite-family ranges including numerical allowances are
1.189–14.191 mg/g and 3.083–11.022 EY pp. Every mechanistic configuration fails
shallow cumulative delivery. Outlet adequacy changes with startup assumptions;
for example, central dose/uniform amplitude 0 versus 1 changes outlet RMSE from
1.689 to 14.140 mg/g. This substantial prediction sensitivity does not change the
overall CALIBRATION_INADEQUATE decision. It does not identify wetting physics.
Calibration inadequacy applies to this frozen bounded two-start procedure; it
is not proof that every admissible parameterization of these equations fails.

Eight families meet the **arithmetic** relative-gain margins against both N_M
and N_T in every declared readout/start instance. Dose/uniform/1 and
hydraulic/uniform/1 fail those margins. Because calibration and shallow delivery
adequacy fail, none earns the overall transfer-advantage claim. The baselines
also fail shallow adequacy; their failure does not rescue the mechanistic model
or establish an adequate empirical replacement.

| Decision | Disposition |
|---|---|
| Observation contract | QUALIFIED_FOR_DECLARED_USE |
| Fit-specific numerical qualification | PASS for all 120 mechanistic condition records |
| Deep calibration | CALIBRATION_INADEQUATE for all ten families |
| Shallow adequacy | Delivery FAIL throughout; outlet depends on startup; no independent transfer-failure inference |
| Material gain over N_M and N_T | Arithmetic margins recorded separately; no earned mechanistic advantage |
| Initialization/parameter sensitivity | Large trajectory variation; no overall decision reversal within declared family |
| EWP development | Do not prioritize integration of the tested formulation; no fitted constants/default promotion |

Central signed endpoint-delivery errors are +2.349 to +2.865 EY pp deep and
+3.085 to +4.438 EY pp shallow. N_M/N_T shallow endpoint errors are +6.617/+6.477
EY pp. All sampled outlets are beyond the declared mobile-volume wash-through
reference, so early RMSE is **not available**, not zero. Secondary post-wash RMSE
uses an unweighted point diagnostic and is explicitly different from the primary
mass-weighted score; every value is retained in `scores.json` and
`central_comparison.csv`. No unobserved outlet segment was reconstructed from a
line to zero. Signed near-zero observations and nonmonotone pot-derived readouts
are preserved without clipping, smoothing or target-fitted correction.

The full shallow outlet support is 11.80–287.60 g; pot support is 11.42–287.88 g.
Deep supports are 21.68–985.81 and 21.96–985.63 g respectively. N_M extrapolates
beyond its dose-scaled deep support above 205.377/205.340 g (outlet/pot), shown in
the figures. N_T extrapolates below the earliest deep observations: shallow
outlet starts at 2.934 s versus deep 5.390 s, and pot at 2.839 s versus 5.460 s.
Its upper endpoint (about 71.6 s) remains within the deep upper extent (about
245 s). These early N_T extrapolation regions correspond to masses below
21.68 g in Figure1 and below 21.96 g in Figure2. No difficult target region
was removed.

## Source contract and interpretation

The original 19-page Moroney2015 PDF has SHA256
`896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8`.
Original vector objects and page renders were inspected independently for Fig3
(printed page219, PDF index3) and Fig11 (page233, index17). All 120 selected raw
rows match distinct plotted marker subpaths. Accepted observations are **44 deep**
(22 pot + 22 outlet) and **28 shallow** (14 + 14). Excluded are **44 duplicate
deep points** in Fig11 and **four confirmed legend symbols**, data rows 7, 33,
45, 71 at approximately (189.87,206.498), (190.06,161.812), (179.87,201.501),
(180.05,156.815), in g and mg/g. Those markers sit inside legend boxes beside
series labels. The full 292-row mapping also retains 44 out-of-scope Cimbali
Fig3 observations as excluded and 84 fitted model-line / 44 duplicate Fig7
coordinates as reference-only. These are not additional experimental folds; the
120-object audit is restricted to the selected JK Fig3/Fig11 panels. Fig3 has no
analogous selected-panel contamination. Raw CSVs are
unchanged. `qualified_rows.csv`, `source_objects.json` and the independent
[source audit](review/source-audit.md) retain exact source hashes, row/object
identities, coordinates and exclusion evidence. MEASURED denotes plotted-coordinate
extraction, not certainty that every object is an observation or zero error.

Deep outlet is the primary calibration observable; deep pot-derived cumulative
mass is its dependent mass constraint. Shallow concentrations, endpoint yield,
initial amplitude and time shift never enter fitting or prediction construction.
Only shallow geometry, source operating metadata and sampling masses enter before
freeze. Fig7 fitted lines are reproduction references; later papers and blue
Fig11/12 curves add no independent experiments. Tables supply qualified measured,
nominal, derived or fitted inputs as distinguished in the protocol. No other
source family was reopened; catalog references are not claimed as inspected data.

The observer uses S_out[g]=M[g]*c_pot[mg/g]/1000 and
C_exit[kg/m3]=965.3*c_exit[mg/g]/1000. Source rho=965.3 kg/m3 and prescribed
Q=250 mL/min give 4.02208333 g/s. This is first-outflow/post-fill time, not pump-on
or first-contact time. Fig3/Fig7 duplicate conversion discrepancies are retained
as readout sensitivity, not a shallow-fitted density. Reported doses are as
received with approximately 4% moisture: 60/12.5 g become 57.6/12.0 g dry.
Ymax=.143435/.44=.325988636 of dry dose (31.2949% as received), giving initial
inventories 18.77695/3.91186 g. Delivered mass, retained mobile/internal liquid,
remaining surface/kernel solid and losses remain separate. Kernel solid is zero
under the declared post-fill dissolved-kernel assumption; modeled losses/inflow
are zero. No independent pot amplitude is fitted.

This is the conservative 2015 saturated advection reduction, not the 2019 LDF
model. The printed Eq59 same-sign exchange inconsistency is explicitly disclosed
in the protocol: internal exchange uses the opposite mobile sign, as required
by conservation and the existing batch implementation. This is not an
author-confirmed erratum. Dose-based and hydraulically conditioned storage
volumes remain distinct formulations; inferred porosity is not measured or a
permeability-law validation. Total source inventory is fixed in both conditions.

## Numerical, sensitivity and execution evidence

Every admitted configuration uses 480/960/1920 cells plus tightened 1920-cell
integration. Maximum adjacent-finest/tight observed outlet difference is
**0.135206 mg/g**, delivery difference **0.059658 EY pp**, below 0.5/.1 budgets.
Maximum relative solute-balance residual is **6.2024e-10**, below 1e-6. The
smallest mass state is -1.704e-12 kg, within the explicitly declared 10-atol
roundoff allowance; no clipping was used. These refinement differences are
empirical sensitivities, not proven continuum error bounds. All coarse-grid and
pointwise startup differences remain in `numerics.json`.

The reservoir audit replayed all 120 frozen mechanistic condition records,
with **zero trajectory difference** and no target-concentration reads. Separate
reservoir masses at each observable's support and time zero are retained in
`inventory_audit.json`, whose SHA256 is
`2105ae409413e57e0fc512a7a951e039b22e1e3ea5967f8b21973af88f445117`.
Initially dissolved mobile solute is debited locally from surface inventory;
internal dissolved mass is debited from kernel inventory. No budget repair or
hidden dose normalization is used.

Thirty mechanistic family/readout calibrations and three empirical calibrations
used **66 deterministic starts**, all successful and admitted; no integration
failures. Five lower-readout starts hit the lower alpha bound .01 and remain
recorded. Across admitted mechanistic fits alpha spans .0100–.2034, beta
.02818–.04644 and surface split .7011–.8123. These are conditional fitted
multipliers, not independently measured diffusivities. Central empirical widths
53.816/53.918 g nearly coincide; the two-exponential decomposition is weakly
identified. Both starts and all parameter records remain available. No post-score
bound, optimizer-start, model, threshold or initialization expansion occurred.
The finite source/start family is not exhaustive uncertainty or experimental
confidence, and digitized points are not independent replicates.

Calibration used 4,827 mechanistic solves / 5,566,821 RHS evaluations and 359
empirical objective calls. Prediction/refinement used 480 solves / 930,702 RHS
evaluations. Fit plus prediction took 1,512.729 s; the inventory audit added 120
solves / 239,741 RHS evaluations / 125.143 s. Total B inference plus audit:
**5,427 solves / 6,737,264 RHS evaluations**, with no failed integration.
Python3.12.3, NumPy2.5.3, SciPy1.18.1 are frozen; dependency locks are unchanged.

The separate A published-configuration control used three solves / 5,011 RHS
evaluations / 1.841 s and its own 17.99517 g initial budget. At 1920 cells its
RMSE against the **fitted Fig7 model line** is 2.49885 kg/m3, maximum difference
13.13758 kg/m3. It is a descriptive reconstruction, not an exact reproduction,
calibration target or transfer evidence. No cause for its mismatch is uniquely
assigned, and its initial state was never substituted into B.

## Reproduction, reviews and artifacts

The [protocol](PROTOCOL.md), [commands](REPRODUCE.md) and [environment](environment.json)
make the analysis executable. Scientific freeze SHA256 is
`39ff2ff62c77879bfd5640217406f4b85c2c9e683f3bf5129e27c3c22b6ba067`.
Independent [pre-scoring approval](review/pre-scoring-review.md) binds that
freeze and original base before any real calibration. All 144 prediction records
were hashed before target attachment: prediction-freeze SHA256
`69eb224f51112e036bbf1cbbe17e554a4741c61259cd037d28f28191913868d8`.
The one-time score SHA256 is
`b2f6d23be2ab56a64b10570e5429090bcb5155af01c5ba62c9bed6dd6caf4ab1`;
[decisions](results/decisions.json) SHA256 is
`96c04a03d65e0a51091503fcb63bc5d60c92bc20f518f4f5d48b1caa5b0470dd`.
Reporting consumes these immutable files; it cannot refit or change predictions.

[Outlet curves](results/figure1.png), [cumulative delivery](results/figure2.png)
and [consequential sensitivity](results/figure3.png) distinguish observations,
source fitted references and conditional predictions. Their VizSpecs carry the
same-source exploratory claim ceiling. Ranges are finite sensitivities, not
experimental confidence bands. Full records are `calibration.json`,
`predictions.json`, `numerics.json`, `scores.json`, `decisions.json`,
`inventory_audit.json`, `central_comparison.csv` and `summary.json` under `results/`.

Local Puckworks quick suite: **4,617 passed, 33 skipped, 65 deselected** in
1,043.52 s; focused solver/observer/source/leakage/reporting plus historical
Moroney tests: **28 passed** in 7.41 s. Registry gates: 65 PASS + 1 ACK_EXCEPTION.
Ruff passes. Tests include analytic conservation/advection/exchange limits,
invalid-state rejection, dependency tampering, shallow-value leakage and a fully
synthetic fit/freeze/score/report path. The full quick run began before the two
reporting tests were added; those tests passed in the focused run. Independent
final scientific review and exact-head CI are recorded with the open linked PRs
and the [independent final result review](review/final-result-review.md); pending
checks are not represented as completed.

Original bases/trees are in `identities.json`; the EWP handoff binds the final
producer commit/tree separately from its unchanged production lock. This is
retrospective same-source model development, not blind validation, independent
replication, population inference, unique mechanism identification or espresso
physical validation. PHYSICAL_VALIDATION remains NOT_ESTABLISHED. Native
builds/integrations, production/default/public-interface/registry promotions,
dependency-lock changes, new experiments, author contact and successor execution:
**all zero**. PRs remain OPEN and UNMERGED.
