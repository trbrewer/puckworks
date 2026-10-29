# SCI-MD-POCKETSCIENCE-AFFINE-TDS-001

Pocket Science Coffee (2024). G1 / NO_GOVERNING_PHYSICS_CHANGE. One retrospective,
exposed conditional comparison under the owner's bounded implementation/review
authorization. Numerical checks are not independent human review. P1 blind-TDS=OPEN.

PW main `21669a427145194e1f4003e3cf1b97dedefe2679`; new branch base/scientific parent,
PR378 `2425223a872e104345a787984ee5874671258368`; its Git parent / PR377 final head
`499930653969f473136b2c5303b00d09b8945c68`; PR375 LOCO reference
`9f8c6c7cf894872908f3ea212c69209db13c602a`; PR374 ancestor
`2f93c216f02700e28801418a3069684fff0ba9ea`; read-only EWP
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Preserve predecessors and the pytest
launcher configuration. Stack the draft on PR378 while unmerged; no auto-merge.

## Authentication, restored cohort and folds

Dataset: `pocketscience2024/workbook_assay_reconstruction`. Resolve configured
locators inside code, never print private paths/configuration or scan unrelated
directories. `--predecessor` permits a narrow explicit PR378 candidate. The
predecessor resolver's dictionary covers PR374–377; its proposed output is only
a locator. Authenticate the actual PR378 FREEZE/RESULT bytes before accepting it.
Neither a name nor a symlink establishes authority.

| Receipt | SHA256 |
|---|---|
| Workbook | `9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc` |
| Ancestor57 membership | `1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196` |
| PR375 FREEZE.json | `cdad2b189075198368efdcd5b46953df4ef0d38a20a662ff4e24ebb160c595e5` |
| PR375 RESULT.json | `fdf422e40b9ccd7598c3d99be10a211a6a41b342c89943a9a87232845811d868` |
| PR378 FREEZE.json | `88d0d110185b1ddb3e2bf1a3abfcd0d01abd927c04655edc2d62ad288883a4ef` |
| PR378 RESULT.json | `17e1af2636e697bf9ba9455eab5dc3a658fe01ab0ce560b793224f09a2fa820c` |

Verify frozen code/input hashes, result/freeze linkage, relevant saved artifacts,
and full-precision historical results. The unchanged observer opens the original
formula/cache workbook views once and compares all 60 cup-qualified observations,
identities and original ordering with PR378 SOURCE_SHOTS and earlier full-cohort
SHOTS records. PR378 SHOTS contains only40 Sworks rows and is not this cohort.
No PR378 transfer replay or separate historical bootstrap campaign is authorized.
Rounded chat numbers are context, never regression targets. Different transfer
and LOCO estimands are not compared numerically as competing scores.

Primary: exactly57 physical shots, 37 Sworks+20 VST, 29 traditional+28 turbo,
12 conditions. Preserve PR375 membership, exclusions, physical order and sorted
global condition order. Identity=sheet+row; condition=(sheet/basket,grinder,
preparation,dispersion). ALL60: 40 Sworks+20 VST, 30 traditional+30 turbo,
same12 condition definitions. Restore Sworks rows7,9,23 with original sectioning
exclusion provenance. Ten separate flush measurements remain excluded. Repeated
readings, used means and resampled copies do not add physical shots.

Freeze explicit folds before fitting. Each fold lists training/held identities
in original order; sets are disjoint, every copy of the held condition stays
outside training, and every physical shot receives exactly one OOF prediction
per arm. New fold hashes:

- primary: `8985caa049b1699a7b56c986ce811342e0750e881f4fdd6b758b13c28edf5127`
- ALL60: `ee687e95c7205170cc5025f91e660a745a9eccb1d4fd7f3f7eeef55c4a539807`

Fold records also freeze training x ranges and held extrapolation, overall and
by style, before fitting. Bootstrap supports use positive-weight training rows.
Keep every qualified held row; record coverage and raw prediction-domain flags.

## Observation and exposure

x=measured dose_kg/measured final beverage_kg; raw D/E grams become kg.
y=direct filtered numeric TDS percentage points from B, including B54.
Raw C supplies the independently refitted/scored unfiltered sensitivity.
Nominal basis: refractometer-equivalent solute per solution mass; no density
conversion. Derived EY, regional assays and historical Y54 are not predictors
or substitute targets; preserve historical treatment. Exact mapping remains
Niche Zero→traditional, Superjolly MP64→turbo. Preparation N means paper on top,
distinct from model N.

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS. Used means expose underlying shots.
Procedural holdout and new arm A do not restore blindness. Inspect only existing
qualified files/receipts; record actual inspection and limits. Sessions,
installation/order, shared calibration and systematic measurement uncertainty
remain UNKNOWN. No causal, practical-adequacy, new-campaign or production claim.

## One bounded-slope affine policy

Explicit arm order: A,M,P,N. A=a+b*x; M=theta[style]*x; P=alpha*x; N=mu.
A/M each fit two scalars; P/N one. Each independently minimizes identical
physical-shot squared error in absolute TDS pp on the same training fold.
Point weights=1; bootstrap weights=the shared multiplicities.

Freeze a∈R, b∈[0,100]; M/P/N retain coefficient bounds[0,100]. The signed
intercept is a local empirical TDS-pp offset, not an extraction property.
A nonnegative intercept would impose an unsupported constraint at x=0.
This is the bounded-slope affine family, not unrestricted affine regression.
A/M match nominal count, observations, loss and complete optimization, but their
parameter meanings and constraint geometries differ. Report active/interior fits.

For positive-weight training rows only:

```
xbar=sum(w*x)/sum(w); ybar=sum(w*y)/sum(w)
Sxx=sum(w*(x-xbar)^2); Sxy=sum(w*(x-xbar)*(y-ybar))
b=clip(Sxy/Sxx,0,100); a=ybar-b*xbar
```

This is the exact constrained optimum. Never independently clip coefficients
from an unconstrained affine solution or use the disjoint-column shortcut on
correlated columns[1,x]. M uses independent style-specific weighted scaling;
P uses clip(sum(w*x*y)/sum(w*x*x),0,100); N uses clip(sum(w*y)/sum(w),0,100).
Reuse unchanged design, grouping, bootstrap and metric helpers with explicit
column mapping. Fit only A/M/P/N; do not mutate predecessor globals/guards.

Fit functions receive only training x,y,style,weights. Prediction accepts
coefficients,x,style and no target y. Predict raw a+b*x; no clipping or dropping
targets outside nominal[0,100]. Flag and score such predictions unchanged.
No inherited coefficients, alternate observer, target-dependent bound, tuning,
unequal fit budget, interaction, shrinkage or other policy/model family.

## Numerical gates on every point/bootstrap/deletion fit

Require finite inputs/weights, nonnegative weights, positive finite total weight,
both training styles for M, positive finite Sxx and full-rank weighted[1,x].
Ordinary SVD rank tolerance=max(n,p)*machine_epsilon*largest_singular_value;
record singular values, rank tolerance and column-normalized condition number.
No post-score cutoff, ridge or fallback family. Active bounds alone are valid.

Independently solve A on weighted original[1,x] using scipy.optimize.lsq_linear,
bounds=([-inf,0],[inf,100]), method="bvls", tol=1e-14. Independently solve retained
arms with their exact bounds/objectives. Both training and held raw predictions
must agree within absolute1e-10 TDS pp. Require all training nesting inequalities:

```
SSE(A)<=SSE(P)+allowance
SSE(A)<=SSE(N)+allowance
SSE(M)<=SSE(P)+allowance
allowance=128*epsilon*max(1,sum(w*y*y),relevant SSEs)
```

A/M are not nested. Tolerances concern arithmetic, not measurement error or
precision. Rank/solver checks suffice; no jaxgsa/GSA campaign is a deliverable.

## Scores, paired intervals and reproduction

Primary loss=sqrt(mean squared error across physical OOF shots), TDS pp.
Report MAE, signed prediction-minus-observation bias, unchanged condition-balanced
RMSE, coefficients, condition/style errors, adverse/worst cases, support and
predictions privately. Contrasts: A/M primary; A/P key incremental-value comparison
against retained P; A/N naive reference. Delta=RMSE(A)−RMSE(B), negative favors A;
gain=1−RMSE(A)/RMSE(B), positive favors A. Zero reference loss gives undefined
gain, no epsilon; retain valid absolute contrasts.

Primary, unfiltered and ALL60 each use2,000 paired draws, numpy default_rng
seed20261026. Preserve physical/group order. Resample physical shots within each
fixed condition at original size. One global multiplicity vector is shared by
all arms. Refit every arm in every outer fold using training rows/weights only;
score held predictions with held multiplicities. Save multiplicities, fold
coefficients/numerical checks, draw scores/contrasts and prediction-domain counts.

Authenticate PR375 saved multiplicities and verify their deterministic sequence
before fits. Compare new M/P/N point predictions/scores to corresponding PR375
full-precision records within1e-10 pp for all three analyses; compare M/P/N draw
metrics inline and exact multiplicities on every draw. These reference refits
belong to the joint comparison, not separate historical campaigns.

Report percentile95% CIs for each RMSE and paired delta/gain, requested/completed/
failed/unattempted counts, undefined gains, active/interior fits and domain flags.
A failed draw stops that campaign; save its multiplicity/reason and unattempted
count. Suppress successful-only CIs/decisions. Undefined gains do not erase
absolute contrasts; relative intervals require all completed gains defined.

Intervals condition on fixed conditions, within-condition exchangeability and
previously selected family. They omit unknown sessions, installation/order,
shared calibration/systematic error and prior model selection; they are not
simultaneous intervals or new-campaign evidence.

## Decisions, boundaries and exactly three sensitivities

For each absolute delta CI: upper<0→first arm lower; lower>0→reference lower;
otherwise, including zero endpoints→unresolved. Primary A/M labels:
AFFINE_LOWER_THAN_MATCHED_M / M_LOWER_THAN_AFFINE /
AFFINE_MATCHED_COMPARISON_UNRESOLVED.

Separate selection: only when A/M,A/P,A/N all have upper<0, report
AFFINE_CONDITIONAL_ADDED_VALUE_OVER_M_P_N. Otherwise report
AFFINE_NOT_SELECTED_RETAIN_PRIOR_P_QUALIFICATION. Always report individual
conclusions. A/M alone cannot replace P. Retaining P does not establish
equivalence, adequacy or absence of affine benefit. Preserve historical results.
Zero is no improvement, not a practical acceptance margin.

Gain grades: worse<0; small[0,.10); moderate[.10,.25); large>=.25. Report point
and every CI-intersected grade. Reclassify unchanged estimates/CIs under all nine
lower{.075,.10,.125} × upper{.1875,.25,.3125} combinations, without refits.
These are reporting conventions, not adequacy or measurement-error robustness.

A: unfiltered C, same57/folds, independent refits/bootstrap. B: ALL60 filtered B,
same12 definitions, every arm refitted, own bootstrap. C: delete each primary
condition in turn, rerun LOCO on remaining11, refit every remaining fold and
score every remaining shot. Report point ranges, ties and ranking reversals,
not CIs. Identify exactly which interval/selection conclusions change. No
favorable-channel selection, reverse transfer, further partition or policy variant.

## Bounded execution, artifacts and handoff

Freeze source/cohort/folds, policy/code/method hashes, seed/tolerances, roles,
decisions and sensitivities before scoring. One implementation/author-review
cycle, at most one material correction; scientific computation<=30minutes,
excluding installation/required QA. No acquisition, figures, experiments, native
EWP runs, production/registry changes or separate governance project.

Stop on missing authenticated inputs, hash/observation/membership drift,
unresolved identity/basis, leakage, rank/solver/oracle/nesting failure,
unexplained reference drift, invalid inference, exhausted scientific budget or
unfixed material bug. Record precise BLOCKED/NOT_RUN/INCOMPLETE with existing
artifact needed or exact failure. No means substitution, adverse-shot removal,
silent tolerance relaxation or scope expansion. Exposure/unknown sessions are
limitations, not a new audit. Preserve predecessor files and private artifacts.

Install `pip install -e '.[dev,reconstruct]'`, retaining the corrected pytest
root-path setting. From this isolated branch:

```bash
python tools/pocketscience_affine_tds.py inspect
pytest -q tests/test_pocketscience_affine_tds.py tests/test_pocketscience_pooled_scaling.py tests/test_pocketscience_cup_tds.py tests/test_pocketscience_cross_basket_tds.py tests/test_pocketscience_cross_style_tds.py tests/test_pocketscience_cross_dispersion_tds.py tests/test_pocketscience2024_assay.py
python tools/pocketscience_affine_tds.py freeze
python tools/pocketscience_affine_tds.py run
```

The runner resolves candidates inside code and emits only safe status/hashes.
Use `--output` for a fresh private external directory and `--predecessor` for an
explicit PR378 locator, consistently at each stage. `inspect` authenticates once,
`freeze` binds final code/tests/methods, `run` refuses repeated attempts. Run
focused tests/required existing gates once; broaden only for a concrete failure.
Report local and hosted checks separately; numerical verification is not human review.

Public: code, synthetic tests, frozen methods/reproduction, safe hashes/status.
Private: locators/identities/coefficients/results/predictions/aggregates/draws;
RESULT.md<=2pages,target<=750words including tables; SUMMARY.md<=120words;
complete RESULT.json,SCORES.csv,CONTRASTS.csv, predictions/bootstrap records,
inspection/freeze receipts and ARTIFACTS.json. Draft PR on PR378, unmerged,
auto-merge disabled. P1 blind-TDS=OPEN.

Single next candidate: SCI-MD-POCKETSCIENCE-AFFINE-CROSS-BASKET-TDS-001, same
A/M/P/N policy,37 Sworks→20 VST under established basket contract. It is justified
only if this primary selection earns incremental value over M/P/N; otherwise
mark NOT_JUSTIFIED and retain prior P qualification. Do not execute it here or
manufacture another affine/partition follow-up. Reassess if genuinely unexposed
existing data become executable.
