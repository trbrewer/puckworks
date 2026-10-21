# Independent scientific review

**Disposition: accepted for the declared partial figure-reading analysis and
conditional hydraulic interpretation. No material scientific finding remains
unresolved. PHYSICAL_VALIDATION=NOT_ESTABLISHED.** This is not an approval of an
unqualified run-level trend, physical mechanism, runtime model or merge.

Reviewer: the separate `scientific_review` agent, acting as the one independent
scientific reviewer requested for SCI-MD-MELROSE-TRANSIENT-HYDRAULICS-001. The
reviewer did not author or edit the implementation, source transcription or
results, and spawned no further reviewer. Only this review record was written
to the repository. Source and candidate review began **2026-10-21 14:15:00 UTC**;
final scientific assessment and candidate-hash verification completed
**2026-10-21 14:31:29 UTC**. The subsequent administrative count-only delta
was inspected at **2026-10-21 14:33:18 UTC**, completing the review. This is a
retrospective, target-exposed review.

## Exact reviewed candidate

The reviewed scientific candidate is the 20-file SHA256 mapping in
[SCIENTIFIC_CANDIDATE.json](SCIENTIFIC_CANDIDATE.json), frozen at
2026-10-21T14:30:38.674764+00:00. Its SHA256 is
`2dbf237b78b4f9e747bf5eb52e8ba78ece1fa47e9d4c6903c196f566a0650a84`.
The reviewer independently recomputed the manifest hash and **all 20 of 20
mapped file hashes**, with exact agreement. The mapping includes the plan,
source reconciliation, contract, coordinates, profile and ambiguity records,
normalized observations, results, implementation, tests, card and integration
producers. Implementation base is
`58075bbbce548e63d94106c96b918c1464221514`.

The plan's SHA256 is
`ba842af502b76aa3d79e145904d7260a1656d03aee7a3e60cf7d83e9aefa8e95`.
The reviewed RESULT.json SHA256 is
`d24d61d96935d1a8a3a52ea56b80c2f5690b840a57998b3a6e5f2c8652d389c9`.
The later commit binding and software/hosted-CI evidence belong in
[VERIFICATION.md](VERIFICATION.md). Adding that administrative evidence does
not alter this reviewed scientific identity; any scientific-file change must
be evaluated against the mapping rather than silently inheriting this review.

## Sources, identities and coverage

The reviewer independently hashed the held originals. The preprint matches
`20b7990af4a9026b44d56a29b559ab0d02f4a094d5a3e171b8d1bb41ae58c6ed`
and has 29 PDF pages; its title page says 26 September 2019. The thesis matches
`f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818`
and has 359 PDF pages. PDF metadata and `pdfimages -list` independently confirm
the Figure 2 JPEG at PDF/printed p.11, object 29, native 957 by 678 pixels.
The originals, extracted figures and inspection crops remain outside Git.

Direct inspection covered preprint methods pp.3–4, Figure 1a/b and its caption
pp.9–10, Figure 2 and accompanying text pp.10–12; thesis printed pp.63,65,90,
273–276 / PDF pp.88,90,115,298–301, including apparatus, outlet-observer and
Table 7.1 images. Source URLs and exact page mappings are correctly preserved
in the reconciliation record. The accepted EWP result was read with `git show`
at `aace2cc6b6c2a393d2dbfb0274104192ca6c7203`; no EWP file was changed.

The Figure 1 convention supports B triangles, C squares, D diamonds and E
circles, with open 480 and closed 400 symbols. Figure 2 has two open-looking
LF triangle tracks, so assigning one to each density would invent a resolution
the image does not supply. Four disconnected triangle fragments and explicit
candidate identities are appropriate. Heavy LF overlap does not support an
eight-by-eight marker count or a complete C400LF series. The retained C400LF
singleton, bounded partial C480LF squares and unjoined triangular fragments
avoid those inventions. HF B480 is not separately distinguishable; its absence
from thesis Table 7.1 does not prove absence from the later preprint.

The ledger correctly distinguishes **16 intended conditions, at least 12
distinguishable traces, 14 recovered fragments, 10 uniquely condition-assigned
profiles and 57 retained observations**. Seven observations belong to the four
unassigned triangle fragments and are not credited to both candidate conditions.
The total source-profile count and obscured-point count remain unknown. No
additional unambiguously identifiable marker was found omitted in the source
inspection. Connecting lines and wholly obscured centers were not used as data.

The thesis and preprint share campaign provenance. In particular, thesis
Figure 7.1's LF E presentation is visibly different from the preprint's circle
traces: it cannot fill hidden preprint points or provide an extra scored sample.
The narrow Melrose-to-Corrochano campaign alias in the existing denominator
producer correctly prevents a second campaign credit. The associated generated
draft-table change is only manifest records 118 to 119; four matching numeric
references in the existing prose were corrected after the candidate freeze as
dependent count metadata. The reviewer inspected that delta: campaign count
remains 46, no scientific argument changed, and no mapped scientific file was
changed by this administrative correction.

## Reading bounds and every load-bearing witness

The native axis anchors and internal ticks support the stated affine
calibration. Full visible-glyph footprints, a one-native-pixel raster guard and
shared anchor ranges of plus/minus one pixel give defensible conservative
enclosures. Null centers at identifiable overlaps preserve visible-marker
evidence without estimating hidden centers. The source rectangles and common
calibration parameters are retained, and their rectangular outer relaxation
is distinguished from a jointly admissible reading. Neither enlargement of
the inspection image nor the thesis density approximation is treated as added
measurement precision or independent pointwise experimental uncertainty.

The reviewer checked the retained source boxes and all attaining maximum
decline/increase witness locations against the original figure and native-pixel
crops, including the points used by every reported shared-trough triple. The
eight resolved declines and six resolved increases are supported by those
enclosures and within-fragment displayed order. The largest decline is
HF-E480-x122 to HF-E480-x368, **2.3020408163265302 mL/s**; the largest increase
is HF-C480-x204 to HF-C480-x368, **1.9102040816326529 mL/s**. HF-C400,
HF-C480 and HF-D480 have respectively 14, 11 and 8 qualifying shared-trough
triples. Their point identities and bounds agree with the source images; the
33 triples are overlapping comparisons, not independent events.

The LF late-upper increase of **0.012244897959183376 mL/s** leaves only a
one-native-pixel gap under the declared enclosure. Its explicit qualification
as small and reading-contract dependent is necessary and is present. The
LF early-lower decline of **0.03673469387755102 mL/s** is likewise small.
Neither is assigned a density or joined into an LF recovery curve. A lack of
resolved recovery in the other partial profiles is not evidence of its absence.

## Mathematics, independent computation and reproduction

The nondecreasing predecessor-lower-maximum witness, nonincreasing
successor-lower-maximum witness and constant-intersection criterion are correct
for the declared finite partial-order problem. All comparable pairs, including
transitive relations, are used. Each expanded pair gap is reduced by twice
delta, proving the reported half-gap minima; the retained expanded witnesses
provide sufficiency. Invalid intervals/centers, equality, deterministic ties,
singletons, no-data and order-free cases receive the appropriate treatment.

The reviewer separately formulated linear programs with variables q_i and
delta, constraints q_i-delta <= u_i, -q_i-delta <= -l_i, order inequalities
and, for a constant, equalities q_i=q_1. This calculation read the retained
intervals and order pairs without calling the producer's compatibility or
expansion formulas. **All 42 profile/hypothesis LP optima agreed**, with maximum
absolute difference **2.220446049250313e-16 mL/s**. An independently formulated
LP using only the adjacent order inequalities for [2,3], [0,3], [0,1] and
1 before 2 before 3 gave delta=0.5 with witness [1.5,1.5,1.5], confirming the
load-bearing transitive constraint. All 42 actual expanded witnesses were
also checked against their enclosures and every supported order pair; the
1e-14 verification tolerance addressed arithmetic roundoff, not verdicts.

Independent execution used Python 3.12.3 in the existing evidence-directory
virtual environment:

```bash
python -m puckworks.analysis.melrose2019bed_transient --output /home/tim/Documents/melrose-transient-001-evidence/reviewer-reproduction
python -m pytest -q tests/test_melrose2019bed_transient.py
```

The actual interpreter was
`/home/tim/Documents/melrose-transient-001-evidence/venv/bin/python`.
All four generated CSV/JSON outputs reproduced byte-for-byte. The final focused
run passed **22 tests in 0.53 s**, including the campaign-alias regression.
Earlier inspection commands needed two harmless retries: the shell lacked a
`python` alias, and an observation-file read preceded its move to the final
dataset path. Neither was a failed scientific calculation. Producer-reported
ordinary repository checks and hosted CI are separate evidence, not inferred
from these reviewer checks.

Counts independently agree: 121 strict comparable pairs, 162 supported chains,
12 temporally informative fragments and two singletons. Within the informative
set, up/down/constant exclusions are 8/6/11; not-excluded counts are 4/6/1.
Feasibility remains only non-exclusion by the rectangular relaxation. No
joint-calibration feasibility claim is made.

## Observation, aggregation and hydraulic scope

The preprint directly supports aliquot-volume/collection-duration ordinates
and first-drop time zero. Thesis methods support weighed aliquots, approximate
water-density conversion and 5/10-second HF/LF sampling in the shared campaign.
They do not establish the exact displayed interval endpoints or a plotted
end/midpoint convention. Figure 1's repetition count and sample SD, and the
thesis's general statistical wording, do not establish Figure 2 pointwise
replicate membership or fixed weights. The unspecified-aggregate status is
therefore correct. The proofs for unequal-duration successive interval averages
and fixed nonnegative replicate weights are correct; changing duration shares
in a ratio of summed volumes/durations require their own check.

Pressure constancy, pressure value and pressure-node identity are correctly
separated. The preprint's 1.75/3.75-bar assignment and thesis grind/density-based
tank selection remain unreconciled. The regulated tank, pre-cell transducer and
bed drop are not silently equated. Early inlet/outlet disagreement due to
filling and absorption, and the reported outlet thermal transient, prevent
unqualified storage-free or isothermal inference. The decisive early observations
are explicitly related to the reported transient without inventing a cutoff.

The fixed-topology, positive linear, quasi-static network proof is correct:
Rayleigh monotonicity implies nondecreasing K under increasing edge conductances,
and fixed bed drop then implies nondecreasing Q. The slit example correctly
requires fixed relevant constitutive factors. The separate constant-applied-head
argument correctly requires a common reference/outlet, fixed head and a
time-invariant, memoryless nondecreasing apparatus loss. Passivity alone,
unspecified nonlinear dynamics or changing storage are not claimed sufficient.

Consequently, zero recovered profiles qualify for an unconditional hydraulic
rejection under the complete observation/aggregation contract. A resolved
plotted decline contradicts the stated conjunction only when its premises are
qualified; it does not select an alternative mechanism. The report preserves
EWP #213's UNRESOLVED_BOUNDED_ANALYSIS and line-pressure NOT_ASSESSED, and makes
no cross-pressure reversal, intrinsic-permeability or physical-validation claim.

## Findings resolved within this task

Early reviewer source findings were incorporated before the scientific candidate
freeze: ambiguous LF triangle identities and dense square clusters are retained
conservatively; the differing thesis E presentation is not used as replacement
data; the small triangular margins are qualified; rectangular status is explicit
per hypothesis. Final card-only corrections distinguish preprint-reported
pressure values from established bed pressure and state the actual inlet/outlet
thermal account. All were verified in the frozen candidate. No reading bounds,
inclusion rules or numerical outcomes were tuned to obtain a preferred verdict.

The scoped scientific analysis is accepted. Software QA, required hosted CI,
draft-PR state and the final checked head remain separately reportable facts.

## QA-only delivery delta, 2026-10-21

The same reviewer inspected a bounded delivery correction from **14:56:15 to
14:59:12 UTC**. The original scientific content was committed as
`f63f3a6d307ffcad76bdac5e5ceb992a91b4dc83`; administrative verification followed
at `c553c11e8dfab4966384416501dab749d690c3fc` in draft PR #348. This addendum
accepts the QA-only delta and preserves the original scientific review.

The historical SCIENTIFIC_CANDIDATE.json is deliberately unchanged: its SHA256
remains `2dbf237b78b4f9e747bf5eb52e8ba78ece1fa47e9d4c6903c196f566a0650a84`.
The reviewer independently rehashed its mapped files. **All 19 other mapped
files remain byte-identical**; the sole mapped delta is
`tests/test_melrose2019bed_transient.py`, whose reviewed replacement SHA256 is
`abadd7448fdb785ea78c4aabfab96cdef3e0bbb56de80825979349c25e823714`.
Its historical hash remains recorded in the original manifest rather than
being overwritten. The producer, source readings, contracts, normalized data,
results, card and campaign treatment have not changed.

The test helper now passes `threads=1` to HiGHS and uses the existing repository's
specific `OptimizeWarning` filter for the forwarded native option. This matches
the existing Pannusch state-envelope/prefix solvers and avoids a conflicting
process-global HiGHS scheduler configuration. Objective, constraints, bounds,
algorithm selection, comparison tolerances and production code are unchanged;
optimizer success is still asserted. The reviewer inspected the original local
interaction log: the 22 new tests passed, then the first existing Pannusch LP
test failed. Independent execution of that same ordered combination after the
correction passed **23 tests in 0.79 s**.

The producer reported 49 hosted quick-Python-3.10 failures on the earlier head:
47 existing solver cases, a missing active-card README reference and a stale
claim audit. These are software/QA failures, not adverse scientific findings.
The reviewer inspected the corrected combined local log: **236 passed**, with
one remaining README size failure (52330 bytes versus its 52000-byte limit).
The added citation was then shortened to a linked Melrose card reference; full
source metadata remain in the card and dataset. The claim audit was regenerated,
changing its source-commit metadata and Paper3 input hash after the previously
reviewed count-only changes. Neither change alters a scientific assertion.

The reviewer independently ran the corrected Melrose plus README/governance
tests: **84 passed in 42.65 s**. Independently executed
`python tools/claim_binding_audit.py --check` reports the audit current at
`c553c11e8dfa`. The analysis command was rerun to the external
`reviewer-reproduction-after-qa` directory; **all four retained outputs remain
byte-identical**. Thus the source-image, finite-mathematics, LP-optimum and
physical-scope evidence above is reusable with the explicit test-file delta.

Disposition: **QA-only delta accepted; original scoped scientific acceptance
unchanged**. Full-suite and required hosted-CI reruns were still in progress
when this addendum completed and remain separate delivery evidence. No physical
validation, new scientific result or expanded eligibility is asserted.
