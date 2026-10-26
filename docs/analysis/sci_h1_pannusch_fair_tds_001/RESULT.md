The simple fraction-mean baseline predicts best. Finite-rate Pannusch reduces
RMSE by **3.103 TDS percentage points (72.4%)** relative to its independently
calibrated equilibrium limit, but its error is **0.277 pp (30.6%) higher than
the baseline**. These rankings survive every declared cohort deletion,
numerical allowance and reporting-threshold variant. Prefer the baseline as
the conditional research comparator: finite-rate complexity has not earned a
predictive advantage over it. Practical adequacy remains unestablished.

G1 / NO_GOVERNING_PHYSICS_CHANGE / SOURCE_INTERNAL / CAMPAIGN_SEPARATED /
TARGET_EXPOSED. PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is one retrospective
absolute-TDS comparison, not a repeat of the historical normalized-share result.

| Arm | Mean shot RMSE, pp | Mean signed shot bias, pp | Mean absolute shot bias, pp |
|---|---:|---:|---:|
| B: training fraction means | 0.903168 | −0.054062 | 0.457757 |
| F: finite rate | 1.179901 | +0.516582 | 0.516582 |
| E: equilibrium | 4.282739 | −1.005647 | 1.005647 |

Each shot uses measured-vial-mass weights; shots within conditions and conditions
receive equal weights. Equal-shot aggregates coincide here. Absolute bias is
taken **before** averaging. All 72 windows in all 12 shots are supported in
every arm, with no coverage failures.

| Condition | B RMSE | F RMSE | E RMSE |
|---|---:|---:|---:|
| PRED-C01 | 0.778419 | 1.421603 | 4.689610 |
| PRED-C02 | 0.737467 | 0.987410 | 3.989389 |
| PRED-C05 | 1.097888 | 1.089794 | 4.191623 |
| PRED-C06 | 0.998898 | 1.220797 | 4.260333 |

F's nominal 0.0081 pp advantage over B in C05 is numerically unresolved.
Adverse conditions and fractions remain included. [SCORES.csv](SCORES.csv)
also reports every condition's signed and absolute biases; the
[figure](comparison.png) shows aggregate observed and predicted means.

The bounded P1 check reused the configured owner inventory and existing exposure
records: **no verified executable blind candidate in inspected scope**.
[HOLDOUT_MAP.csv](HOLDOUT_MAP.csv) retains unknown/unqualified records; unopened
copies and raw replicates beneath exposed summaries do not create blindness.
The corpus is not declared exhausted.

Original-source joins verify FIT-C09/C10/C11/C14/C15: 15 physical shots and
90 TDS windows; evaluation is PRED-C01/C02/C05/C06: 12 shots and 72 windows.
Fractions 1,2,3,5,7,10 retain individual measured masses, actual boundaries and
all gaps. Other FIT conditions and temperature/flow ramps are excluded.
Original MAT arrays, preprocessing code, RI/design workbook structure and sampled
training RI cells were inspected; qualified exports supply the analysis. Original
evaluation TDS was reconciled after freeze. [SOURCE.json](SOURCE.json) specifies
the inspection limits and identities.

Both mechanistic arms independently fit c_s0, K_ref and gamma to the same
balanced mass-weighted squared-error objective; inventory amplitude is profiled
analytically. F additionally fits A1/B1/A2/B2. The training-only local Jacobian
rule retained all seven permitted parameters (six nonlinear optimizer dimensions);
B1 lies at its lower bound, leaving six interior parameters. Local rank does
not establish global or physical identifiability. E has three parameters/two
optimizer dimensions; B has six means. Source geometry/closures and initialization
policy are shared. [CONFIG.json](CONFIG.json) fixes finite ranges and four starts
per arm; [PARAMETERS.json](PARAMETERS.json) retains every fit. All F starts agree
closely; E reaches distinct local minima. This is bounded optimization, not proof
of a globally best equilibrium model. No probabilistic priors, Sobol indices or
parameter confidence intervals were inferred.

N200 fitting and N800 prediction are disclosed. The conservative training-derived
F allowance is **0.121585 pp**, exceeding the frozen **0.05 pp** numerical target:
**numerical-budget compliance fails**. Refinement changes decrease; positivity,
conservation (8.6e−14 relative), time splitting (8.1e−13 pp) and independent
physical-coordinate integration (7.0e−12 pp) qualify. The allowance is an engineering
sensitivity, not a continuum certificate. Fine-grid training objectives and all
admissible-start checks are in [NUMERICS.json](NUMERICS.json).

Across all 12 whole-shot and four whole-condition deletions, including numerical
allowances, relative gains span **−0.5884 to −0.0349 (F/B)**, **−4.2254 to
−3.3896 (E/B)** and **0.6790 to 0.7678 (F/E)**. Thus numerical noncompliance
does not erase these resolved descriptive rankings. Training-admissible start
variation changes F's relative gain by less than 0.000007; this is not comprehensive
optimization uncertainty. Every one of the nine .75/1/1.25 threshold-factor
combinations retains worse/worse/large, including deletion/numerical variants
([THRESHOLDS.csv](THRESHOLDS.csv)). These bands are not practical acceptance gates.

Observed between-shot TDS SD spans 0.0080–1.9549 pp across 24 condition/fraction
groups at differing windows. Deletions are not CIs. Assay, calibration/recovery,
mass/boundary, training and campaign uncertainties remain unknown, not zero.
TDS is 100×solute/beverage mass; model conversion is 100*c_l/980. Shared
Q=flow_label/1000/980 retains unresolved physical label meaning. Predictions
condition on supplied windows/masses and programmed inputs, without evaluation
chemistry; they predict neither hydraulics nor complete-cup EY.

[Cameron](CAMERON.md) remains separately unresolved: D_S is intragrain diffusivity;
changing K_RATE alone is not full equilibrium. Reported ST≈.83/≈0 lacks a recovered
original receipt, priors, budget or CIs. Fig.5 reproduction/basis remains unresolved.

Cost: 437 objective calls, 12 local diagnostic calls, 416.1 s fitting/qualification/
prediction, plus 1.1 s source benchmark and 4.7 s independent pre-score replay;
repository QA is separate. One score; figure-only recovery after a missing optional
dependency. Originals, detailed predictions/logs and locators stay outside Git.
Derived aggregates retain Pannusch et al., Mendeley 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0. Historical results, production defaults and EWP pins are unchanged.

**Exactly one next task:** qualify Cameron's Fig.5 generating configuration and
D_S/source baseline, including geometry, inventory, physical EY and original GSA
receipt, before its complete diffusion/equilibrium comparison.
