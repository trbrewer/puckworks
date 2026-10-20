# 5-CQA calibration provenance and retained FIT/PRED applicability

SCI-MD-5CQA-OBSERVATION-PROVENANCE-001. GOVERNANCE_CLASS=G1;
NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY; RETROSPECTIVE; TARGET_EXPOSED;
SOURCE_INTERNAL; PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Determine what existing upstream records can distinguish among calibration,
dilution, recovery/censoring/sample identity, campaign/material and predictor
explanations. An unresolved or unavailable component is a result. No new blind
holdout, fit, replay, prediction, score, correction, offset, uncertainty allowance
or change to accepted authority is authorized.

## Intake and finite boundary

PW base e6822df8df4465e61ce4616c7a1c577236cab9b2 has accepted #344 tree
b4492544eac40cd0d6d5f3ff856ed9626fe18918. #343 merge b755f250 is an ancestor.
EWP remote main 7c025527da7e07982428d4c78a3e79bfa29a76ac is contextual read-only.
Targeted task-ID and equivalent PR checks found no duplicate. Main has no delta
from the supplied base. No unrelated checkout was reset.

Eight originals are independently authenticated against ASSAY-002
SOURCE_IDENTITIES.json and source_inputs.csv: P24-HPLC-FIT/PRED,
P24-DOE-FIT/PRED, P24-M-PREP-FIT/PRED, P24-MAT-FIT/PRED. Inherited DELIVERY-001
label and lineage remain intact. Existing environment/config root semantics are
used; historical all-or-nothing resolvers remain unchanged. Missing access,
identity failure and parsing failure are distinct and block only dependent uses.

Metadata intake found all eight originals accessible and matching. Four workbooks
have 20/11 HPLC FIT/PRED sheets and six sheets in each DoE book, all visible;
both DoE books have one hidden filter defined name. HPLC includes nonnumeric CGA,
Coffein and Trigonellin sheets. Inspect CGA stock/working-standard records and its
embedded chart; formula/header/comment records that explicitly describe relevant
preparation, batch, controls or material identity; HPLC numeric fraction sheets;
DoE HPLCWeightsAlcaloids, ExpSheet and relevant SampleWeights identifiers.
MAT container metadata and MATLAB text are inspected without executing them;
accepted MAT value reconciliation is reused. M-PREP names are preprocessing code,
not physical preparation records.

Finite queue: these eight identities and their internal explicitly linked ranges,
charts, defined names and external links. Record each reference once using source
identity plus part/range; stop cycles by visited identity. FIT HPLC has one external
workbook relationship to an author's Windows path; inspect its embedded external
link metadata and dependent references, but do not infer an alternate version or
search a new corpus. Other-analyte/telemetry references in MATLAB are disposed as
not applicable. No directory census, acquisition or source execution. Original
files are never saved, recalculated or link-refreshed.

## Completed-work/new-work ledger

| Evidence | Status and actual scope | New information sought |
|---|---|---|
| RAW-REPRO-001 and accepted dictionary/registers | Reuse species/column mapping, valid-zero and spill semantics, 45 FIT/24 PRED shots, original vial masses/support | No reconstruction rerun |
| DELIVERY-001, TDS-001, ASSAY-001/002 | Reuse campaign formula/cache/MAT reconciliation, all 69 q1 and 66 valid q2 assays, 180 FIT and 96 PRED suffix formulas/values, mass-prefix exclusions | No repeated assay calculation |
| #340 decision-resolution addendum | Reuse residual decomposition, declared physical-shot deletions, adverse panels and feature extrapolation | Residual identities supply no causal offset |
| October 1 Section E C01; absolute-benchmark-20261001T004537Z | Reuse three March C01 shots, six fractions, caffeine/trigonelline and 18 preparation checks | Newly establish explicit shared preparation/row relationship to 5-CQA; no generalization without joins |
| CGA sheets and linked charts | Newly inspected upstream records | Reconstruct declared standard preparation arithmetic and displayed regression, separately from standard accuracy |
| Calibration-to-sample batch relation; recovery/blank/LOD/LOQ; lot/roast relation | Previously unresolved; inspect only new linked evidence | A supported applicability/control/material relation, or bounded unresolved disposition |
| DoE HPLCWeightsAlcaloids to HPLC sample rows | New independent quantity comparison outside the C01 predecessor scope | Identify agreement, transcription conflict, ambiguity or missing preparation; copied quantities are not independent weighing events |
| External Windows workbook reference | Unavailable original reference unless accessible at its explicit locator | Preserve unresolved relationship, never conclude nonexistence |

## Method fixed before new reductions or joins

The independent reviewer audits this protocol after metadata intake and before
any new regression, preparation reduction or cross-source join. Historical results
and selected source metadata/ranges were exposed during design. No historical
review stage is reopened.

**Identity and bases.** Preserve MATLAB cAlcaloids(:,3), HPLC response I and mass Y,
with original six fractions 1,2,3,5,7,10. General CGA/Chlorogenic acid worksheet
labels do not authorize CQA_sum substitution. Source calibration concentration
is labelled mg/kg, response is chart-labelled peak area mV min/10. FIT uses
(area−78.923)/24.513 and PRED (area+88.067)/26.383 for diluted concentration.
The downstream mg/kg × dilution /1000 yields beverage mg/g, then × whole fraction
g gives analyte mg. No density conversion. Aliquot coffee mass, dilution water,
whole vial liquid and dry dose have separate identities.

**Calibration reconstruction.** Inspect original stock weighed entries B/C5,8,
F formula/cache; working-standard H/I/J/K (and L/M means); chart2 CGA D/E43:55.
Reproduce exactly the source stock rule (which uses water mass as denominator),
working dilution and linked chart linear trendline: response on concentration,
free intercept, all populated source chart pairs, equal point weights as encoded
by the chart, no new exclusion or regression selection. Preserve FIT blank chart
positions as missing, PRED zero pair as an explicit chart point of unresolved
physical origin; do not invent a measured blank. Check cached plot pairs against
underlying standard rows. Compare coefficients only at their displayed rounding
precision. A regression match does not verify purity, weighing accuracy or batch
applicability. Flag mass-basis ambiguity rather than change the source rule.

**Applicability/range.** Distinguish nominal target standard concentrations,
prepared source concentrations, observed standard-response support and an
explicitly validated range (unknown unless documented). Equality with either
endpoint counts within support. Sample classification is allowed only for
explicitly applicable standards of the correct analyte/basis: a source-defined
calibration/sample association or batch/run key, not co-location, nearby dates or
matching coefficients alone. If absent, both response and diluted-concentration
range outcomes remain unassessable; below/within/above counts are null, not zero.
Do not reconstruct all old assay values to attach unavailable flags. If a supported
relation is found, compare original I response and source-equation diluted mg/kg
separately; preserve zeros and all flags. No comparison to undiluted liquid,
fraction mass, dose or model-feature limits.

**Preparation/sample joins.** Extract DoE explicit No./Fr. and IST H20/IST Kaffee
entries with exact cell locators. Match only within a campaign by unprimed physical
sample number and fraction, crosschecked against source ExpSheet shot numbering,
HPLC sample label and accepted Y-to-I row reference. Record all duplicate,
ambiguous or unmatched keys; UNKNOWN never joins. Fraction labels in merged source
blocks may be carried only within the explicitly bounded block. Compare recorded
water/coffee quantities and (water+coffee)/coffee with the HPLC C entry where the
formula or C01 source rule establishes it. Require positive coffee and nonnegative
water; missing/formula-error/invalid values stay unassessable. For FIT embedded
literal formulas compare each quantity as well as the ratio. For PRED cached
numbers distinguish arithmetic consistency from an independently logged injection.
Use arithmetic-only relative tolerance 1e-10 (absolute 1e-12) for double caches;
exact printed input quantities are compared without relaxing their decimal values.
This tolerance is not analytical uncertainty or an adequacy limit.

Reuse C01's 18 preparation checks; newly inspect its explicit common C reference
across T/V/Y to extend that preparation interpretation to 5-CQA. Do not count the
same 18 as new arithmetic evidence. Remaining preparation comparisons are new.
If a concrete discrepancy exists, retain private source-value diagnostic with both
locators, documented rule and direct dilution/concentration/mass multiplier only.
Do not compute a corrected predictor or alter observations/conditioning inputs.

**Roles and coverage.** FIT: 45 physical shots, q1 45 intended/valid conditioning
inputs, q2 45 intended/42 valid conditioning inputs, suffix 180 intended/valid
training positions. Matched training cohort is 42 shots/168 suffix positions,
165 with qualified mass prefixes. PRED: 24 physical shots; q1 24, q2 24 conditioning
inputs at evaluation and 96 evaluation targets. Total frame 270 FIT +144 PRED
positions; 411 source-valid +3 invalid spills. FIT-E03-R1/E11-R3/E14-R3 q2 source
zero assignments remain INVALID_SPILL, not nondetects. Valid zero assays remain
separate. Preparations, standards, injections, fraction observations and shots are
not interchangeable replicates. Report intended/source-valid/inspected and each
component's assessable/unassessable counts by role; flagged is a subset, not an
extra observation. Analytical eligibility does not require model mass-prefix or
feature-domain support.

**Controls/material.** Inspect source-linked text, comments, metadata and relevant
ranges for standard purity/isomer, blanks, recovery, LOD/LOQ, repeated injections,
batch and roast/lot keys. A repeat column header without values is not replication;
a zero chart point is not a blank measurement. No probabilistic uncertainty is
estimated without eligible independent control evidence. Author roast attribution
remains attribution. No same-lot join from product names/dates/UNKNOWN. Primed
whole-sample bookkeeping stays outside scope unless explicitly necessary.

Stop after this finite queue is disposed. Report inspection completion separately
from scientific disposition, including smallest missing records. Preserve all
historical thresholds, models, observations, masks, support, decisions and rights.
Pannusch/Schmieder remain one lineage; source-derived evidence retains
CC-BY-NC-3.0 / DOI 10.17632/y2tz67f6ry.1 separately from software licensing.
Private details remain external with hashes and executable reproduction commands.

Method-audit clarification before execution: PRED CGA I11/I25 are blank. The
source formula's spreadsheet blank-as-zero convention can be reproduced, but the
raw weighed-water entries remain missing and are not independently verified zero
additions. The two chart trendlines display the same series and create no extra
standards or independent regressions.
