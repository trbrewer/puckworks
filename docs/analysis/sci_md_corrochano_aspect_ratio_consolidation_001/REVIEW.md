# Independent scientific review

**Disposition: APPROVED_FOR_DECLARED_RESEARCH_ONLY_RESULT.** One substantive
independent review, with one bounded provenance correction verified within this
review. No unresolved scientific blocker was found for the claims in RESULT.md.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED** remains required.

Reviewer: independent Codex review agent `/root/scientific_review`, which did
not implement the producer or transcribe the candidate coordinates. Review
completed 2026-10-22 UTC (2026-10-21 America/Chicago). This is a review of the
working-tree bytes identified below, on base
`f7bd1686854db990e7c8950ca6e9bd7dd8073bac`. That base is not the final candidate
commit. This document does not attest hosted CI, a later commit, merge status,
or production adoption. Integration verification must establish that the final
scientific bytes match these reviewed bytes and report the final head and CI
separately.

## Evidence actually inspected

Read AGENTS.md, CLAUDE.md, onboarding, the data guide and relevant capability
register entries, available-data-first policy, applicable governance provisions,
both Corrochano cards, the prior tamped-K result and pressure-flow result, and
the task plan, source reconciliation, numerical producer, optional extractor,
focused tests, input bundle, RESULT.md, RESULT.json and reconstruction. The
registered material JSON and journal/thesis table CSVs were opened as underlying
files. Their previous results and uncertainty contracts were not imported into
this calculation.

I independently opened and rehashed both held primary PDFs:

| Source | SHA256 | Pagination |
|---|---|---|
| Birmingham thesis, `Roman-Corrochano17EngD.pdf` | `f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818` | 359 pages; printed page +25 = PDF page |
| Journal version with Birmingham repository cover | `a67e855f52472589dd35c878a16a6825866a5a901958a1ea46752c50138b800f` | 12 pages; Table 2 printed 113 / PDF 9 |

The journal cover and first article page identify the version of record, DOI
10.1016/j.jfoodeng.2014.11.006, and CC BY 3.0. This is a different file from the
prior input qualification's 11-page journal copy; no byte identity was assumed.

Direct thesis text inspection covered printed 62–65, 85–89, 219–225 and
230–238. I additionally checked Table 6.1 on 227, the K–C expression on 97,
and dry-size Table 4.1 on 111. Full-page renders were visually inspected for
Figures 6.9 (236), 6.8 (234), 6.1 (221), the empty-cell calibration (64), and
Table 6.1 (227); journal Table 2 (113) was also inspected visually. Journal
Table 1 (109) and thesis Table 4.1 corroborate A/B/C/D ↔ Psi_B/C/D/E through
their four dry Sauter-size summaries. This supports the grind aliases, not
identity of individual experimental beds.

The holdings receipt was inspected as a receipt; I did not independently repeat
the broader eleven-CSV external inventory audit or the integration agent's
remote-ref/PR searches. Those are separate preflight activities. The missing
temperature-consolidation result is not available for this review, and no
conclusion from it is inferred from thesis Section 6.2.4. No external source
images, raw PDFs, EWP files or lock were edited by this reviewer.

## Direct graphical extraction and bounds

Using PyMuPDF 2.0, I inspected all native drawings on PDF page 261. Page xref
2817 has content xref 2818 and no image XObjects. The decoded stream hashes to
`05405dc1d325a1895e1ad012425e08e9da99598d05021951982d160da3043d57`.

My independent scratch calculation selected thin black bar quadrilaterals,
blue cap lines and long black axis lines by type, color and geometry. It did
not import the candidate producer or extractor. Eight bar outlines reduce to
four unique geometries, in the visually confirmed order B 2:1, B 6:1, E 2:1,
E 6:1. Fill/outline tops agree within 0.001 pt. Blue paths 23 and 32 contain
identical twelve line items, yielding eight unique cap endpoints.

The shared axis centers are zero 312.3118896484375 pt and top
104.43576049804688 pt, with multiplier 1e-13 m². The declared guards enclose
the source half-strokes: axis 1.2147022486/2 < 0.61 pt; bar outline
0.3036755621/2 < 0.16 pt; cap 1.8220534325/2 < 0.92 pt. The six tick centers
are consistent with the linear calibration; the largest nominal residual is
below 0.061 pt. These are graphical interpretation bounds, not uncertainty in
the experiments or proof of exact published numerical precision.

Independent conversion gives the following, in units of 1e-14 m²:

| Condition | Mean | Lower displayed endpoint | Upper displayed endpoint |
|---|---:|---:|---:|
| Psi_B 2:1 | 2.59071 | 2.34235 | 2.84149 |
| Psi_B 6:1 | 6.21134 | 5.54907 | 6.87363 |
| Psi_E 2:1 | 8.95056 | 8.20064 | 9.70051 |
| Psi_E 6:1 | 8.40029 | 8.24202 | 8.56099 |

All twelve centers and all twelve reading intervals match RESULT.json,
including its exact rational bounds. The small displayed cap asymmetries were
retained, not replaced with a forced symmetric spread.

For the ratio `r=(z-y6)/(z-y2)`, the common top and scale cancel. Its derivative
with respect to zero is `(y6-y2)/(z-y2)^2`; it decreases with y6 and increases
with y2. Thus the fine ratio reaches its minimum at the larger zero and the
coarse ratio at the smaller zero, with opposite choices for the maximum.
Evaluating these analytic extrema independently gives:

| Grind | Center | Joint shared-axis bounds |
|---|---:|---:|
| Psi_B | 2.397543447673243 | [2.37198523195488, 2.4238431141891548] |
| Psi_E | 0.9385211128189173 | [0.9366480242976788, 0.9403851628315305] |

Exact fractions agree with the artifact; a separate dense interior check over
31 zeros and 11×11 bar-top choices per grind lies inside these extrema. The
reported ratios of marginal ordinate intervals are correctly labeled outer
enclosures, not jointly realizable calibration witnesses. Neither treatment
turns displayed variability into SEM, confidence intervals or physical bounds.

## Scientific and arithmetic checks

The conservation identity is `(1-epsilon_j)(1-lambda_j)=1-epsilon0`. Substituting
it into `f(epsilon)=epsilon^3/(1-epsilon)^2` gives the independently derived
closed form

```text
R_KC = [(epsilon0-lambda6)/(epsilon0-lambda2)]^3
       × (1-lambda2)/(1-lambda6).
```

This agrees with the producer's separate porosity/factor calculation. I checked
particle-volume conservation, reversal of chamber labels, reciprocal ratios,
and equal-consolidation cancellation. The fixed 480/1337 kg/m³ routes give:

| Route | epsilon0 | epsilon2 | R_KC | F_required |
|---|---:|---:|---:|---:|
| A, particle porosity 0.53 | 0.2361431595 | 0.1220036316 | 9.5800842603 | 0.2502632944 |
| B, particle porosity 0.50 | 0.2819745699 | 0.1746834137 | 5.5569477368 | 0.4314497025 |

Here epsilon6=epsilon0, lambda2=0.13 and lambda6=0. Exact residual bounds also
match RESULT.json. The coarse scenario correctly cancels any common admissible
porosity at zero/zero consolidation: R_KC=1 and F_required=0.9385211128. It does
not assign the fine grind's measured particle porosity to the coarse grind.
All declared nominal residual intervals exclude one. This establishes the
reported conditional reading mismatch, not physical rejection or significance.

Figure 6.1b is Psi_C, not Psi_B. Figure 6.1e is the two-method average defined
by Eq. 3.24, with Psi_B/480 near 13%; p.230 independently states 13%. The
candidate correctly avoids substituting panel a's depth-only endpoint. The
1.2–2.3-fold method disagreement on p.222 supplies neither a task-specific error
distribution nor a bound on a reported zero. The nominal zeros in p.235 are
therefore appropriately left without invented detection thresholds.

The calculation conserves effective particle volume as an assumption. It does
not establish conservation through extraction, swelling, deformation or material
loss. F_required is the conditional multiplicative residual for representative
states; it is not an observed bed-level prefactor ratio or a fitted mechanism.
Unknown lambda–kappa covariance and the nonlinear aggregation issue remain
material: `f(mean epsilon)` and `mean f(epsilon)` need not agree. The source's
per-bed inverse pressure/flow slopes and lengths are not recovered from the
displayed condition means.

For equal initial volumes, I derived H0=3^(4/3)=4.3267487109. The printed
dimensions independently give `(54/37)^2(18.5/9)=4.3783783784`. Applying the
fine length factor 0.87 gives the reported common-viscosity conductance ratios
9.0250041788 and 9.1326965815. Coarse gives 4.0607450151 and 4.1092005480.
Area/length, permeability-weighted area/length, conductance and resistance have
the stated distinct SI units. These two geometries are deterministic source
representations, not uncertainty endpoints. Actual hydraulic ratios retain the
mu2/mu6 multiplier and require valid pressure/through-bed-flow mapping.

I independently checked, with rational arithmetic, that a fixed authenticated
Q/P slope obeys `kappa=mu L S_QP/A` and `kappa A/(mu L)=S_QP` for multiple
lengths. Changing the length consistently cancels; holding published kappa
fixed while changing lambda is a different conditional comparison. The report
does not claim that mean kappa divided by mean length is the mean physical
conductance. This qualification is essential because pp.219 and 225 explicitly
say consolidated length was used to derive permeability.

The source's full-chamber products are independently reproduced as 10.37356802
and 4.06074502, rounding to p.238's 10.37/4.06. They are derived products, not
separate pressure observations. The fine prose approximation of 3 is outside
the graphic-reading range and correctly remains a separate statement. Setting
epsilon0=0.23 gives 10.58529, which rounds to 10.6; it is an arithmetic
reconstruction, not an authenticated author intermediate. Registered epsilon0
rounds to 0.24 at two decimals. No hypothetical 8% rescue calculation is added.

## Source joins, protocol and observer limits

Journal Table 2 directly gives A/480 = 2.59±0.25 and D/480 = 8.95±0.75 in
1e-14 m², with averages of three independent samples and standard deviations.
The narrow Figure 6.9 means/endpoints agree within the reading bounds. Thesis
Table 6.1 displays 2.6±0.3 and **9.00±0.8**. The latter mean is a real literal
precision discrepancy with 8.95, not ordinary rounding at the displayed 0.01
precision. Source conditions, table summaries and method language support
linked aggregate presentations; they do not authenticate identical beds.
The candidate neither replaces figure readings nor pools table and figure as
independent observations. The wider bars have no matching journal table rows.

The methods support inherited 600 s hydration and steady-state measurement,
nominal 80°C and initial 480 kg/m³. Aspect-specific hydration changes tank
pressure from 4.5 to 1.5 bar. Generic 4.5→0.5-bar steps and aspect-specific
4.5–1.5-bar wording differ; neither authenticates a marker-index schedule or
paired physical beds. Generic three-sample and ambiguous SD-of-the-mean wording
do not independently recover the Figure 6.9 sample roster or error definition.

Figure 6.8 visually confirms panel a=Psi_B, b=Psi_E, blue=2:1, red=6:1, Q on
the horizontal axis and reported bed pressure on the vertical axis. Horizontal
caps are visible; independent vertical caps are not resolved. Narrow-chamber
pressure is higher over visible common-flow support in both panels. The rough
overlap ranges stated in reconciliation are appropriate orientation readings;
no point intake, regression, numerical pressure ratio or independent validation
is warranted from this audit.

Pages 63–64 explicitly include **chamber wall** losses in the empty-cell
correction, and p.234 explicitly reuses that calibration for the changed wider
chamber. This remains a material unquantified observer limitation. At Q=1e-5
m³/s the printed positive-intercept polynomial gives 25200 Pa, while the
displayed calibration is near 21000 Pa. I confirmed this arithmetic and the
visual discrepancy directly. Fine common-flow support is below the displayed
calibration observations; coarse includes below-support and in-range portions.
No refit, second correction, physical-zero inference or viscosity estimate is
justified. The ultrasonic meter's upstream location and unresolved volume
reference also persist. These are reasons to retain the physical claim ceiling,
not new adjustments to the four recovered means.

## Finding and bounded correction verification

**R1, corrected:** the initial reconciliation said the blue error caps appeared
once. Direct source inspection showed identical error drawings 23/32, sequences
38/48. Both were already retained in source_paths.json; the coordinates used
the second copy, so the numerical extraction had not double-counted them.
The implementation agent corrected the prose and provenance table and added
duplicate-error equality checks to the optional extractor and focused test.
I inspected those changes and replayed extraction. The coordinate CSV,
source_paths.json, numerical producer, contract, RESULT.json, readings and SVG
were byte-identical to their pre-correction versions. The test-only change to
use `rel=1e-13, abs=0` for the small SI conductance assertions was also checked.
No new scientific calculation or review round was opened.

## Executed checks and exact scope

Using `/home/tim/corrochano-pressure-flow-001-evidence/venv/bin/python` from this
worktree with `PYTHONPATH=.` where needed:

- Independent direct-PDF/path selection and closed-form arithmetic: PASS.
- `pytest -q tests/test_corrochano2017_aspect_ratio.py`: **18 passed**.
- Producer replay with `--plot`: RESULT.json, readings.csv and reconstruction.svg
  are byte-identical to the task artifacts; readings also match the data bundle.
- Optional extraction from the rehashed thesis: source_coordinates.csv and
  source_paths.json are byte-identical to the registered bundle.
- RESULT.json's recorded input hashes all match the inspected input bytes.
- The complete reconstructed SVG was rendered and visually inspected: condition
  ordering, units, displayed endpoints, reading-bound distinctions and physical
  validation ceiling are present and consistent with the source.

Independent scripts, numerical receipts and source renders remain outside Git
under `/home/tim/corrochano-aspect-ratio-001-evidence/review`. The equations and
checks above state the review's independent reasoning; passing software tests
alone is not its scientific basis.

The maximum approved claim is a fixed-input, source-internal, retrospective
comparison of four condition means and a qualitative Figure 6.8 audit. The
fine fixed scenarios overpredict the recovered contrast; coarse differs from
the nominal equal-consolidation prediction under the reading contract.
Measurement uncertainty, cohort identity, covariance, calibration reuse and
fluid state prevent physical adequacy/rejection, mechanism identification or
causal attribution. Temperature-study synthesis remains UNAVAILABLE. No
protected holdout, independent replication, fit, production change, EWP result,
automatic successor or general rejection of consolidation is established.

## Reviewed working-tree SHA256 identities

Paths below are relative to the repository. Review/verification documents are
not self-hashed. The listed byte identities distinguish this scientific review
from a later integration or hosted-CI assertion.

| File | SHA256 |
|---|---|
| `puckworks/analysis/corrochano2017_aspect_ratio.py` | `ea81fb8ec94d3a8248503f380eacc68751ec4a4c028af421b9e4b374ed8826d5` |
| `tools/extract_corrochano2017_aspect_ratio.py` | `82a4729b333ceff82e126f0fc51b16e3e573c6930e95a9bba44ff007803c2ab2` |
| `tests/test_corrochano2017_aspect_ratio.py` | `b93ca93168a33cf0408c39a089eaf4864a709e2091d70bfe9bef67601e522e00` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/PLAN.md` | `01d08dbce34a53d21c2a085deae6cd2558c10c74020c3987efd11961d8447987` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/SOURCE_RECONCILIATION.md` | `81be5d7a29fd440cebb1cbbefc5ef7ef43d30f6165b36c48a135b81ec556db6e` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/RESULT.md` | `4ee153c11d0846b59abed9f3f27137a6c09cbef9fcfa843a70ace97066c1058d` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/RESULT.json` | `e3e3053984460625aa840cfa2012f00f1d0e5d60954c8f58b5abfee17ed5662a` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/readings.csv` | `dc2143a8e3555605fd1d4916380a232f6bddaa0e2267c77e105d67abec55a126` |
| `docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/reconstruction.svg` | `2aeb235f6176926418f17f3f254c647a7b82463c3cef68180ed2e3a62284156b` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/contract.json` | `75a0e4809c741efaec386b6df968d859213c8ee4800d81db1e47e40e1a1c7c82` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/source_coordinates.csv` | `0d76c18f11111818ef8ab07516911412b0b52afa332f7b902e49f6712cd1084e` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/source_paths.json` | `fab12949bab2af751453ce049f0d16892b12dd0aa05c01841c149bcb54906a07` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/PROVENANCE.md` | `2388a27cfd401d8af329378323a413202f342370b85f7549c698ca73ef95fecf` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/readings.csv` | `dc2143a8e3555605fd1d4916380a232f6bddaa0e2267c77e105d67abec55a126` |
| `puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/holdings_checked.json` | `1fe38d3abcfd265f31268a6752427d8d52e90fe3d5245ead53a3933cb3282c43` |
| `puckworks/data/romancorrochano2015/sci_val_tamped_k_001_inputs.json` | `a3a0384394cae7bf17ab15ee8e528c63dc876a83a76b9397f7df250940411a99` |
| `puckworks/data/romancorrochano2015/table2.csv` | `cd81b18db8bc799b1b67a2c765f96e70ae41db1f0b88be0f1566a1327278737e` |
| `puckworks/data/romancorrochano2017/table6_1_tamped_kappa.csv` | `aa42f1c6d438a39e042e207106ae9c251040f2be2dc5ce7028611c84410477ce` |
| `docs/cards/romancorrochano2015.md` | `d09461fc63ce8667ac683f94778d3371caa3ad9fb30dab1b81db51ef6e8845e2` |
| `docs/cards/romancorrochano2017_permeability.md` | `1779d7fe45c5b404f4a3076af3e4b4230bb6f2359a3fea40b19e399e766986e5` |
