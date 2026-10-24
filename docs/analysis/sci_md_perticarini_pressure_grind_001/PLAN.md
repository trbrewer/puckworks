# SCI-MD-PERTICARINI-PRESSURE-GRIND-001 — frozen analysis plan

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## Question, exposure and freeze

How does reported condition duration respond to nominal pressure across grind
settings in Perticarini Extraction Procedure 1, and which aspects of the accepted
Cameron S2 pressure-by-grind relationship recur in this separate brewing campaign?
The source values and preliminary arithmetic were already inspected. This is a
bounded retrospective source analysis, not preregistration, a target-blind or
held-out study, or model validation. No protected scoring, parameter fitting,
new experiment or successor study occurs. This complete plan is frozen before
implementation outputs; its SHA-256 and freeze receipt are recorded separately
in VERIFICATION.md. One substantive independent review suffices. Routine bounded
corrections stay in this task, with unchanged scientific review evidence reused.

Live heads verified at intake, 2026-10-24:
Puckworks actual base `1398d38ff1986aa85150d55ad9f797bc1aaff1eb` (includes merged #359);
EWP `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Both equal reviewed heads; no
intervening commits or duplicate Perticarini PR were found. Work occurs in isolated
branch `analysis/sci-md-perticarini-pressure-grind-001`. EWP remains read-only;
unrelated work, production physics/defaults/dependency locks and historical
scientific receipts remain unchanged.

## Sources and observational contract

Use only canonical `perticarini2024/ey_tds_cibao` (18 rows,
`puckworks/data/perticarini2024/ey_tds_cibao.csv`) and `egidi2024/table2` (12 rows,
`puckworks/data/egidi2024/table2_egidi2024_tds_ey.csv`). Authenticate every condition
label and numerical cell against Perticarini's *Predictive Models in Espresso
Coffee Percolation*, Tables 4.2/4.3, printed pp.90/91, PDF pp.102/103; cross-check
Modœtia against Egidi et al., DOI 10.1016/j.chaos.2024.115625, Table 2, PDF p.6.
Inspect rendered tables, units, headers, captions and methods: thesis printed
pp.85–89/PDF pp.97–101 and Egidi p.6. Record actual PDF and input file SHA-256
hashes separately from Git blob IDs. Thesis reviewed SHA-256:
`248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f`;
Egidi: `1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33`.
Keep originals and facsimiles outside Git; offline numerical reproduction uses
committed canonical tables alone. Investigate hash/value discrepancies, retain
original identity/value and unsupported comparisons, and resolve only what the
source supports. Never override evidence with the supplied arithmetic checks.

The two publications present the same Modœtia observations, retained under
`egidi2024/table2`: no duplicate dataset, campaign or replicate evidence. The
30-row observation view is derived bookkeeping, not 30 authenticated shots.
Procedure 1 uses 20 ± 0.1 g dose, nominal 40 ± 2 g beverage, 20 kgF nominal tamp,
Mythos 1, PUQ PRESS M2, VA388 Black Eagle and VST Competition basket (internal
radius 29.25 mm, height 26 mm). Three samples per chemical configuration and
explicit TDS/EY averages do not establish n=3 duration means or 90 timed shots.
Displayed sigma is TDS SD. Use **reported condition duration** for tau: statistic,
spread, rounding rule and clock start/stop convention are unresolved unless
further primary evidence resolves them. Do not derive duration SD/SE/CI from TDS.

Native p [bar] labels 6/9/12 are nominal machine settings; pressure reference,
sensor node and actual history remain unknown. No one-bar subtraction or mapping
to measured puck pressure drop. Native tau units are seconds. Actual per-condition
beverage masses are unknown: no 40/tau measured-flow conversion, per-shot mass
inference from EY/TDS, resistance or permeability inference. Exclude Table 4.1's
pressure/temperature-pooled mean times, all model times and fitted/model Darcy
fluxes. Preserve ordinal extra_fine, fine, optimal, coarse, extra_coarse plus
original labels. Optimal is source recipe-defined; no common particle-size scale
across coffees or mapping to Cameron dial values.

## Complete support and contrast families

Keep four separate coffee × exact decimal temperature strata:

| Coffee | Temperature (°C) | Supported grinds and nominal pressures | Rows |
|---|---|---|---:|
| Cibao Altura | 93.4 | five grinds at 6/9; extra fine/coarse also 12 | 12 |
| Cibao Altura | 90.4 | fine/optimal/coarse at 6/9 | 6 |
| Modœtia | 93.4 | fine/optimal/coarse at 6/9 | 6 |
| Modœtia | 90.4 | fine/optimal/coarse at 6/9 | 6 |

No imputation, temperature/coffee pooling or full-factorial 12-bar interpretation.
Join by dataset, authenticated coffee, exact temperature, pressure and normalized
grind, never row position. Use stable source-condition IDs from these keys.

Primary: all 14 D_6,9(C,G,T) = tau_9 − tau_6. For **every** supported ordered
finer/coarser pair Ga/Gb in each stratum, compute I_6,9 = D(Ga) − D(Gb):
10 + 3 + 3 + 3 = 19 interactions. Retain adverse and zero rows.
Secondary (Cibao/93.4 extreme grinds only): four D (12−9 and 12−6 at each
extreme) and two I (extra fine minus extra coarse on those intervals).
Total **39 distinct dependent contrast IDs**: 14/19/4/2. Uncertainty layers,
21 reversal diagnostics and arithmetic-identity checks add no contrasts.

Build all contrasts from signed coefficients on original source-condition IDs.
Combine shared coefficients *before* bounds. Check coefficient-vector equalities
D_6,12 = D_6,9 + D_9,12 at both extremes and I_6,12 = I_6,9 + I_9,12 for the
extreme pair. These are structural identities, not independent confirmations.

## Exact arithmetic and conditional sensitivity

Layer A: exact rational arithmetic on printed tau; classify positive, negative
and reported_zero. Reported zero does not establish physical equality.
Layer B: one common deterministic entrywise box over all 30 source conditions,
tau_i* ∈ [tau_i−h,tau_i+h], h ≥ 0 seconds. For combined vector a,
L0 = sum(a_i tau_i), s = sum(abs(a_i)), L(h)=[L0−hs,L0+hs].
For s>0, h_critical=abs(L0)/s exactly; strict sign holds only if the enclosure
excludes zero, hence for nonzero L0 only at h<h_critical. Equality is unresolved.
For L0=0,s>0: reported_zero, critical=0, never strictly signed even at h=0.
For s=0: structural arithmetic identity, residual/radius identically zero,
critical=null; never divide by zero. Primary D norms=2 and I norms=4.
Classify before display rounding; preserve exact rationals and round outward
if decimal bounds require rounding.

Include h=0.5 s only as a **conditional nearest-second illustration**; integer
printing does not authenticate a rounding rule. These are conditional perturbation
ranges, not confidence intervals, timing error bars, experimental variability,
significance or measurement accuracy. The box assumes no probabilistic
independence. All contrasts share the same original values; marginal extrema
cannot be combined arbitrarily. Propagate composed claims from original
coefficients. Report all exact critical values and breakpoint summaries showing
what survives as h increases, including zero-touch boundaries; never estimate h
from these comparisons.

## Reversal diagnostic and interpretation

For all 19 primary and two secondary grind pairs, retain component D IDs,
component sign resolution, and whether both signs resolve and oppose at h=0 and
h=0.5. For nominally opposite nonzero components,
h_reversal=min(abs(Da)/sa,abs(Db)/sb), here sa=sb=2. Strict opposite signs hold
for 0≤h<h_reversal; at the boundary reversal is unresolved, not disproved.
Same-sign or zero-component pairs have no positive reversal threshold and report
nominal opposite signs not established. An interaction sign is not a shortcut for
reversal. Keep secondary evidence separate from the primary 6-to-9 question.

Independently recompute from canonical rows; use the request's full numerical
cross-checks only as test oracles, never as production result constants. Check
14 D/19 I nominal and h=0.5 counts, both adverse Cibao optimal-minus-coarse rows,
all secondary values, exact identity cancellation and five primary nominal
reversal thresholds. Discrepancies remain visible until source-resolved.

RESULT.md answers which grinds differ, which strict orderings survive the stated
allowance, reversal thresholds, descriptive differences between strata and
measurement information needed for stronger inference. Compare briefly with
accepted Cameron S2: retain its central-reading and displayed-extents layers
separately; Perticarini's assumed box is not Cameron's displayed variability.
No pooling, common fitted effect, grinder alignment, temperature test via
significance labels, matched replication or shared-mechanism conclusion.
No compaction/channeling/choking/fines migration, causal/population, actual
puck-pressure-drop, intrinsic permeability or resistance inference. Unknown
shot variability stays unknown even for contrasts with large critical h.
Persistent interactions with unresolved primary reversal is a valid completion.

## Implementation, discovery and completion

Small standard-library/existing-dependency module and focused tests following
`cameron2020_pressure_tamp.py`; no generalized framework or model component.
Command: `python -m puckworks.analysis.perticarini2024_pressure_grind --output /tmp/perticarini-pressure-grind`.
Bundle: this PLAN; SOURCE_NOTES; qualified observations.csv; contrasts.csv/json
(all 39, coefficients, source/input hashes, units/assumptions, nominal status,
exact norms/critical values and h=0.5 bounds/status); reversals.csv plus equivalent
JSON; linked complete generated tables; RESULT; COMPARISON.svg from the same
records; bundle-local VIZ_SPEC; REVIEW and VERIFICATION. CSV uses LF.
Figure groups primary D/I by stratum and visibly separates secondary results;
native labels, seconds, categorical grind spacing, visible zero, all negative/
zero rows and explicitly conditional h=0.5 ranges. No source artwork in Git.

Update actual consumers and verified shared-publication lineage in the two
existing manifest records, relevant cards/provenance and curated producer
capabilities/family notes. Correct the Perticarini blanket condition-means claim;
preserve TDS/EY bracket qualification and all unrelated equations/PSD/backlog.
Retain dataset identities/count. Run available-data-register, local-corpus-family-
index and espresso-data-guide generators; never hand-edit generated sections.
Additional corpus/claim-binding/Insight generators only for actual dependencies
or demonstrated generated-check drift. No new corpus scan. Check preservation of
nominal pressure semantics and unrelated relations/stable IDs; no measured
puck-pressure, flow-calibration or physical-validation edges.

Verify schemas, all 30 unique conditions/four strata, joins/orientation,
14/19/4/2 support and 21 diagnostics, exact arithmetic/cancellation/structural
zeros/zero touches/reversal boundaries, independent arithmetic, deterministic
outputs/figure and affected loader/discovery paths. Run required repository
checks; inspect current required hosted checks. Record actual local, hosted and
one substantive independent scientific-review dispositions separately; resolve
material findings here, distinguish infrastructure failures, no CI policy changes
or unrelated scientific campaigns. Open one draft PR with question, direct
result, reproduction and limits; leave OPEN / DRAFT / UNMERGED, auto-merge off.
Closeout records actual base, final submitted/tested head, source identities/pages,
all family/results/thresholds, unresolved semantics, verification and PR URL.
