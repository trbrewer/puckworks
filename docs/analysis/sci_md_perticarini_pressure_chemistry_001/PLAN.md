# SCI-MD-PERTICARINI-PRESSURE-CHEMISTRY-001 — analysis contract

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## Question, exposure and scope

At fixed coffee, native grind and exact temperature setting, does the reported
duration response to nominal 6→9 bar accompany lower or higher reported TDS?
Which joint directions remain strict under explicitly declared per-condition
perturbations? Published EY is a secondary, chemically related central endpoint.
The deliverable is a condition-level observation target for future comparisons.
Duration agreement and historical per-grind EY/TDS range bracketing leave this
joint response untested. No model fit, pressure/temperature law, duration-to-EY
predictor, EWP comparison, production adoption or successor work is authorized.

The sources and preliminary contrasts, including the supplied review checkpoints,
were already exposed. This contract is recorded before implementation results;
it is not preregistration, blind/held-out prediction or protected scoring. One
implementation and one substantive independent nonhuman review; material findings
are resolved here with only affected evidence and required gates rerun.

Intake 2026-10-26: actual Puckworks base
`b3860d47ae6de6f6592add05cfac78fe9fb00487` equals reviewed main; #367 merged.
EWP main is `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`, read-only; production
Puckworks pin `fc61c4670ec7bf801e40bb391aab16048b8da26b` remains untouched.
Isolated branch `analysis/sci-md-perticarini-pressure-chemistry-001` preserves
unrelated work. Open Puckworks PRs #337/#336/#333/#321/#264/#257/#129/#128 show
no overlapping Perticarini/Egidi task. Read AGENTS/CLAUDE, onboarding, the data
and development guides, governance, relevant cards/registers and predecessor.
Original PDFs, relevant methods/text and native table renders are accessible;
this is not catalog-only inspection. Reuse the accepted complete authentication;
inspect only the chemical operator, averaging and native formatting anew.

## Original inputs and observation operator

Use canonical `perticarini2024/ey_tds_cibao` (18 conditions), raw-byte SHA-256
`2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703`, and
`egidi2024/table2` (12), SHA-256
`1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419`.
Thesis Table 4.3 and Egidi Table 2 are the same Modœtia observations, counted
once under `egidi2024/table2`. Preserve all original IDs from
`perticarini2024_pressure_grind.py`, coffee identities, exact temperature and
pressure strings, native/canonical grind labels, and predecessor artifacts.
Join by full condition identity, never row order; no raw-shot pairing.

Chemical operator: refractometer measurement of prepared beverage aliquot;
three extraction samples per configuration; C_bar=(C1+C2+C3)/3 and
E_bar=(E1+E2+E3)/3, with E_j=C_j/r_j and r_j=dry dose_j/beverage mass_j.
Sigma is reported TDS SD with unspecified estimator, retained descriptively,
including printed zero. Raw replicates, EY SDs, relevant covariance, actual
condition masses and an authenticated joint timing/chemistry replicate model
are unavailable. Nominal 20±0.1 g / 40±2 g does not establish E_bar=2*C_bar.
All three tables display TDS means to ONE decimal and EY means to two;
SD formatting varies. Printed decimals establish neither rounding nor accuracy.

Reuse the accepted reported-condition-duration qualification, not timed-shot
means, instantaneous flow or residence time. Pressure is a nominal machine
label, not measured puck pressure drop; temperature is a setting, not a measured
puck history. Native grind labels are ordinal within coffee, not a common
physical particle-size scale. Preserve numerical-table rights/attribution;
PDFs, facsimiles and page renders remain outside Git. No full intake reaudit.

## Exact coverage and arithmetic

All pressure contrasts are HIGHER minus LOWER. Duration: seconds; TDS and EY:
percentage points (pp), never relative percent changes.

- Primary: all 14 9−6 pairs: Cibao/93.4 (five grinds); Cibao/90.4 (Fine,
  Optimal, Coarse); Modœtia at each temperature (Fine, Optimal, Coarse).
  Retain original low/high durations, TDS means/SDs, EY means and adverse/tied rows.
- Interactions: six I_C=(C9−C6)_93.4−(C9−C6)_90.4, one per coffee and each
  shared Fine/Optimal/Coarse label. Compute from four original values; keep
  coefficient maps, component IDs, signs, exact thresholds and conditional status.
- Secondary, visibly separate: Cibao/93.4 Extra Fine and Extra Coarse, 12−9
  and 12−6 (four). TDS primary; EY/duration alongside.

Primary pairs cover 28 distinct conditions; two additional 12-bar conditions
bring the union to 30. All 14+6+4 slots are dependent derived contrasts, not
24 independent experiments. No unavailable cell imputation or coffee pooling.
Keep a complete condition-to-comparison map. Verify all 18 duration contrasts
against the accepted predecessor. At both extremes verify (12−6)=(12−9)+(9−6)
for TDS and duration. Shared P9 cancellation gives norm 2, not 4; identity residual
has norm/radius zero. These checks add no observations.

## Deterministic sensitivity and joint claims

For each original condition C_i*=C_i+delta_i, |delta_i|≤h_C≥0 pp. h_C is the
TOTAL declared allowance, not measured error, SD, SE, CI, tolerance or an extra
term added to inferred rounding. Analogously tau_i*=tau_i+eta_i, |eta_i|≤h_tau≥0 s.
Use one consistent original-condition collection across all derived contrasts;
no probabilistic independence, and overlapping marginal extrema need not be
jointly attainable. Never convert SD into mean uncertainty or propagate SD/h_C
into EY using a nominal exact brew ratio. EY uncertainty remains unqualified.

Combine repeated coefficients first. For L=sum(a_i*x_i), compute exact nominal
L0 and s=sum|a_i|; box image [L0−s*h,L0+s*h]. For nonzero L0 and s>0, strict sign
holds exactly at 0≤h<|L0|/s; equality touches zero and is unresolved. Pair norms
are 2; interaction norms 4. Printed zero with s>0 has no strict sign even at h=0.
Structural identity s=0 has residual/radius zero at every h and threshold null,
never division. Use exact rational arithmetic from source decimal strings for
values/bounds/status/thresholds; serialize exact values and readable displays.
Reject negative inputs. Primary sensitivity output is exact sign-loss thresholds.
Also illustrate h_C=0.05 pp and h_tau=0.5 s, neither an authenticated measurement
bound. No p-values, confidence intervals or significance labels.

Keep nominal signs, printed-tie flags, separate conditional component statuses,
joint labels and exact joint regions. For two nonzero differences, the strict
joint region is 0≤h_tau<|delta_tau|/2 AND 0≤h_C<|delta_C|/2. Otherwise it is
empty, with the zero-component reason. Preserve a resolved component when the
other is unresolved. Do not equate printed ties with physical equality.
Opposite TDS directions across temperatures require named component contrasts
and intersection of their strict domains, not merely a strict interaction.
Equal printed duration changes do not establish equal actual shortening.

## Outputs, verification and completion

Offline CLI: `python -m puckworks.analysis.perticarini2024_pressure_chemistry
--output DIR --tds-allowance-pp 0.05 --duration-allowance-s 0.5`.
Use predecessor identities/coefficient utilities without modifying accepted code
or labeling chemistry as seconds. No generic framework or new dependencies.
Compact bundle: PLAN, SOURCE_NOTES, condition CSV, primary/secondary CSVs,
interaction CSV and unified JSON (hashes, values, coefficients, regions, accounting),
RESULT with complete generated tables, one comparison figure, concise VIZ_SPEC,
VERIFICATION and REVIEW. Narrow card/consumer/capability producer updates only;
regenerate affected views and preserve existing dataset/evidence identities.

Figure: delta_duration horizontal, delta_TDS vertical, zero axes, separate
coffee/temperature panels, all 14 native-grind labels. Coincident points stay at
original coordinates with label callouts. Conditional pair half-widths are
2*h_tau=1 s and 2*h_C=0.10 pp at illustration, prominently not experimental error
bars. No fitted curve/correlation; secondary rows stay separate in tables.

Focused verification covers 30 identities/deduplication; 14+6+4 support;
18 predecessor duration comparisons; independent arithmetic and units; cancellation,
structural zeros, ties and threshold equality; component/joint regions; figure
extents/data agreement; offline deterministic regeneration; canonical/predecessor
byte preservation; EWP/default/pin preservation. Run required repository gates.
Independent review covers actual source access/operator/formatting/lineage,
arithmetic, allowance semantics, boundaries and claims. Record actual local and
hosted results, failures and pending states separately. Leave one PR OPEN / DRAFT /
UNMERGED, auto-merge disabled. Final closeout: URL, actual base, tested/submitted
head, numerical summary, verification, hosted CI and remaining limits.

The analysis establishes only arithmetic patterns in published summaries and
conditional strict signs. No causal pressure effect, resolved experimental
reversal, population law, duration-only physical-law rejection, mechanism,
shot covariance, measured 40g/duration flow, individual masses from mean ratios,
independent confirmation from related TDS/EY, practical equivalence, sensory
value, production adequacy or validation upgrade. Unknown uncertainty stays
unknown. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
