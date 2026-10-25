# Independent substantive review — SCI-MD-MO-WET-CT-PROFILES-001

**Disposition: acceptable after bounded corrections; no unresolved
material scientific finding.** Reviewed 2026-10-24 by the separate nonhuman
review agent, against the frozen PLAN.md and accepted base
`13c750c7d08d1fc868e24ad500dced5fb34127e4`. This is the requested single
substantive review, not physical validation or approval to merge.

The final reviewed substantive identities are the 46 SHA-256 entries in
[independent_review_receipt.json](independent_review_receipt.json). That receipt's
SHA-256 is `79d088c376e6513672592ae6d041baf19ca4ca52fade3135ccc81c455551e3a2`.
It binds the producer, extractor, canonical data/metadata, frozen plan, results,
figures/crops, source notes, tests, affected cards/protocol, and discovery files.
Verification/hosting receipts and this review are excluded from that substantive
identity set; later receipt-only changes may reuse unchanged evidence.

The review checker subsequently received a bounded portability correction:
source and receipt paths are explicit command-line arguments, and protocol
comparison/change enumeration use the fixed accepted base above. This preserves
the same scientific checks after commit and lets replay leave the historical
receipt untouched. That correction changed only the review tool. A subsequent
serialization-only cleanup used
LF CSV line endings and removed SVG line-end whitespace. The reviewer independently
verified saved originals against the prior hashes, exact CSV CRLF-to-LF equivalence
and parsed-row equality, exact SVG per-line whitespace removal, unchanged contrast
JSON, metadata equality except the canonical CSV hash, and summary equality except
input identities. Reversing only the declared serialization edits in the producer
and extractor recovers their prior reviewed hashes exactly. The scientific review
evidence is reused; affected file identities are rebound in the final receipt.

The generated CLAIM_BINDING_AUDIT.md/json correction was also checked against
the accepted base: only the source-commit identity and Paper 3 input fingerprint
changed, with all claim text and numbers unchanged. The fingerprint matches the
reviewed Paper 3 bytes. Both audit files are added to the final binding set; the
previous 44 bound files and all substantive scientific review evidence were unchanged
for that generated-identity correction.

## Finding and disposition

**R1 — corrected numerical audit fact.** SOURCE_NOTES.md initially stated twice
that every native segment had dx >0.127 pt. Independent inspection of the original
PDF paths found a minimum of **0.11798095703125 pt**. The producer corrected both
statements to **>0.117 pt**, and the reviewer verified the final text. The revised
denominator bound still supports the arithmetic guard. No scientific code, data,
calibration allowance, window, result, or figure changed for this correction.
This was a real factual defect, not an objection to conservative bounds; it did
not invalidate the computed enclosures or alter any classification.

**R2 — bounded numerical portability correction, verified.** The producer's
alternate-BLAS regression exposed last-bit dependence in nominal dot products.
The correction replaces the three BLAS reductions with scalar binary64 products
and `math.fsum`; the reviewer inspected the cancellation/forbidden-BLAS test and
alternate-kernel subprocess regression. Comparing saved, hash-authenticated
pre-correction artifacts independently confirms that only 33 nominal contrast
estimates changed (maximum 2.776e-17) and 12 diagnostic means changed (maximum
1.111e-16). All other request fields, bounds, support and classifications are
unchanged. RESULT.md, summary.json, and both rendered figure formats retain their
reviewed bytes. Canonical data, calibration, graphical allowances, and continuous
interval code are unchanged. Source/membership/mask/continuous-bound/visual
evidence is reused within this same bounded review.

The independent exact-source checker was replayed for the corrected nominal
values. A separate exact-rational audit, now retained in the same checker, of all
94 actual nominal/mean reductions
also confirmed that each `fsum` result correctly rounds the exact sum of its
binary64 products. With unit roundoff u=2^-53, each reduction's error is bounded by
u times the sum of absolute exact products plus u times the absolute sum of the
rounded products. The maximum product norm was 7242.114 and the maximum
signal-scaled bound was 1.302e-16. This argument does not assume an internal
operation count for `fsum`; it leaves the 1e-7 guard ample for the unchanged
weight/integration arithmetic. No allowance or sign was retuned.

## Sources, membership, and display support

The reviewer read AGENTS.md, CLAUDE.md, onboarding, the relevant data/governance
guidance, PLAN.md, source notes, implementation, results, affected claims, and
protocol changes. The three external originals were independently opened and
rehash-verified: final 15-page publication, 18-page arXiv v2, and seven-page final
supplement. Their hashes are recorded in the receipt. Final pp.3–5 and 11–13
confirm the dry reference-porosity threshold, distinct wet peak-midpoint threshold,
liquid/solid limitation, annular measurement regions, two capsule histories, and
the medium/three-days versus dark/immediate timing. The supplement contains SPH
methods/parameters and enlarged sections, not additional numerical 1/24-hour
profiles. Those delays remain narrative-only here.

The journal date and v1/v2 chronology were separately checked against the
[publication record](https://pmc.ncbi.nlm.nih.gov/articles/PMC10541431/) and
[arXiv history](https://arxiv.org/abs/2305.03911). Final p.15 supplies CC BY 4.0;
neither selected figure/caption has a separate credit-line exception. Retained
attribution, modification descriptions, and license link are appropriate.

Independent PDF parsing authenticated all **12,494 line segments**, their native
endpoints, increasing orientation, original subpaths, paint order, six unique
stroke/legend colors, and all intermediate tick locations/widths. Each panel has
the six printed radii, giving **24 annular profiles from two histories**. Original
arXiv geometry agrees within 8.46729e-5 mm horizontally and 4.06440e-6 signal
units after separate calibrations; it is not counted as new evidence.

The independently inspected PDF clip stack confirms the extra delayed-central
clip. The legend is an opaque white fill painted after the curves. Its full
border-expanded rectangle is an acceptable conservative mask. All visibility
pieces were checked against original geometry. The three central subpath gaps
are retained. Full-calibration/local-box support was independently checked for
every requested band: only `post_late_14b_r0.92` is unsupported. Its missing
estimate/bounds correctly reflect legend occlusion, clipping, and a source gap;
hidden PDF coordinates supply no displayed-evidence integral. All other requested
bands retain support throughout the allowed set, not merely at nominal anchors.

## Independent numerical execution

Executed successfully with the separate supplied Python/PyMuPDF environment:

```sh
/tmp/mo-wet-ct-venv/bin/python \
  docs/analysis/sci_md_mo_wet_ct_profiles_001/independent_review_check.py \
  --source-dir "$SOURCE_DIR" \
  --receipt-output /tmp/mo-independent-review-replay.json
```

The source/geometry, exact-integral, and enclosure oracles do not use producer
functions or the extractor and do not call producer tests. They read original PDF
segments, integrate them with exact rational arithmetic, and separately compute all **35 supported
within-panel enclosures** in extended precision (63 stored mantissa bits), then
check the **12 cross-panel differences**. They check all 48 unique request IDs and
classifications, and all supported diagnostic means. Maximum nominal-contrast
disagreement after R2 was 2.36e-16; maximum mean disagreement was 4.78e-16. Every independent
enclosure lies inside the delivered guarded enclosure. The maximum difference
between the observed guard expansion and 1e-7 was 7.48e-16.

R2 adds an explicitly separate reduction audit that imports the producer only to
obtain its actual weight vectors and `deterministic_dot` outputs, then checks
scalar-product and summation errors against exact Fraction arithmetic. The receipt
discloses this limited producer use and retains the 94-reduction audit metrics;
the independent source/integral/enclosure oracles remain unchanged.

The mathematical inspection supports the implementation: partial-segment
trapezoid integration includes the affine Jacobian; common ordinate offsets and
reused band terms cancel before uncertainty relaxation. For uncertain horizontal
reading/calibration, interpolation weights remain nonnegative with unit band
sum, so the uniform vertical box bound is valid without freezing nominal weights.
The 4×4 closed calibration-box cover and 256 full-width y cells enclose continuous
sets: inverse-map corner extrema and PL endpoint/all-interior-vertex extrema
bound each cell integral. Multiplication by the positive ordinate-scale interval
and independent-panel subtraction are valid outer operations. They need not
produce jointly attainable endpoints. This deliberate conservatism is acceptable,
and a grid of sampled extrema has not been substituted for a continuous proof.

The reviewer independently checked the stated coordinate/slope/denominator
bounds with R1 corrected: maximum coordinate <545 pt, maximum absolute slope
24.600186, horizontal separation >164 pt, vertical separation >144 pt, and maximum
gamma <0.0028. The 10,000-operation/1e6-intermediate estimate for the unchanged
weight/cell-integration arithmetic is about 6.22e-9 signal units before the larger
1e-7 guard; R2's separate product/sum bound covers the changed reduction without
counting `fsum` internal operations. The outward coordinate
pad and final endpoint expansion are retained. The extended-precision replay is
corroboration, not the sole reason the continuous enclosure is valid.

## Scientific claims, protocol, and figures

All 48 classifications independently agree: **33 positive, 10 negative,
4 sign-unresolved, 1 unsupported**. Immediate/dark primary and late contrasts
are positive at all six radii. Delayed/medium primary contrasts have four positive,
one contrary central ordering, and one unresolved ordering. Its late sensitivity
has four positive, one negative at 2.77 mm, and an unsupported central request.
Immediate/dark changes of the primary contrast are all positive;
delayed/medium changes have four positive and two unresolved signs. Adverse and
missing results are retained, not replaced by equality claims.

The exact rational witness independently returns the same (3/25, 2/25) signal
with porosity contrasts +2/25, 0, and −2/25, with all physical ranges satisfied.
It establishes nonidentification under its stated favorable idealization; it is
neither a fitted observation model nor an assertion that Mo measures gas volume.
The results appropriately withhold geometric-porosity ordering/change, mechanism
identification or exclusion, monotonicity, whole-bed weighting, and population
inference. The display-coordinate differences do not establish material
registration or a common wet/dry operator. Roast, capsule, and delay remain
confounded. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

Protocol 4 correctly separates solid occupancy from geometric void fraction and
withdraws its standalone mechanism verdict. The reviewer independently verified
the entire Protocols 1–3 section is byte-identical to the accepted base. The
dependent decision/table wording is appropriately narrowed. Cards, provenance,
manifest, and discovery retain the new dataset's signal-only ceiling; the new
dataset has no geometric-porosity/permeability measurement edge. Old numerical
records and evidence-strength labels remain unchanged; the existing manifest
rights cell receives the final-publication correction. The dated external census
is unchanged, and manuscript count changes reflect one new manifest record.

Both original-panel crops were regenerated directly from the authenticated final
PDF and matched the committed bytes. The reviewer visually compared those panels
with COMPARISON.png and the standalone COMPARISON.svg rendered in headless Chrome.
All four profile panels, six memberships, the central delayed rise and tiny visible
fragment, masks, fixed bands, and all 48 summary rows agree. Missing portions stay
missing. The plot labels its bounds as graphical, not experimental error bars.

No runtime, governing-physics, EWP, source-window/tolerance, or successor change
is introduced. Ordinary test/CI disposition belongs to VERIFICATION.md and the
live checks; this review does not convert their outcome into scientific authority.
