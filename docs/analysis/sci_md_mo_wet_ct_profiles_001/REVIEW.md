# Independent substantive review — SCI-MD-MO-WET-CT-PROFILES-001

**Disposition: acceptable after one bounded factual correction; no unresolved
material scientific finding.** Reviewed 2026-10-24 by the separate nonhuman
review agent, against the frozen PLAN.md and accepted base
`13c750c7d08d1fc868e24ad500dced5fb34127e4`. This is the requested single
substantive review, not physical validation or approval to merge.

The final reviewed substantive identities are the 46 SHA-256 entries in
[independent_review_receipt.json](independent_review_receipt.json). That receipt's
SHA-256 is `d95cdf1e5392f1e72fbccd6a88feef8389fa33564ac1fabd9a5f05d98844056e`.
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
previous 44 bound files and all substantive scientific review evidence are unchanged.

## Finding and disposition

**R1 — corrected numerical audit fact.** SOURCE_NOTES.md initially stated twice
that every native segment had dx >0.127 pt. Independent inspection of the original
PDF paths found a minimum of **0.11798095703125 pt**. The producer corrected both
statements to **>0.117 pt**, and the reviewer verified the final text. The revised
denominator bound still supports the arithmetic guard. No scientific code, data,
calibration allowance, window, result, or figure changed for this correction.
This was a real factual defect, not an objection to conservative bounds; it did
not invalidate the computed enclosures or alter any classification.

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

This checker imports neither the scientific producer nor its extractor and does
not call producer tests. It reads original PDF segments, independently integrates
them with exact rational arithmetic, and separately computes all **35 supported
within-panel enclosures** in extended precision (63 stored mantissa bits), then
checks the **12 cross-panel differences**. It checks all 48 unique request IDs and
classifications, and all supported diagnostic means. Maximum nominal-contrast
disagreement was 2.23e-16; maximum mean disagreement was 5.04e-16. Every independent
enclosure lies inside the delivered guarded enclosure. The maximum difference
between the observed guard expansion and 1e-7 was 7.48e-16.

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
gamma <0.0028. The stated 10,000-operation/1e6-intermediate forward-error estimate
is about 6.22e-9 signal units before the larger 1e-7 guard; the outward coordinate
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
