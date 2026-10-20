# 5-CQA provenance: source conflicts found; cause of model bias unresolved

**Three FIT dilution-quantity conflicts are demonstrated. Both original CGA
calibration regressions reproduce their reported coefficients. The inspected
records cannot identify how much, if any, of the retained FIT/PRED discrepancy
comes from these conflicts, calibration applicability, recovery, material or
predictor error.** No accepted observation or model is changed.

SCI-MD-5CQA-OBSERVATION-PROVENANCE-001 · GOVERNANCE_CLASS=G1 ·
NO_GOVERNING_PHYSICS_CHANGE · RESEARCH_ONLY · RETROSPECTIVE · TARGET_EXPOSED ·
SOURCE_INTERNAL · PHYSICAL_VALIDATION=NOT_ESTABLISHED.
ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED; no narrowly quantified uncertainty
component was earned.

## What was inspected and what was reused

All eight ASSAY-002 originals match their accepted SHA-256 identities. New work
inspected every worksheet name/visibility, defined name, workbook relationship,
explicit formula reference and textual annotation in the four workbooks;
CGA stock/working-standard tables and their linked calibration chart; the
414 fraction-position sample identities and dilution/preparation relationships;
and the two MATLAB preprocessing texts. MAT container metadata was read; the
accepted numerical-array checks were reused. Neither MATLAB script was executed.

The four books contain **43 sheets**, all visible: HPLC FIT 20, HPLC PRED 11,
and DoE FIT/PRED six each. Both DoE books have a hidden filter defined name.
The complete sheet lists are in [SOURCE_AUDIT.json](SOURCE_AUDIT.json). This
inspection includes nonnumeric sheets excluded by the historical source_books
helper, whose behavior remains unchanged. Only the declared relevant numeric
ranges were reduced. Other analytes, experiment 46, primed/full-sample records
and telemetry references were disposed at the metadata boundary.

One FIT HPLC external relationship points to an author's Windows workbook. Its
embedded link metadata was inspected: the cached CGA sheet is empty, while the
populated cache concerns experiment 46, outside this observation frame. The
referenced original is unavailable at its explicit locator here. No substitute,
unbounded search or inference of nonexistence was made. There were no original
hash mismatches. Two initial FIT parser diagnostics concerned an unused nominal
header and out-of-frame source blocks; both were resolved without changing
source bytes or scientific rules. The final reduction has no parsing failures.

**Execution/inspection dimension:** all eight named originals and the relevant
internal reference scope were inspected at the levels above. The complete finite
scope is **PARTIALLY_INSPECTED**, because one explicitly referenced external
original is unavailable. Its relationship remains unassessed; this is not a
corpus-exhaustion finding.

The [protocol ledger](PROTOCOL.md#completed-worknew-work-ledger) and hashed reuse
records identify completed work: species/column mapping; campaign-specific
HPLC formula/cache/MAT agreement; all 69 q1 and 66 valid q2 assays; all 180 FIT
and 96 PRED suffix values/formulas; vial-mass support/exclusions; #340 residual
decomposition and physical-shot deletions; and October 1 C01 preparation work.
Those computations and historical review stages were not repeated. C01's 18
preparation checks concern three March shots, six fractions and caffeine/
trigonelline. Newly inspected common T/V/Y references to the same sample-row C
entry explicitly extend that preparation relationship to 5-CQA; they do not
extend C01's independent scope to every other shot.

## Calibration origin and applicability

The accepted mapping remains **MATLAB cAlcaloids(:,3) → response I → analyte
mass Y**, not CQA_sum. Source CGA/Chlorogenic acid labels are interpreted through
that accepted mapping; they do not independently certify the standard's isomer
or purity. CGA stock rows contain weighed solute and water, and working-standard
rows contain aliquot and dilution-water quantities. The chart explicitly links
its concentration and response series to those tables.

| Campaign | Recorded stock preparations | Prepared nonzero standard records | Chart pairs used once | Source chart linear response equation, reproduced at displayed precision |
|---|---:|---:|---:|---|
| FIT | 2 | 10 | 10 | area = 24.513 × source mg/kg + 78.923 |
| PRED | 2 | 12 | 13 | area = 26.383 × source mg/kg − 88.067 |

The source uses response-on-concentration linear trendlines with a free intercept
and the populated points in its declared series; there is no encoded weighting
or additional exclusion. Two displayed trendlines share each series and are not
replicates. All four stock formula caches and all 22 working-standard formula/
chart mappings agree. The FIT chart's three blank positions remain absent. PRED's
additional zero/zero point is retained as encoded; its physical origin is
unresolved and it is **not established as a measured blank**. The PRED second
response column is empty, so its header supplies no repeat-injection evidence.

PRED has two blank working-water entries. Reproducing the spreadsheet's
blank-as-zero arithmetic does not establish physically recorded zero additions.
Stock formula concentration uses **water mass** as denominator; the source also
contains an mg/L=mg/kg annotation. This is a source convention and unresolved
basis qualification, not permission to invent density or replace the denominator.
No standard purity certificate, independent balance record or actual standard
injection identity was located in the inspected ranges.

| Support concept | FIT | PRED |
|---|---|---|
| Nominal nonzero target standard interval, source mg/kg | 25–400 | 5–400 |
| Prepared nonzero interval, source mg/kg (rounded aggregate endpoints) | 25.1138–399.6363 | 5.85036–409.5659 |
| Encoded chart response interval, source mV min/10 | 647.369–9488.070 | 0–10833.027, including unassigned zero point |
| Explicitly validated analytical range | Not established | Not established |
| Explicit standard-to-sample analytical batch/applicability link | Not established | Not established |

Regression reproduction traces the numerical origin of both equations. Matching
coefficients and co-location do not independently assign those standards to the
sample injections. Consequently **all 411 source-valid positions have unassessable
response-support and diluted-concentration-support classifications**. Below,
within and above counts are null with that reason, not zero observations in those
classes. No old assay calculation was rebuilt just to attach unavailable range
flags. A future eligible support comparison would include both endpoints and
would keep response and diluted concentration checks separate. It would not
establish accuracy or recovery, nor identify the size of an extrapolation error.
Different FIT/PRED equations alone are not a defect.

## Independent preparation quantities and actual roles

Within each campaign the source's No./Fr. preparation keys, ExpSheet shot keys,
HPLC sample labels and accepted Y-to-I row references cover all **414**
positions with unique preparation-key matches. There are **412 exact sample-label
matches** and **two source-declared invalid positions whose labels retain a
`(broke)` annotation**. The strict parser preserves those two label mismatches;
the accepted spill identities, rather than stripped arbitrary annotations,
establish their invalid status. This is a documentary
sample/preparation join; no analytical injection or calibration batch identifier
was found. DoE IST water/coffee quantities are distinct from whole vial mass and
dry-coffee dose. The documented rule is `(water_g + coffee_g) / coffee_g`.

| Campaign / role | Intended | Source-valid | Newly inspected position identities | Preparation assessable | Unassessable | New quantity agreements | Reused C01 arithmetic | Flagged quantity conflicts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FIT q1: development conditioning | 45 | 45 | 45 | 45 | 0 | 44 | 0 | 1 |
| FIT q2: development conditioning | 45 | 42 | 45 | 42 | 0 | 41 | 0 | 1 |
| FIT 3/5/7/10: training targets | 180 | 180 | 180 | 180 | 0 | 179 | 0 | 1 |
| PRED q1: evaluation conditioning | 24 | 24 | 24 | 24 | 0 | 21 | 3 | 0 |
| PRED q2: evaluation conditioning | 24 | 24 | 24 | 24 | 0 | 21 | 3 | 0 |
| PRED 3/5/7/10: evaluation targets | 96 | 96 | 96 | 95 | 1 | 83 | 12 | 0 |
| Total | 414 | 411 | 414 | 410 | 1 | 389 | 18 | 3 |

Assessable = new agreements + reused agreements + conflicts; flagged conflicts
are a subset of assessable. The three invalid FIT q2 spill positions are outside
the source-valid/assessable denominator, not unassessable valid assays. Their
source-assigned zeros remain invalid, never nondetects. The accepted 5-CQA exports
contain no valid-zero values in this frame; valid-zero semantics remain distinct
and are exercised synthetically. There are **69 physical shots**, not 414
independent experiments or extra shots for each model/role.

All three conflicts are mismatched water quantities in source records, with the
coffee quantity agreeing. Their exact source cells, values and conditional
multipliers are private. One affects a valid original FIT q1, but that shot is
already outside the matched 42-shot cohort because of its q2 spill. The other two
affect a retained FIT q2 conditioning input and a retained fraction-3 training
target. If the DoE quantities were authoritative, the documented dilution rule
would multiply the associated beverage concentration and analyte mass by the
private diagnostic ratio; **which source entry is correct is not established**.
The conditional changes span roughly −0.026% to +5.21% across the three conflicts.
This is a source-value diagnostic, not an analytical uncertainty interval,
corrected measurement series or model-performance result.

One PRED suffix position has a recorded water quantity but no recorded coffee
aliquot quantity. Its HPLC dilution number exists, but independent preparation
arithmetic is unassessable. No missing quantity is inferred from that number.

Agreement in the other records narrows documentary dilution-transcription
concerns within the inspected scope. It does not establish that a balance was
accurate, a vial contained the intended material, extraction recovery was complete,
or an injection was correctly identified. The same shared preparation may affect
several analytes; it is not independent evidence each time.

Analytical preparation eligibility is independent of predictor support: the
original 45 FIT shots remain, with the matched 42-shot/168-target cohort and its
165 qualified measured prefixes unchanged. All 24 PRED shots and 96 suffix
positions remain, including the existing unsupported mass-domain interval and
all feature-extrapolation/adverse-panel flags. No new analytical exclusion changes
those historical masks or decisions.

## What the evidence distinguishes

Private locator keys below refer to the bound evidence directory label
`5cqa-observation-provenance-001-private`; actual paths and individual joins are
excluded from Git. `E-CAL`, `E-PREP`, `E-ID`, `E-CONTROL` and `E-REF` are exact
sections in its `SOURCE_LOCATORS.md`; source hashes and reduction hashes are in
[SOURCE_AUDIT.json](SOURCE_AUDIT.json) and [RESULTS.json](RESULTS.json).

| Explanation | Inspected evidence; new/reused; private locator | Demonstrated inconsistency and affected roles | Disposition and remaining confounding | Smallest specific missing evidence that could change it |
|---|---|---|---|---|
| Calibration mapping or applicability | Reused I/Y/cAlcaloids mapping and all accepted assay reconciliation; new CGA stock/working inputs and chart2, E-CAL | No regression mismatch; physical purity/basis and PRED zero-point origin unresolved; both campaigns/all roles | Numerical equation origin traced; batch applicability/range unassessable. Standard accuracy and matrix effects remain inseparable | Injection sequence or analytical batch sheet explicitly linking these standards/equations to the FIT/PRED sample IDs; standard identity/purity/preparation record for accuracy |
| Dilution/sample preparation | New DoE IST quantities→HPLC C joins, with 18 C01 arithmetic checks reused and common 5-CQA C reference newly inspected, E-PREP | Three FIT water-entry conflicts across q1/q2/target; one missing PRED aliquot mass | Specific documentary inconsistency supported; uniform offset not established. Correct side and predictive effect unknown; shared input/target dependence retained | Original weighing/preparation record resolving each conflicting water entry; the missing coffee aliquot entry for the single PRED position |
| Recovery, blanks or censoring | New relevant workbook text/chart/standard-column inspection; reused spill semantics, E-CONTROL | No eligible recovery/LOD/LOQ/blank or repeat-injection record located; zero chart point has no blank identity | Unassessable; no uncertainty allowance, no relabelling zeros/spills as censored; absence of detected defect is not accuracy | A source-linked control result plus its method/batch/sample population; identity of the PRED zero chart point |
| Material/campaign differences | New DoE/sample text inspection; reused campaign identities and unresolved lot/roast register, E-ID | No explicit lot/roast batch relation established; dates/product names do not join | Campaign difference remains possible and inseparable from analytical/predictor causes. Author roast explanation remains attribution | Lot/roast batch ledger mapping the actual FIT and PRED physical shot sample numbers |
| Predictor error or extrapolation | Reused ASSAY-002 and #340 inadequacy, bias decomposition, deletions and extrapolation; new preparation conflicts mapped to roles, E-PREP/E-ID | No corrected predictor evaluated; retained input and training-target conflicts could interact with learned parameters | Historical inadequacy stands; predictor contribution is not isolated by assay agreement or lack of controls. No additive correction follows | A qualified assay/preparation/batch bridge resolving the named observations; only then could a separately authorized model investigation separate contributions |

Workbook/MAT agreement is not independent assay-accuracy evidence. A verified
provenance chain would still not exclude every matrix/recovery error. Within-range
support would not prove accuracy; an out-of-range flag would not prove a cause of
bias. Residual decomposition supplies no common additive correction. Failing to
find another analytical defect would not prove predictor error.

**Scientific dimension:** specific new source inconsistencies coexist with traced
numerical calibration provenance and unresolved applicability/control/material
components. The bounded attempt is complete. It does not solve the broader T09
chemistry question or authorize another search, source acquisition, fit,
correction campaign, laboratory task or author contact.

[Protocol](PROTOCOL.md) · [machine results](RESULTS.json) ·
[method audit](METHOD_REVIEW.md) · [handoff/reproduction](HANDOFF.md).
Pannusch/Schmieder remain one source lineage; Mendeley DOI 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0 for source-derived evidence, separately from software licensing.
