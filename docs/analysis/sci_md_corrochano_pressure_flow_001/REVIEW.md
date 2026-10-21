# Independent scientific review — SCI-MD-CORROCHANO-PRESSURE-FLOW-001

**Disposition: APPROVED within the declared figure-reading and conditional
compatibility scope. No material scientific defect found.** This does not establish
physical conductance, authenticated run pairing, a causal mechanism, or physical
validation. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

One independent reviewer performed this review on 2026-10-21. The reviewer did
not implement the producer or transcribe its input coordinates, and made no
changes to the scientific candidate. This is the one substantive review required
by the frozen plan, not a new study, fit, or review stage. Approval concerns the
examined working-tree bytes below; it is not a claim that a final commit or hosted
CI was examined. Integration and final revision verification are separate.

## Examined identities and scope

Base: `96d8fe8779f065f12eeeed3c96de0a2d0c4a758b`.
Candidate: [SCIENTIFIC_CANDIDATE.json](SCIENTIFIC_CANDIDATE.json), SHA256
`4e3cff5cd6fc1fc51544fcc03c7e96132c6a780569b297a136209df0add29546`.
Every listed file was rehashed and matched before and after the substantive
checks. The candidate describes a working tree on that base, not a committed
review head.

Paths in the following table are relative to the repository root. All hashes are
SHA256; they bind the exact examined content rather than a mutable branch name.

| Examined file | SHA256 |
|---|---|
| `docs/analysis/sci_md_corrochano_pressure_flow_001/PLAN.md` | `fd1be0aa0e8802cf7473f0f9b0f6e2a8c49b28e72f6c45617891290097ed4724` |
| `docs/analysis/sci_md_corrochano_pressure_flow_001/RESULT.json` | `da24eb624a9c7fdb0a927ee6adde984d481ff331d51da421e6e16607ebe54044` |
| `docs/analysis/sci_md_corrochano_pressure_flow_001/RESULT.md` | `646559d3b943e18f6298b96a9d5c4e6b1691ad34c4b0d108e57cd28f89424125` |
| `docs/analysis/sci_md_corrochano_pressure_flow_001/SOURCE_RECONCILIATION.md` | `5cae5e1d954628e8cccbb322290a508b9831e2dae3cfb3698a238ea914bde47a` |
| `docs/analysis/sci_md_corrochano_pressure_flow_001/conductances.csv` | `abcf9b3a274a3b86d91d15d77820c3741845c5eda4e5f13c4565ef54a64c10dc` |
| `docs/analysis/sci_md_corrochano_pressure_flow_001/reconstruction.svg` | `f5b82b82c857cfcb0c5cf168edc6f86d15886b272c6edf243451ffb4b37b39d2` |
| `docs/cards/romancorrochano2017_permeability.md` | `131b1ebf136c4bad225658f40cf18242ee7eab97a25622ff568d525851246144` |
| `puckworks/analysis/corrochano2017_pressure_flow.py` | `8372a54448e401ab936fe23c3861365448f25b343b861fc9aa712c3334820dd0` |
| `puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/PROVENANCE.md` | `94003aa301b33a48c57948710285246d25eaba5f8e6678c93ebf98e8a6e1c115` |
| `puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/contract.json` | `2a3427b022c9abf4a74233d313ff5aaaafa1d656cb416444291e520642c7d6a9` |
| `puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/coverage.csv` | `178f283e614a2588e3855068f7f7e3fb5cfcab3ea0a044fe3ca1edb18c7cd3c2` |
| `puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/readings.csv` | `9e909939a87b98a13f7c95d5bbb565455138afed01d6d9726d41226e5235cf12` |
| `puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature/source_coordinates.csv` | `63fe2346a2377092bc434265d5ef5c0163939bf744000fef39eec7eff6e65cc9` |
| `tests/test_corrochano2017_pressure_flow.py` | `f0b3ce719610719eff6c3b15ede19cccf2ab99e2d4ad4836446253cad8199794` |

The reused `puckworks/analysis/melrose2019bed_transient.py` was inspected and
verified byte-identical to the base; SHA256
`757b9f82fb1b011699a1633f1c74cf1848d91861af49a7e176265b1775411412`.
The reviewer read AGENTS.md, CLAUDE.md, onboarding and applicable governance/data
guidance, the frozen plan, source reconciliation, result, input and coverage
contracts, producer and focused tests. Relevant card, manifest and availability
scope records were checked for claim/campaign consistency. This review did not
repeat the author's bounded external-inventory survey and does not certify an
exhaustive raw-data search.

## Direct source inspection and observer assessment

The held thesis was opened with PyMuPDF and independently rehashed:
`f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818`.
PDF page 291's actual image list contains objects 3223 and 3226, both 512×384.
Their extracted JPEG hashes matched respectively:

- Flow: `9812ced032ea7a8a4a3a2ab24c5d0fcfcdbd6599356042d8b327e07d00788c9b`.
- Pressure: `9ce1ffc678791654b61c1966ca98ede419dbc5b2dbf88ab9032ebdd997234240`.

The reviewer inspected both native panels, enlarged crops and full-band overlays;
read text independently extracted from printed pp.62–65,86–88,231–232,250–258,
266–267 and274; and directly viewed the rendered pages carrying Figure3.1,
Figure3.3, Figure6.23, Figure6.24, the p.257 viscosity unit and p.274 inlet/outlet
discussion. This is underlying-source inspection, not catalogue-only review.
Source images, page renders and reviewer overlays remain outside Git.

The source supports Psi_B, initial400kg/m³ and figure-specific15°C/80°C. Blue=cold
is supported by the temperature discussion and the explicitly cold blue
continuation on p.267. The indistinguishable caption dashes are not a run key.
The generic20°C methods statement is a real discrepancy that is appropriately
preserved rather than silently replacing15°C. Steady-state hydration and
pressure-step averaging cannot be imported into this first-minute observer.

Figure3.1 places the flow meter upstream of the heaters. The pressure is a
pre-cell transducer indication with an empty-cell, flow-dependent apparatus-loss
subtraction, not an independently measured two-tap bed differential. Common10Hz
logging does not establish equal channel response or figure-specific alignment.
The source explicitly distinguishes inlet-meter flow from outlet collection
during circuit filling and absorption. Thus the candidate's indication-level
`Q_meter/DeltaP_bed_reported` is the supported observable; primary-grid10s does
not establish that wetting, storage or thermal transients have ended.

Direct inspection confirms the Figure3.3 positive-intercept expression and its
arithmetic: at1e-5m³/s it gives18000+5300+1900=25200Pa. The plotted observation
and curve are about21000Pa, inside the stated20000–22000Pa reading enclosure.
The displayed six observation centres span approximately3.2e-6 to1.66e-5m³/s,
not the complete0..2e-5 axis range. Retaining this inconsistency without a refit,
sign repair, second pressure subtraction or invented low-flow error budget is
scientifically appropriate. Calibration applicability classifications are
conservative relative to the uncertain support endpoints.

The p.253 dripping discussion prevents interpreting a plotted floor as physical
zero. Retaining bounded indication ratios with positive pressure and an unbounded
cold/hot upper ratio when hot's lower bound is zero is consistent with this
distinction. Figure6.20 uses other conditions and inferred viscosity; p.257
indeed prints3.3–3.6Pa s. Neither that unresolved unit nor the author's qualitative
argument supplies a synchronized measured viscosity bound for Figure6.23.

## Coordinates, continuity and quantified coverage

The extreme-axis anchors and internal ticks agree with the native panels.
Independent inverse-affine calculations reproduce all declared horizontal bands:
the union over x-anchor corners, followed by ±2px and outward integer rounding.
The y-anchor corners, full-band ordinate extrema and additional ±2px guards
produce conservative raster-reading enclosures. A separate colour-excess scan
found all44 readable condition-panel band extrema inside their guarded bounds;
manual inspection checked stroke width, spikes, merges and grid intersections.
The scan is a diagnostic, not an experimental uncertainty model or a definition
of physical trajectory count.

The following load-bearing unguarded y bounds were checked directly against the
native image. The producer adds its declared2px ordinate guard to these values.

| Support | Full x band | Flow y bounds | Pressure y bounds |
|---|---:|---:|---:|
| Cold10s, complete envelopes |119..126|215..241|175..225|
| Cold50s, complete envelopes |347..354|249..270|128..160|
| Cold5s, complete envelopes |91..98|200..223|210..259|
| Cold55s, complete envelopes |375..382|252..271|126..156|
| Late upper hot-flow fragment25s, all hot pressure |205..212|323..328|74..84|
| Late upper hot-flow fragment55s, all hot pressure |375..382|311..315|75..88|

The upper red flow stroke is separately followable throughout the retained
25–55s span. Enlarged endpoint crops support the stated full-band bounds, and
inspection of the intervening image supports continuity without an unresolved
crossing. The early merged region is not joined to this fragment. The small
secondary-grid increase therefore has defensible source support under this
specific reading contract; its size does not justify upgrading its physical
meaning or extending it to all hot runs.

The full60s band404..411 extends beyond visible endpoints around406..408 in both
panels. All four60s slots are correctly unsupported rather than clipped. The
44/48 condition-panel count and seven additional fragment readings are correct.
Three distinguishable flow strokes somewhere in each condition and a caption
stating three repetitions do not recover persistent pressure identities or an
authenticated physical membership list. Reporting zero recovered joint
trajectories, unknown hidden counts, and no enumerated cross-panel permutations
is justified.

Complete-envelope separation is universal over the represented ordinates at the
named times. If both panels represent the same persistent condition population,
every contained fixed matching inherits that separation. This is weaker than
authenticating every physical repetition. The fragment/full-pressure construction
is also valid: its rectangle contains every possible pressure partner, including
every fixed partner, so exclusion survives the relaxation of partner identity.
Rectangle feasibility does not construct a consistent partner or calibration.

## Independent arithmetic and finite-order checks

A separate reviewer script recomputed affine bounds using
`scale*(bottom-y)/(bottom-top)` with exact fractions; it did not call the
producer's recovery, ratio or affine helpers. It verified all55 normalized
readings and time bands, all31 conductance records including missing slots,
all12 condition contrasts with11 supported, and every ordered pair and resolved
same-middle triple in all six grid/support groups. Exact results agree with
the candidate. The strongest separations are:

| Witness | Independently recomputed strict margin, m³/(Pa s) |
|---|---:|
| PRIMARY cold10→50s decline |`611/152150000000000` =4.015773907328295e-12|
| SECONDARY cold5→55s decline |`2891/82350000000000` =3.510625379477839e-11|
| SECONDARY late hot fragment25→55s increase |`1/3825000000000` =2.614379084967321e-13|

In particular the last comparison is
`1/112500000000 - 11/1275000000000 = 1/3825000000000`:
the later lower bound strictly exceeds the earlier upper bound. This includes
the full hot pressure envelopes and all declared anchor/ink guards; it is not
obtained by selecting a favourable pressure trace.

Both cold grids exclude nondecreasing and constant selections. Both full hot
grids allow constant selections in the rectangle relaxation. The late hot
fragment allows constancy on PRIMARY and excludes nonincreasing/constant on
SECONDARY. All11 supported cold-minus-hot intervals are strictly positive.
There is no resolved same-middle decline/recovery triple in any retained group.
An outer hot envelope allowing a constant selection is entirely compatible with
a contained documented fragment excluding constancy.

For finite interval data on a partial order, nondecreasing feasibility requires
`L_i <= U_j` for every ordered pair i≤j; when this holds,
`x_j=max_{i≤j} L_i` supplies a feasible rectangular selection. This establishes
the transitive-pair criterion and why checking adjacent pairs alone can miss a
contradiction. Reversing the order gives the nonincreasing criterion. Constancy
requires intersection of all intervals. Exact touching is feasible; it is not
a strict change. A resolved trough requires both endpoint lower bounds to exceed
the upper bound of the same middle reading. Rectangular possibility requires
that middle's lower bound to be below both endpoint upper bounds; it does not
establish a common physical witness.

An independent constraint-matrix construction checked420 finite-poset cases
with one through seven points, including zero-width intervals, using840 HiGHS
linear feasibility programs with `threads=1`. Both directional decisions agreed
with the reused implementation in every case. The reviewer also checked the
explicit nonadjacent contradiction, exact-touching and same-middle examples in
the focused tests.

The fixed-partner counterexample is sound: Q=(10,9) declines after division by
either P=(1,2) or P=(10,11), while switching from the second partner to the first
manufactures1→4.5. Therefore fixed permutations, pointwise switches, one-run and
all-run quantifiers cannot be interchanged. The candidate does not make that
interchange or count feasible envelope selections as physical monotone runs.

## Conditional physics, verification and final finding

The positive-linear fixed-topology network implication is correct. Under unit
terminal pressure difference, effective conductance is the minimum dissipative
energy over internal potentials. If every edge conductance increases, the energy
at every admissible potential increases, so its minimum cannot decrease. Constant
imposed pressure is not needed for Q/P. The implication is along a run and does
not establish a comparison between different runs or arbitrary dynamic/nonlinear
networks.

The separate observer premise is essential: with
`P_reported=beta*P_actual` and `Q_meter=alpha*Q_bed`,
`G_app=(alpha/beta)*K`. Transferring network monotonicity requires a positive,
time-invariant mapping and the other stated pressure, timing and through-bed
eligibility premises. A resolved indication decline constrains their conjunction;
it does not identify gas, fines, swelling, consolidation or viscosity as its cause.

Under the additional pressure-equivalence, single-phase quasi-static Darcy and
common-geometry assumptions, the viscosity identity
`mu_hot/mu_cold=(alpha_hot/alpha_cold)*(G_cold/G_hot)` is correct. An exact
constructed example with unequal alpha verified that omitting the mapping ratio
would be wrong. The candidate keeps the equal-alpha scenario explicit and leaves
the physical ratio unresolved when alpha is unknown. Nominal grind and initial
density do not establish equal later geometry. No empirical viscosity-only
rejection is earned or claimed.

Verification performed by this reviewer:

- Focused Corrochano and reused Melrose tests: **35 passed**.
- Independent rational/source-band checks and840 LP checks: **passed**.
- Offline numerical/plot reproduction into an external review directory:
  `RESULT.json`, `conductances.csv`, `readings.csv` and `reconstruction.svg` are
  **byte-identical** to the examined candidate.
- The reused finite-order module is unchanged from the base. Candidate hashes
  remain unchanged. These checks establish reproducibility and mathematical
  consistency of the declared readings, not experimental accuracy.

External reviewer work is retained under
`/home/tim/corrochano-pressure-flow-001-evidence/independent-review/`.
`check.py` SHA256 is
`d3dfc0601945ae7e0d3c3ef0623c2ae9b2869cafa31373d2515dce4aa8822a48`;
its `independent-checks.json` SHA256 is
`61bc0cca28443ab149aa682811db73c42d626e4f5ec76a1bbc03a362820eb4f8`.
These external scratch artifacts include source inspections and are not added to
the repository or needed by the offline producer.

No correction to the examined scientific candidate is required. The calibration
discrepancy, source-reading dependence of the small hot-fragment witness,
unauthenticated run membership/pairing, and unresolved physical observation map
are substantive limitations already disclosed in the result, not silently
resolved defects. The new pressure ordinate adds a supported figure-level
pressure normalization while preserving PR348's historical results, shared
Corrochano/Melrose campaign identity, EWP's UNRESOLVED_BOUNDED_ANALYSIS and
line-pressure NOT_ASSESSED. Approval authorizes no physical-validation promotion,
production adoption, new model or successor study.
