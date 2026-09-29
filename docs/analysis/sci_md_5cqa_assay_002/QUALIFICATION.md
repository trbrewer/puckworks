# Source and numerical qualification

SCI-MD-5CQA-ASSAY-002 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
Scientific adequacy, source qualification, numerical qualification, software QA,
independent review, hosted CI and merge authorization are separate statuses.

Eight original files and ten required normalized registers retain exact accepted
identities. Original unrounded MATLAB `cAlcaloids(:,3)` and campaign-specific HPLC
area-I calibration/dilution formulas reconcile all 69 first assays and 66 valid
second assays: FIT 45/42 and PRED 24/24, respectively. The original FIT denominator
is 45 shots and 180 intended suffix slots. The three invalid q2 spills exclude
FIT-E03-R1, FIT-E11-R3 and FIT-E14-R3 from every arm, leaving the matched 42-shot,
15-design cohort and 168 intended targets. Their zero assignments were never
interpreted as valid assays or nondetects. Valid zero concentrations remain valid.

All 180 original FIT suffix values/formulas were source-reconciled; 165 of the
168 eligible slots have qualified measured mass prefixes. The original missing
prefixes remain FIT-E01-R3 fractions 7/10 and FIT-E06-R3 fraction 10. Every intervening
original vial contributes to cumulative mass; unassayed vials are included.
No nominal-flow replacement, inferred missing mass or imputed chemistry is used.
Held-design comparison support is identical across arms/lambdas: 164/168 slots,
including the three missing prefixes and FIT-E06-R2 fraction 10 beyond its fold's
training-only bound of 0.06610329999999999 kg. The final training-derived bound is
0.06971540000000001 kg. PRED coordinates never enlarge it.

All 549 real starts converged, 183 per arm, with zero failed or boundary starts.
Actual residual-call counting includes 101,716 calls, of which 97,175 are numerical
Jacobian calls; maximum 313/start. The fitting span was 34.413168 seconds, versus
3,600 authorized; optimizer wall sum 20.291055 seconds. Peak fitting RSS was 85,728 KiB.
One worker/thread, a 12 GiB address-space cap and 5 GiB private evidence ceiling apply.
The actual task clock started 2026-09-29T16:34:51Z and expires 22:34:51Z without resets.
No historical arm was refitted, regenerated or rescored. Every attempt, objective,
convergence/boundary record, held-design score and numerical allowance is retained
privately and bound by FREEZE.json; public DEVELOPMENT.json reports all candidates.

Each arm independently selected lambda 0.0001 under the conservative largest-lambda
tie/ambiguity rule. Selected held-design balanced R is 0.174767448 mg/g for L1M,
0.108564633 for L2M and0.105159253 for L12. These are FIT-only development estimates,
not unbiased nested validation or the later-campaign result.

The predecessor 64/128-point knot-split quadrature and independent adaptive
integration remain unchanged, with epsabs 1e-14 kg, epsrel 2e-13 and limit 200.
Shared fraction 3 boundary reconciliation is restricted to the established
four-ULP anchor discrepancy and explicitly adds the displacement to the interval
mass allowance. There is no clipping to obtain qualification. All 285 supported
prediction records qualify; the maximum total allowance is
2.0385979472329884e-16 kg, below 1e-9 kg. Numerical allowances propagate through
concentration, shot R/bias, condition/panel averages and every decision threshold.
They are neither analytical uncertainty nor statistical confidence intervals.

All 288 status records remain frozen: each arm has 48/48 primary, 24/24 temperature
and 23/24 flow support. PRED-E07-R1 fraction 10 remains outside the mass domain.
C08 mass-feature extrapolation remains flagged. Feature extrapolation does not
remove predictions or establish accuracy. Original-denominator failure lower
bounds remain available when a condition is incomplete; incomplete coverage alone
does not prove scientific failure. Secondary panels cannot rescue primary failure.

New synthetic tests cover exact species/SI units; arm-specific field rejection;
q2 poisoning invariance for L1M and q1 invariance for L2M; PRED suffix/recipe/identity
firewalls; whole-design folds and fold-local transforms; identical cohort masks;
spills versus valid zeros; exact 20/20/25 counts; both fixed-lambda nesting directions
and unchanged predecessor penalties; immutable models/states, strict identities
and deterministic replay; additivity, bounded nonnegative delivery, knot splitting,
adaptive integration and zero-width/invalid-query semantics; original-denominator
failure bounds and numerical ambiguity; durable starts, actual Jacobian counts,
resource budgets and rejection of repeated scoring. Source-free inference is
checked with training/source imports, optimizer calls and network access forbidden.

The pre-fit focused/new/predecessor run passed 154 tests. A prior synthetic test
asserted a preparation-level audit key on a narrower source audit and failed;
only that assertion was corrected before real fitting. No science/source/runtime
change followed fitting. Full local QA and final publication checks are recorded
in QA.json and HANDOFF.md. Existing skips and optional-Taichi acknowledged exception
remain distinct from passes. Generic QA never invokes a protected historical scorer.

Pannusch/Schmieder are one shared lineage. Unknown coffee-lot/roast-batch joins
remain unknown. Source-derived artifacts retain CC-BY-NC-3.0, Mendeley DOI
10.17632/y2tz67f6ry.1, separately from software licensing. Original data, detailed
observations/predictions, shot results and logs stay private. Physical validation
and analytical uncertainty remain NOT_ESTABLISHED. There is no production,
registration, default/lock, EWP, native OpenFOAM, release, merge or successor action.
