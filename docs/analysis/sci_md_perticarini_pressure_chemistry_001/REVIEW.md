# Independent review — SCI-MD-PERTICARINI-PRESSURE-CHEMISTRY-001

**Disposition: PASS for the bounded retrospective condition-summary analysis.**
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.** No material scientific or numerical
finding remains. One minor figure-label overlap was corrected within this review.

Reviewer: independent nonhuman agent `/root/independent_review`, distinct from the
implementation agent. The task and exposed checkpoints were supplied in context;
this is not a blind review, human review or independent experimental confirmation.
One review, with a bounded same-task figure correction; no review ladder or successor.

## Actual access and checks

- Read the task PLAN, new source notes, implementation, tests, complete numerical
  outputs and RESULT; reused the accepted predecessor's complete table authentication
  and duration qualification. Independently hashed both externally cached original
  PDFs; hashes equal the supplied identities. Extracted thesis PDF97–103 and Egidi
  PDF6 anew with pdftotext. Viewed native full-page renders of thesis Tables 4.2/4.3
  and Egidi Table 2, including captions and headers. No whole intake audit repeated.
- Confirmed one decimal for TDS means in all three native tables, two for EY, and
  variable TDS SD formatting (including 0.00, 0.3 and 0.50). Confirmed prepared
  beverage-aliquot refractometry, triplicate chemical extractions, per-sample
  E_j=C_j/r_j before separate C/E averaging, and r_j=dry dose_j/beverage mass_j.
  The passages do not specify the SD estimator or authenticate raw timing/chemistry
  pairing, masses, covariance or mean-error bounds. The operator and unknowns in
  SOURCE_NOTES accurately preserve this distinction.
- Wrote a separate external Decimal parser/calculation, without importing either
  analysis producer: `/tmp/pressure-chemistry-review-arithmetic.py`. It independently
  reduced all 18 pressure comparisons (duration, TDS and EY), six original-four-cell
  interactions, coefficients, exact thresholds, conditional statuses and joint regions.
  All agree with contrasts.json. Pressure orientation and pp versus seconds agree.
  Log: `/tmp/pressure-chemistry-review-arithmetic.log`.
- Verified 30 unique original identities, 14 primary/4 secondary/6 interaction support,
  28 primary-condition coverage, all native identity fields, no imputed cells and sole
  Modœtia identity `egidi2024/table2`. All 18 duration differences/maps and allowances
  agree with the accepted predecessor. Canonical files and every predecessor bundle
  file plus its producer are byte-identical to actual base b3860d47.
- Independently checked exposed Cibao Optimal contrasts: hot (−6 s, −0.2 pp, −0.58 pp)
  and cool (−6 s, +0.3 pp, +0.19 pp); their joint opposite-TDS/shorter region is exactly
  h_tau<3 s AND h_C<0.1 pp with nonnegative allowances. Modœtia Fine/Coarse hot TDS
  bounds touch zero at h_C=0.05. Fine interaction +0.3 remains strict there while
  component opposition does not. +1 s duration touches zero at h_tau=0.5.
  Extra Fine 12−9 retains +0.1 pp TDS and −0.32 pp EY.
- Checked both extreme-grind shared-P9 cancellations in TDS and duration: composed
  norm 2; residual vector/norm/radius zero and threshold null. Printed ties remain
  distinct from structural identities and physical equality. Conditional component
  status is retained when its partner is unresolved. Exact threshold equality loses
  strict sign; rational values drive all classification, not displays or floats.
- Separate focused run: **25 passed in 2.44 s** (new and predecessor analysis tests).
  It covers exact box vertices, arbitrarily close strict boundaries, negative CLI
  inputs, joins, accounting, original-value preservation and actual plotted extents.
  Separate affected discovery tests: **9 passed in 0.21 s**. Logs are
  `/tmp/pressure-chemistry-review-tests.log` and
  `/tmp/pressure-chemistry-review-discovery-tests.log`.
- Independently regenerated all seven CLI outputs under /tmp with h_C=0.05 pp,
  h_tau=0.5 s; every CSV/JSON/RESULT/SVG matches the reviewed committed-candidate
  files byte for byte. Numerical regeneration requires no PDFs or network.
  Figure uses the existing Matplotlib extra; numerical-only mode is available.
- Viewed the final SVG through a Chrome screenshot. All 14 native-grind points,
  four coffee/temperature panels, both zero axes and conditional half-widths
  ±1 s/±0.1 pp are visible. No data jitter, regression or mechanistic curve.
  The initial Extra Coarse callout overlapped a y tick; the author moved only
  its label. Re-render confirmed correction, with numeric files unchanged.
  Final external render: `/tmp/pressure-chemistry-review-figure-fixed.png`.
- Reviewed narrow cards, manifest, capability/family producers and generated views.
  The source-convention correction to the old TDS-times-brew-ratio metadata is
  explicitly scoped in SOURCE_NOTES. Manifest remains 130 rows; only gate_use/caveat
  fields change for the two named datasets; all validation_strength fields remain.
  Insight regeneration preserves all 639 relationships and the candidate portfolio
  after removing only provenance commit fields. Its four changed entity records
  are the two card fingerprints/section lists and two dataset metadata records.
  The stable ID registry is byte-identical to base. No added campaign or strength upgrade.

## Claims and remaining limits

The contribution is the condition-level joint response that duration agreement and
per-grind range bracketing do not test. At the illustration, seven primary pairs
retain both signs: five shorter/lower TDS and two shorter/higher TDS. The other
seven rows preserve ties/unresolved components. Five of six TDS interactions retain
strict signs, which is a different claim from opposite component directions.

The total declared boxes are not measured error, rounding accuracy, SD/SE/CI or
practical tolerance. Related EY centers supply no independent confirmation or
propagated uncertainty. Shared source variables, unknown experimental uncertainty,
nominal pressure/temperature semantics and condition-only timing qualification are
carried consistently. No causal pressure effect, experimental reversal, physical
law rejection, mechanism, measured-flow relation, practical adequacy or physical
validation follows. EWP, production defaults and pins are outside the implementation;
this reviewer made no writes there. Hosted CI and full-suite completion are separate
owner-agent closeout evidence, not claimed by this receipt.

## Reviewed file identities

These hashes bind the scientific review and narrow source/discovery surfaces.
Review/verification completion text can be added without changing this science.

| File | SHA-256 |
|---|---|
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/COMPARISON.svg` | `5b8adb444fc06f5becd1e2c040d5dc30f9a6060c4596f4e04b82e6f7e23747ea` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/PLAN.md` | `2ed4517c78dbf4878da06e8288748366eae12fa22104efe3a79c7ec0fc83ab37` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/RESULT.md` | `935442e389bc4806e6904d973bc42715e8d2cdad2b5dc48ece60efd1d9671d39` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/SOURCE_NOTES.md` | `5de9833499b802898798d0e0405811742bd2605bdefaa36f67f40536bde64a64` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/VIZ_SPEC.json` | `c8389b1864c981575196cb00fd86ca4ada97f17c788b72540db065a135c74cc6` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/contrasts.json` | `288cdc7378586728a8db8174b2c2a8767291062ef60965daab60e5308f70e7a6` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/interactions.csv` | `0cb8a45440b1d1aaba6064664d08ef3414e52f890f46b32fa8a2b40bc577a76d` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/observations.csv` | `04b7a6655b6ec58cecddb30e65420ab290361e74c54f1397ba55975a73947414` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/primary.csv` | `e10a67003fa35de4475532e574af7671354962ed1c1b0e7c1a030869a32c8c93` |
| `docs/analysis/sci_md_perticarini_pressure_chemistry_001/secondary.csv` | `1363831a5ecb43d77cbc4961ae16111305a0472d9e10afc8dc41ccbccf8f3fc1` |
| `docs/cards/egidi2024.md` | `115dea437954e3cf286ead40b7ef1fb53fcbc3ad50d73b024cde76a74862bcfd` |
| `docs/cards/perticarini2024.md` | `6b0447fd5b85b448a5fe085d75f888f0d82345d9d081b380e25537e3157f41eb` |
| `docs/data/ESPRESSO_DATA_GUIDE.md` | `4a98e11868bfcfdbb0d54ddfcd51f2e1b63007f7fa7f7516a8364b6b79589e6e` |
| `puckworks/analysis/perticarini2024_pressure_chemistry.py` | `eaad960b9203d8539431a51abb4225308761e8a9b13434e06390abb511c3fb5a` |
| `puckworks/data/AVAILABLE_DATA_REGISTER.json` | `c7200471a939fbbd6bfc4a422e6b303512354a1e9843f71df178018480cba2de` |
| `puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json` | `48cf1516144bf3d685cfeb763f8c733b820aaae7246c95f36970d4094f123dab` |
| `puckworks/data/MANIFEST.csv` | `9a0ea165c215ab2e826a8a2a571e74d0e0ea160eb25f53117c45dbbeef56784a` |
| `tests/test_perticarini2024_pressure_chemistry.py` | `1bb904363149e003518fe68d8909e91063a361ba60778f99261ed52beaabe378` |
| `tools/build_available_data_register.py` | `e26a274db4b21cccfff43af2868d34c1f06c6714369bbdf562fa70b7737f3d57` |
| `tools/build_local_corpus_family_index.py` | `55a335025cc4b02f68cf060f96621210890384e0d590364a4b0a8141987f6c4e` |

Recorded UTC: 2026-10-26T14:27:20.968411+00:00
