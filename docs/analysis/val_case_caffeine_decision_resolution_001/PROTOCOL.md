# VAL-CASE-CAFFEINE-DECISION-RESOLUTION-001 protocol

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL; existing evidence class EXPLORATORY.
Owner authorizes this separate retained-evidence reduction, not reopening the
once-only scoring lifecycle. Historical outcomes were read before this freeze;
this is neither blind nor independent validation. Completes one T04 case and
caffeine-specific T02 interpretation only. No automatic successor.

## Frozen population and admission

S2 remains primary; D0, S0, S1 remain all comparators. D0 uses early measured
masses without TDS or C2; S0 uses a constant share of frozen C2; S1 uses mass
context and early TDS indirectly through C2; S2 adds composition conditioning.
S2 versus S1 is additional composition conditioning, not TDS versus no TDS.
Use canonical identities in the bound records: PRED-C01/C02/C05/C06 primary,
PRED-C03/C04 temperature, PRED-C07/C08 flow, three physical shots per condition,
fractions 3/5/7/10. Thus 12/6/6 shots and 48/24/24 intended windows per arm.
All 96 source caffeine observations are valid; prediction support is 95/96.
Retain OUTSIDE_COMMON_TRAINING_MASS_DOMAIN and identify its fraction only from
an admitted crosswalk. Early caffeine spills do not exclude later targets.
45 FIT shots / 15 designs remain training. Pannusch/Schmieder share lineage.

Read only the configured caffeine-delivery-001-evidence/run-001 locator and its
recorded references. INPUT_MANIFEST.json fixes byte commitments. Bound shot
statistics suffice for paired sensitivity; scores may be the identical public
RESULTS.json. Verify completion/receipt/freeze links, model-content versus file
hashes, canonical membership, duplicates, units, finite values, nonnegative
allowances, complete versus subset support and original aggregates. Admit
optional bound observations, predictions, queries and coordinates independently.
No source workbook is required unless retained records leave a material mapping
question. No archive census, host requalification or new acquisition.

Missing evidence is component-specific: shot-to-condition/panel reproduction,
fraction-to-shot reconstruction, primary sensitivity, temperature sensitivity,
source-observed variability. Missing raw observations do not invalidate bound
shots. Hash mismatches block only affected reliance, never replacement inputs.
Do not reconstruct shots from public means or generate missing predictions.

## Arithmetic and historical mapping

JSON numbers remain binary64; preserve full precision until display. Match the
original NumPy weighted dot/square-root and mean order, conditions in frozen
panel order and shots in retained order (validate canonical membership).
Record original/reproduced values and exact decisions side by side. Reconciliation
allows at most 512 ulps at max(1,abs(original)) for arithmetic only (MASS utility);
report the maximum and every nonzero discrepancy separately. No tolerance applies
to statuses, identity, thresholds, comparisons or hashes.

For fraction reconstruction e=retained caffeine_mg_g - 1000*q (q kg/kg),
w=observed mass_kg / sum(mass_kg). Shot R=sqrt(w@e²), B=w@e, absB=abs(B).
Use retained concentration even when integration_start differs from original b0.
Use total retained allowance_kg once: u=1000*allowance_kg/observed mass_kg;
u_R=sqrt(w@u²), u_B=u_absB=w@u. Mean each shot metric/allowance within condition,
then equally mean conditions. Never pool fraction errors, average percentages,
cancel shot biases before abs, or weight conditions by remaining shot counts.
Keep signed-bias and actually-assayed-window mass-error metrics separate.

Historical upper(v,u,t): missing => NOT_ADJUDICATED_INCOMPLETE_SUPPORT;
v+u<=t => PASS; v-u>t => FAIL; otherwise NUMERICALLY_UNRESOLVED.
Adequacy requires every primary condition R<=0.50 and mean absB<=0.25 mg/g.
Conjunction: FAIL first, then all PASS, then incomplete before unresolved.
Incomplete-condition lower bounds use complete shots only, nonnegative R/absB
minus allowance, divided by original three; these can establish FAIL. Preserve
C07's actual result. No new equality convention or precision ceiling.

B/C/D compare S2 with S1/D0/S0 on complete original primary support. Each requires
absolute balanced gain >=0.10 mg/g, relative gain >=15%, >=3/4 definite condition
wins, and abs-bias deterioration <=0.05 mg/g. Relative test is
upper(C-0.85*R,u_C+0.85*u_R,0), forced FAIL if R-u_R<=1e-12. Otherwise report
(R-C)/R and 1-(C+u_C)/(R-u_R). Definite wins C+u_C<R-u_R; possible wins
C-u_C<R+u_R include definite wins. Count PASS at >=3 definite, FAIL at <3
possible, else unresolved. Existing accepted helper is unchanged; use its
compatible interval/sensitivity operations and a case-local historical adapter.
Policy wording v1-proposed is preserved; PR #335 merge is acceptance authority.

## Fixed perturbations and public summaries

Primary: baseline plus each of 12 physical-shot deletions exactly once.
Temperature: baseline plus each of six deletions exactly once. Delete the entire
trajectory and same identity across all arms; keep all original conditions,
affected condition mean over two remaining shots, others over three, then equal
condition weights. Propagate allowances through that hierarchy. Each scenario
retains its actual 11- or 5-shot membership and exclusions privately. No fits,
reconditioning, prediction, condition deletion, fraction deletion, bootstrap,
p-values, confidence intervals, equivalence tests or additional search.

For each S2/reference comparison retain every paired shot and condition
contrast, baseline and deletion: gain g=R_ref-R_S2, u_g=u_ref+u_S2; relative
point and conservative lower gain; absB deterioration and summed allowance;
signed B difference; definite/possible condition accounting and signed continuous
headroom to historical components. Deletions are diagnostics without replacement
A/B/C/D verdicts. Report baseline, deletion-only min/max, positive/zero/negative
counts and scenario-specific allowances privately. Public aggregate envelope is
[min(g-u_g),max(g+u_g)] over baseline plus all declared deletions, each with its
own allowance. Separately answer strict positivity of all deletion points and
all deletion lower endpoints; equality is not positive. Give corresponding bias
and relative-component ranges/envelopes. A helper sensitivity record has the
finite scenario-set estimand with scenario membership explicitly mapped privately;
it is never given original complete-population scope or treated as a bound.

Flow: reproduce incomplete full scope and original supported-subset reduction,
retaining all six shots and both conditions, with paired baseline diagnostics.
No flow deletions, no dropping the incomplete shot to manufacture completeness.
Preserve all C08 flags, adverse C02/C05 versus S1, C05 versus D0, and D0's
better stress RMSE where reproduced.

## Observation variability, claims and outputs

For all 32 intended condition/fraction cells report source-valid n, original
score-support n, mg/g mean and sample SD (n-1; unavailable below n=2), plus
original b0/b1/width kg ranges and missing reasons. Include valid observations
outside scoring support without enlarging it. Unequal coordinates mean dispersion
across recorded collection fractions, combining shot, coordinate and assay
effects; this is not analytical repeatability at an identical interval.

Separate numerical/coordinate application allowances, observed between-shot
spread, score influence, analytical repeatability/recovery/censoring/calibration,
early-input propagation, training/model selection and new-condition/cross-source
uncertainty. Unknown stays unknown, never zero or a fabricated total interval.
Historical contract, descriptive performance, finite perturbation stability and
practical incremental value are separate answers. No independently justified
intended-use margin is supplied; practical value remains unestablished. Do not
replace thresholds from observed SD/errors or infer equivalence/uselessness.
No whole-cup, mechanistic, physical-validation, production-readiness or commercial
rights claim. Caffeine remains a component of TDS.

Write exclusively to new external output directories. Public deterministic
RESULTS.json/RESULTS.md contain baselines, condition summaries, complete aggregate
sensitivity ranges/counts, adverse findings, availability and bindings. Never
publish individual shot metrics or keyed deletion means; their combination with
public condition means could reconstruct restricted values. Complete private
results retain every scenario, shot comparison, crosswalk and locator. Public
hashes bind private output without local paths. Pannusch/Schmieder and Mendeley
10.17632/y2tz67f6ry.1 attribution; source-derived CC-BY-NC-3.0 separate from
first-party software licensing. One independent nonhuman pre-analysis review,
one final review, focused synthetic tests, affected checks and hosted CI; no
new approval ladder. Keep operational QA separate from science.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; MERGE_AUTHORIZED=false;
PRODUCTION_ADOPTION_AUTHORIZED=false; NEW_MODEL_FITS=0; NEW_PREDICTIONS=0;
NEW_NATIVE_SIMULATIONS=0; NATIVE_EWP_RUNS=0;
HISTORICAL_SCORE_LIFECYCLE_INVOCATIONS=0; HISTORICAL_RESULTS_UNCHANGED;
NO_AUTOMATIC_SUCCESSOR. One draft unmerged Puckworks PR, auto-merge disabled.
