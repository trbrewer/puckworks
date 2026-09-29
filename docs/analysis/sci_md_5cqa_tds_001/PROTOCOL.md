# Early-TDS-conditioned 5-CQA interval delivery

SCI-MD-5CQA-TDS-001. G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
The owner authorizes bounded implementation, FIT development, independent exact
pre-score review and one evaluation. No second execution authorization is needed.
No production adoption, merge, new acquisition, laboratory work, solver run,
production default/dependency-lock change, EWP edit or successor search.
This protocol and its model/source bindings must be committed before real fitting.

## Decision and prior authority

NEW_INFORMATION: an untested information-set/model-capability pairing, a
5-CQA-specific composition head over unchanged 006 C2, with early TDS inputs.
Existing observations acquire these task-local roles; no new experiment is implied.
DECISION_IF_POSITIVE: retain the adequate research arm and separately identify
whether added composition complexity earns replacement under fixed budgets.
DECISION_IF_NEGATIVE: reject only the tested new families on qualified primary
evidence and end this task. DECISION_IF_NULL_OR_BLOCKED: retain any adequate
simpler arm or name the exact unresolved dependency/numerical/support/review cause.
GRINDER_TO_CUP_LINK: interval analyte delivery from early measured mass and TDS
without a query-time 5-CQA assay. REPEATED_BLOCKER: inventory/closure is not this
observable-prediction question. LOWER_COST_ALTERNATIVE: analytical S0 and frozen
mass-only E0/D0 controls; Python only. All three selection tests pass within the
owner-selected lane; no replacement task is selected.

Fetched main equals each reviewed authority: Puckworks 7df8db644ad0cfd08866bf91565e3d80445e046c;
EWP f15a417cbf3c7528ac734537bb844cab6dc98287. No later scientific overlap was
found in main or open PRs. #297 tested mass-only 5-CQA E0/D0 and failed every
primary condition. #290 tested caffeine with caffeine-specific coefficients and
budgets. #288 predicts TDS, not 5-CQA composition. #296 is unrelated and closed.
This is not first-ever 5-CQA modeling, new kinetics/transport, H1 confirmation,
or evidence isolating a causal TDS effect relative to historical E0/D0.
Both S1 and S2 receive early TDS through C2; S2 versus S1 tests its additional
use in the composition head. The owner's preselection rank-5 input check
demonstrates nonredundant inputs, not full coefficient identifiability.

## Source and information contract

Resolve PANNUSCH2024_MENDELEY_FULL_REPOSITORY through the established resolver.
SOURCE_IDENTITIES.json preserves the eight originals and ten register identities
from 5CQA-DELIVERY-001. Use that task's campaign-specific HPLC reconstruction,
MATLAB cAlcaloids(:,3), HPLC column Y/area I; never CQA_sum or another isomer.
FIT formula: (I-78.923)/(24.513*1000)*dilution*sample_mass_g;
PRED: (I+88.067)/(26.383*1000)*dilution*sample_mass_g, producing mg/fraction.
Reconcile original concentrations against the rounded public exports. Fit/score
original unrounded qualified concentrations. Use original masses and original
TdS(1:2)/100, joined through the caffeine task's exact campaign/shot/fraction
projection. HPLC spills do not exclude independently qualified TDS.

Inputs are m1,m2 in kg and q1,q2 in kg/kg; queries are cumulative beverage kg.
Only later fractions 3,5,7,10 supervise heads. Original cumulative mass includes
intervening unassayed vials. Never fill prefixes, use nominal-flow mass, clip
observations, impute chemistry, or exclude by target/prediction error.
Keep original designs and physical replicates together. Pannusch/Schmieder are
one shared lineage; lot and roast batch remain unknown.

FIT: 15 designs, 45 shots, 180 intended slots, 177 supported; preserve the three
missing-prefix slots. PRED primary C01/C02/C05/C06: 12 shots, 48/48 windows;
temperature C03/C04: 6 shots, 24/24; flow C07/C08: 6 shots, 23/24, all 24 retained.
No PRED later chemistry enters initialization, transforms, domains, fitting,
lambda selection or prediction. Silent original/formula/validity integrity
checks emit no values and influence none of those choices.

## Immutable parent and fixed models

DEPENDENCIES.json binds frozen predecessor modules/models and source contracts.
Final C2 file SHA-256 c0e38da25edf5441b88f444e3270b5b83f2ea94773fc09048009a691ac7c230e;
semantic SHA-256 960e0c7dd37d3ba876f95a44c00c69f222e53c022a641e4b092a2af686fb9516;
runtime SHA-256 4fb20dd42e0ed7d5a758f549d616131988a1dab05ddc49b9253441606f155e33.
Retained 006 freeze SHA-256 54d5afb2a5dc938f9d9efce88bc6a511f8984837ebd583eae9eea9c4db96a7b3.
Require all fifteen development/C2.0.0001.{group}.model.json files using the
existing retained-parent verifier: hashes, source/training projections, excluded
held design/shot IDs, transforms, domains and complete matrix. Both head training
and held prediction use that fold's excluded-design parent. Only final head
fitting and March inference use final C2. No parent optimizer, refit, lambda
reselection or replacement; missing archive means BLOCKED_DEPENDENCY.

Report five arms. E0/D0 load unchanged frozen 5CQA-DELIVERY-001 artifacts and
their unchanged mass-only contract; inference replay must agree with retained
predictions where available. Never invoke their historical scoring command.
For new arms T(b|x) is C2 concentration and q5 is 5-CQA concentration:

- S0: q5=r*T, one fitted r in [0,1].
- S1: q5=T*sigmoid(sum_j H_j(b)*theta_j dot [1,z_m1,z_m2]); 15 coefficients.
- S2: q5=T*sigmoid(sum_j H_j(b)*theta_j dot [1,z_m1,z_m2,z_q1,z_q2]); 25 coefficients.

Five uniform inherited knots over [0,parent domain]; piecewise-linear logit hats.
Reuse serialized fold-parent means/ranges, mass scales .01 kg and TDS scales .1.
Every coefficient is bounded [-20,20]. No moved/extra knots, interactions or
feature search. Head upper support=min(parent domain, largest qualified head
training endpoint); final upper bound <=0.06971540000000001 kg. Anchor=m1+m2.
The share constraint is an assumption, not measured chemical closure. 5-CQA
already belongs to TDS; never add it as independent dissolved-solids mass.

M5[a,b]=integral_a^b T(u|x)*share(u|x) du, the pointwise product, never separately
averaged factors. Internal units are kg beverage, kg analyte and kg/kg.
analyte_mg=1e6*M5; interval_mg_g=1000*M5/interval_beverage_kg.
No query-time 5-CQA, caffeine, trigonelline, future TDS, temperature, flow,
pressure, time, recipe, inventory or fitted shot-specific correction.

## FIT development and numerical qualification

Fifteen whole-design leave-one-out folds. Equal design weight; equal physical-shot
weight within design; measured interval-mass weights within shot. Identical
coordinate-derived held support across S0/S1/S2, retaining all original slots.
S0 analytical weighted least squares: r=clip(sum(w*Tbar*y)/sum(w*Tbar^2),0,1).
Preserve numerator, denominator, unconstrained r and boundary/result status.
Zero/nonfinite denominator fails, without fallback. At most 16 scalar fits.

S1/S2 lambda grid exactly [.0001,.01,1,100]. Objective: weighted squared
concentration residuals divided by .25 mg/g, plus lambda times the sum of
mean(theta[:,1:]^2) and mean((second knot differences/.25^2)^2).
Exactly three starts, zero feature slopes, intercept=logit(clip(weighted training
5-CQA concentration / weighted predicted parent TDS concentration,1e-8,1-1e-8))
plus -1,0,+1 times linspace(-1,1,5). Clipping is initialization-only.
SciPy bounded least_squares: trf/exact, linear loss, 2-point Jacobian,
diff_step=1e-6, x_scale=1, ftol=xtol=gtol=1e-10, max_nfev=8000, with independent
actual-call accounting including numerical Jacobians and a hard 8000-call cap.
Choose lowest finite converged objective, ties by start order; no rescue starts.
Choose largest lambda within 1e-6 mg/g of minimum balanced held-design RMSE
among candidates with every required fold selectable. Conservative RMSE bounds
must prove that selection is unchanged; otherwise numerical selection is unresolved.
Final fits use all qualified FIT and final C2. Development is selection, not
unbiased nested validation: C2 and its hyperparameter have prior selection history.

Inherited knot-split 64/128-point Gauss-Legendre and independent adaptive quad,
epsabs=1e-14 kg, epsrel=2e-13, limit=200. Allowance is the maximum of 64/128
discrepancy, each adaptive discrepancy plus adaptive error, plus
128*machine_epsilon*(width+abs(I64)). Only fraction-3 shared-anchor reconciliation
within four ULPs is allowed; preserve original coordinates and add twice the
displacement. Total allowance <=1e-9 kg per interval. No broad mass tolerance.
Reject nonfinite, reversed, before-anchor and out-of-domain intervals. Zero width
returns zero mass and undefined concentration. No accuracy confidence is implied.

## Frozen evaluation and decisions

Produce all 5*96=480 records before the single outcome join, including unsupported
slots/reasons. One clean committed exact freeze and one genuine independent audit
precede scoring; the implementer cannot approve itself. If review is unavailable,
stop READY_FOR_INDEPENDENT_REVIEW. One exclusive durable score-start receipt
precedes outcome attachment; failed/completed receipts prevent another score.
One bounded material pre-score correction is permitted under the existing policy;
no extra experiment budget. A scientific defect after score invalidates the
affected result and requires STOP. Reporting-only changes use retained scores.

Per physical shot e=predicted-observed mg/g, w=measured interval beverage mass:
R=sqrt(sum(w*e^2)/sum(w)); B=sum(w*e)/sum(w). Conditions average R and abs(B)
over three original shots; primary summaries equally average four conditions.
Never take abs after averaging signed shot biases. Every primary condition must
have R<=.25 mg/g and mean abs(B)<=.125 mg/g, with complete qualified support.
Each complexity comparison S1/S0, S2/S1, S2/S0 requires candidate primary adequacy,
balanced R reduction >=.05 mg/g AND >=15%, definite R improvement in at least
3/4 primary conditions, and balanced absolute-bias deterioration <=.025 mg/g.

Propagate interval allowances to concentration, shot R by weighted L2, B/abs(B)
by weighted L1, then equal-shot/condition averages. Difference allowances add;
relative gain uses candidate<=.85*reference including both allowances. PASS uses
conservative favorable bounds; definite violation FAIL; threshold overlap
UNRESOLVED. No rounding into PASS. These are research engineering budgets,
not assay uncertainty, health or sensory limits. Secondary panels cannot rescue
primary failure; incomplete flow has only explicit supported-subset diagnostics.

Report separately arm adequacy, each complexity decision, least-complex adequate
new arm, and any more-complex adequate arm earning replacement. S2 earns replacement
only if both S2 comparisons pass; S1 requires S1/S0. Labels distinguish
CONSTANT_SHARE_FIVE_CQA_ADEQUATE, MASS_CONDITIONED_SHARE_INCREMENT_EARNED,
TDS_CONDITIONED_SHARE_INCREMENT_EARNED and ADEQUATE_INCREMENT_NOT_ESTABLISHED.
Only definite failure of all new arms with qualified complete primary evidence
permits TESTED_TDS_CONDITIONED_FIVE_CQA_FAMILIES_INADEQUATE. Missing models,
numerical failure, support loss or threshold overlap receive specific
NOT_ADJUDICATED causes. Historical E0/D0 are reported separately.

## Limits, publication and reproduction

Task start 2026-09-29 01:09:49 UTC; hard deadline 2026-09-29 07:09:49 UTC.
New task clock; no predecessor deadline reuse. At most 183 iterative starts per
S1/S2, 366 total; 16 analytical S0 fits; zero parent/E0/D0 fits. One worker,
one BLAS thread, 60-minute total fitting-stage span, 12-GiB process memory cap,
5-GiB cumulative private task evidence. Durable starts, actual calls, incomplete
attempts and cancellation records persist; a new directory cannot reset budget.

CLI: prepare --parent-evidence; develop (grouped development plus final fits);
freeze (outcome-free inference and exact freeze); score --review; verify (saved
inference/identities, no fit/rescore); report (retained scores only).
Strict typed inputs, immutable states and species/hash/unit-checked serialization.
remaining_5cqa(stop_mass_kg) integrates from the anchor: modeled delivery, not
inventory or a measurement of unassayed beverage. Runtime requires saved models
and verified sibling numerical code, no optimizer, source workbook or network.

Run focused numerical/source/firewall tests, normal repository gates, registry,
lint/type, generated-state, historical-preservation, shell/JSON and secret/path
checks. Pending hosted CI is not PASS. Publish compact derived/model artifacts,
commands, review, all decisions and handoff on one task branch and at most one
draft Puckworks PR. EWP stays unchanged. Originals, individual observations and
predictions, and detailed logs stay outside Git. Source-derived artifacts retain
Pannusch/Schmieder attribution, Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0,
separately from software licensing.

SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION /
PHYSICAL_VALIDATION_NOT_ESTABLISHED. No fresh blind, independent, external or
universal validation, sensor/controller, whole-cup measurement, inventory closure
or mechanistic conclusion. Positive and negative completed results both end this task.
