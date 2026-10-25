# Independent substantive review — SCI-MD-FOSTER-RADIAL-FRONT-001

**Disposition: APPROVE the corrected bounded research result, with the recorded
source-support limitations.** Review completed 2026-10-25 UTC. Reviewer: separate
nonhuman Codex reviewer agent, independent of implementation and initial
numerical intake. This is one review engagement including correction of its
material source findings; it is not independent experimental validation or
approval to merge/adopt physics. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The review was against the isolated working tree based on
`236853feb4871dd57d0a6c1a269588db1a88e784`; the exact corrected scientific artifacts
are bound by the hashes below. Repository/hosted CI and final PR lifecycle are
reported separately in VERIFICATION. This review does not claim those checks
had completed when it was written.

## Material finding and correction retained

The initial intake treated `foster-r04-t03`'s lower endpoint at 248 px as a clear
cap. Independent native-raster inspection found that the green t=2 disk covers
the red cap location: the red pixels below it are a vertical stem, not a visible
endpoint. Inferring the cap from a symmetric bar or the emerging stem would
violate PLAN. The feature is now null/unsupported. Complete G at t=3 is now
`UNSUPPORTED_COMPLETE_COHORT`; the initial all-primary compatibility statement
is explicitly withdrawn. Primary E/D and G4/G5 are unchanged. This is a source
support correction, not a changed tolerance or numerical failure.

The same raster audit found five context endpoints without defensible independent
identity: r00-t01 lower; r05-t02 upper; r06-t02 lower; r05-t06 upper; r04-t07 upper.
They are also null. The faint r05-t02 rim is not used to equate endpoints across
figures or reconstruct a hidden cap. Visible cap-end fragments remain usable
under the predeclared +/-4-pixel overlap allowance: r02-t01 lower (nominal
corrected 189→187), r04-t02 upper, r05-t02 lower, r00-t03 upper at the legend
border, and the already wider gray r00-t07 upper/r05-t07 lower features. These
have visible fragments outside the occluding disks/border. The r02-t03 lower
red cap is separately visible immediately above the green cap and remains
supported. No additional primary cap deficiency was found at t=4 or t=5.

The final source notes, JSON/CSV, results, comparison figure and active Foster
claims reflect the correction. The blank G3 summary location was also labelled
“Unsupported: missing endpoint,” preventing a plotting omission from appearing
to be an unreported numerical result.

## Source and observer checks

Inspected the actual PDF methods/figure content and native Figures 6–9, the
qualitative coarse/fine Figure 11 discussion, and the distinct Figure 12–14
vertical-line observer. Independently extracted native images from the actual
PDF: all four hashes match the canonical images; Figures 8/9 match the user's
reviewed identities. The PDF wrapper is separately identified and its altered
bytes are not used to authenticate article content merely by DOI.

Readable Figure 6 absorption and Figure 9 scan legends support the blue/orange/
green/red/purple/brown/pink/gray/olive clock mapping needed for Figure 7's cropped
time text. Figure 7 profiles support the declared eligibility: all t=0 source-rule
zeros; at t=1 only the inner three fitted; at t=2 the inner nine fitted; all thirty
primary slots fitted. This uses visible absorption and the source's 0.2 rule,
not zero markers alone. Equal annuli/scans are dependent observations; the
analysis makes no equal-area or independent-brew assumption.

Figure 9's inverted ordinate is correctly mapped to positive downward bed
depth. Figure 8's colors encode shells, its negative branch is -H, and the
three linked cyan primary end-shell readings are s. Only center identity is
shared. No endpoint transfer, duplicate averaging, temporal interpolation,
model t_shift or Figure 11 first-contact clock substitution occurs.

The paper's transition-width wording does not identify a confidence level or
unique Figure 9 multiplier. Literal endpoint semantics are retained; Figure 7
SEM is kept separate. The printed Equation (1) z2/z3 inconsistency is recorded
without source refitting. Article CC BY-NC 4.0 and UL-cover CC BY-NC-SA 4.0
notices remain distinct. No private PDF/CT data are added to the repository.

## Independent numerical checks

The independent check constructs its own global linear system from tick and
pixel boxes, with separate alpha/beta pairs for Figures 8/9 and shared latent
coordinates for the three authenticated centers. It imports no producer
arithmetic. Exact Fraction substitution verifies that the nominal witness
satisfies **549 retained global inequalities**, including calibrations, pixel
boxes, endpoint ordering and duplicate linkages. Thus the retained set is
nonempty; the universal results are not vacuous.

A separate floating linear-program cross-check minimizes E with a range epigraph,
minimizes G with an epigraph allowed to be negative, and maximizes both by
separate pairwise objectives. It agrees with the producer's enclosures for all
qualified primary outputs. These floating optima are corroboration only; they
are not presented as strict certificates or as sharpness claims.

The strict decisions have elementary rational certificates independently checked
from the pixel contract. Figure 9's shared scale is within [1/734,1/728], and
its offset cancels from same-depiction differences:

| scan | certified E lower bound | certified D upper bound | certified G upper bound |
|---:|---:|---:|---:|
| 3 | 85/1468 > 0 | -85/734 < 0 | unsupported complete cohort |
| 4 | 37/734 > 0 | -71/734 < 0 | -45/734 < 0 |
| 5 | 9/734 > 0 | -13/734 < 0 | -32/367 < 0 |

The conservative upper E construction excludes i=j, so a single uncertain
center cannot occupy both extrema simultaneously. Both scale uncertainty and
mixed-depiction offsets remain represented. The G maximum is not obtained by
maximizing a lower-constrained epigraph. All decimal bounds checked round
outward from the exact rational values. Ignoring the extra duplicate constraints
when forming some outer bounds is conservative and is correctly not called a
sharp correlated range.

The supplied hand cases, strict/touching/unresolved decisions, infeasible-witness
failure, partial-support obstruction, and independent E/D/G eligibility are
covered by focused tests; **23 tests passed** in the review execution. In
particular, unreadable middle centers do not suppress otherwise supported D/G,
and readable centers do not create endpoint support. The independently computed
nominal witness is simultaneously feasible across all three primary scans.

No positive partial extent-obstruction certificate remains on the final retained
support. That absence is not used to establish all-shell compatibility at t=3
or at incomplete context scans.

## Figure, conclusions and preservation

The comparison retains all nine scan panels, distinguishes the primary cohort,
separates center-reading enclosures from published extents and endpoint-reading
enclosures, and displays missing centers/endpoints without zero filling. The
G3 summary explicitly reports unsupported status. No trajectory is fitted, and
no common numerical depth across different scans is asserted.

The corrected conclusions are appropriately separate: center variation and
outer-shallower direction resolve at all three primary scans; displayed extents
are compatible for every admissible reading at t=4/5; complete G3 is unsupported
by one hidden endpoint. Every-reading compatibility retains the quantifier
“for every reading, there exists a common depth,” and is not a fixed-depth
all-readings assertion. The nominal common-position intervals are correctly
labelled feasible-reading witnesses.

Physical first arrival, extraction onset, binary saturation, azimuthal uniformity,
channeling, permeability, porosity, grind causality, full-model validity and cup
benefits remain outside the result. Nonzero center cost is not treated as rejection
of useful approximate one-dimensional wetting. The active Foster wording no
longer says the source fit independently validates model form or that the sharp
binary approximation is established for fine grind.

Independently confirmed byte preservation of the five previous Foster CSVs and
the post-saturation producer/result bundle relative to the accepted base. The new
canonical discovery node retains source lineage without adding automatically
inferred CALIBRATED_FROM edges to runtime components. No new assurance/Foundry
infrastructure or runtime coupling was introduced by the reviewed changes.

## Exact corrected scientific identities

| artifact | SHA-256 |
|---|---|
| `puckworks/analysis/foster2025_radial_front.py` | `43d5204790d195eeea0c6147ecf59b4f759008547c4a5c4938e944bd131fdd44` |
| canonical radial JSON | `12735f86c5cb98a950c9d38e83ebbfbe12613f05c3419b6d83d26ad36e500b31` |
| canonical radial CSV | `2d3eddaa3b3e978a446539fa91955ddf84e3bc3f45e7be767e2a9a9dafc47168` |
| focused test module | `676ecbc47b4b9617a71110cb3782bc72fce60ef7dc6b8c05bf0d59b0f711aabb` |
| `PLAN.md` | `f9678296172593186779f723a4e9f110f567e793188a87d004750f96ffc96dc3` |
| `SOURCE_NOTES.md` | `269aef0f0259475a8f55ca41be6bec6fa603348e301273dfecd59f790b40d5e1` |
| `RESULT.md` | `12edf7bfce4442057577136857359a57d2428fe16be169dde3eb22fa819bb7cb` |
| `scan_results.json` | `c116ad4be2889f9b40f3b9b2a92c3b29866d264f0254a8176d3882ed2f0f9e98` |
| `summary.json` | `0fc7b399e9889bf41282b6e95a25357b7228919d814e89db4814b109f8f94518` |
| `comparison.png` | `2f65d4bc0873c1ffc0192b3bb43fe50d0ce9c42619107845efccbaeda4ccd2f3` |
| `VIZ_SPEC.json` | `5f51cff41e1032dc2544d1d9e65ec44319a17fcde18e0b1d3b5fb248ac5fce75` |

The optional bounded `independent_check.py` accepts `--root`, `--pdf`, and
`--output` and can live beside this review; it requires NumPy/SciPy/PyMuPDF only
for this separate audit. SHA-256:
`90c86fe918a05a3e248d0f57a7b4d63f8011cf45ca83a84ab17b83b5852f5418`.
Source visibility remains a substantive visual review, not a color-mask test.
No material scientific-review finding remains uncorrected in these artifacts.
