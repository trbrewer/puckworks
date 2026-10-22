# Fixed reported-flow rescaling of Figure 6.22

**The reported mean-flow ratio alone does not align the published normalized
hydraulic-resistance histories under the declared source, clock, support and
graphical-reading contract.** Both caption21/122 and prose209/1220 ratios support
this finding on both predeclared grids. G1 / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NO_GOVERNING_PHYSICS_CHANGE.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The direct observable is the published HR/HR_max. All six graphical identities
were recovered as15 curve chunks, with nine bounded joins and two excluded
legend strokes. The affine time calibration preserves the approximately1s left
frame and original trace starts. No fitted clock, origin, vertical adjustment,
smoothing, maximum replacement, absolute-HR reconstruction or mechanism model.

## Complete represented-condition result

Each supported envelope contains all three represented traces on each side,
over the entire admitted horizontal reading range. D=E_low−E_high is a
conservative outer enclosure with shared-axis dependencies relaxed. Endpoints
are not claimed jointly attainable. Bounds below are rounded **outward** to six
decimals; exact rational bounds and classifications are retained in the tables.

| Mapping / grid | Complete requests | Incomplete requests (all unsupported) | Separated | Not excluded |
|---|---:|---:|---:|---:|
| Caption / PRIMARY | 7 / 8 | 1 | 3 | 4 |
| Caption / SECONDARY | 6 / 7 | 1 | 2 | 4 |
| Prose / PRIMARY | 7 / 8 | 1 | 3 | 4 |
| Prose / SECONDARY | 6 / 7 | 1 | 2 | 4 |
| Same-clock / PRIMARY | 5 / 8 | 3 | 4 | 1 |
| Same-clock / SECONDARY | 5 / 7 | 2 | 4 | 1 |

“Incomplete” records failed three-trace completeness; UNSUPPORTED is the
comparison class. These counts overlap and must not be added. There are zero
cases with only one or two supported traces on a side: in every incomplete
comparison all low traces are supported and all high traces are unsupported.
Thus rescaled totals are26 complete/4 incomplete/4 unsupported out of30;
same-clock totals10 complete/5 incomplete/5 unsupported out of15. No requested
row was removed. Zero numerical-unresolved rows with exact rational arithmetic.

| Low time (s) / grid | Caption D | Prose D |
|---|---|---|
| 60 / PRIMARY | [−0.249834, −0.044467] | [−0.249834, −0.042424] |
| 70 / PRIMARY | [−0.278642, −0.063167] | [−0.278642, −0.063716] |
| 80 / PRIMARY | [−0.306687, −0.003570] | [−0.306687, −0.003570] |
| 65 / SECONDARY | [−0.294237, −0.037456] | [−0.294237, −0.037456] |
| 75 / SECONDARY | [−0.335024, −0.031907] | [−0.335024, −0.031907] |

Each row independently satisfies the sufficient complete-envelope decision rule.
At60s, caption high-time=630/61≈10.327868852s; exact upper D≈−0.044467891219,
a positive gap of0.044467891219 in normalized Y. Prose high-time=627/61≈10.278688525s;
upper D≈−0.042424. At80s the exact upper D≈−0.003570415508 is strictly negative,
not a display-rounded touch. Other supported rescaled comparisons overlap:
PRIMARY20/30/40/50; SECONDARY25/35/45/55. Overlap does not prove alignment,
equivalence, a jointly admissible calibration or a common response.

Same-clock comparison retains its original contrast: at10/15s low lies below
high, while PRIMARY30/40/50 and SECONDARY35/45/55 lie above it. PRIMARY20 and
SECONDARY25 overlap. Exact/outward intervals are in envelopes.csv. No aggregate
error ranking is made across these different supported domains.

## Support, pairs and figure

The rescaled10s query is outside nominal high-flow support. At15s its nominal
centerline query is inside all high traces, but the full horizontal reading
range crosses their starts; both interpretations remain UNSUPPORTED. Same-clock
60s is nominally within all high traces but its full query crosses their ends;
65/70/75/80s are beyond high support. Endpoints and gaps are not extrapolated.

pair_support.csv records nominal and full-contract segment intersections for
all nine pairs and each mapping. Every support retains a positive lower bound.
The original [two-panel figure](comparison.svg) shows all six represented
curves on their published supports and on the caption mean-throughput-proxy
common full-contract domain, approximately[34.9811415845,173.6553621962]mL.
The positive lower boundary is set by H3. Vertical bars show complete predeclared PRIMARY
envelopes; the plot does not invent a continuous confidence band. The curve
segments in panel2 show nominal centreline ordinates within that common domain;
bars additionally propagate the full reading contract.

| Pair-specific reporting rows | Separated | Not excluded | Unsupported | Total |
|---|---:|---:|---:|---:|
| Caption / PRIMARY | 39 | 24 | 9 | 72 |
| Caption / SECONDARY | 31 | 23 | 9 | 63 |
| Prose / PRIMARY | 38 | 25 | 9 | 72 |
| Prose / SECONDARY | 31 | 23 | 9 | 63 |
| Same-clock / PRIMARY | 36 | 9 | 27 | 72 |
| Same-clock / SECONDARY | 41 | 4 | 18 | 63 |

There are270 rescaled pair requests (139 separated,95 not excluded,36
unsupported) and135 same-clock pair requests (77 separated,13 not excluded,45
unsupported). These are descriptive graphical pairings, not matched experiments
or independent repetitions. Pair-specific separation is never promoted to a
complete-condition claim. Prose changes one PRIMARY pair classification without
changing the condition-level disposition.

## Exposure, interpretation and limits

Formal60s caption bounds closely agree with the exposed low[0.76,0.90],
high[0.94,1.01] and independent exploratory D≈[−0.252,−0.042]. The formal
30/40s overlaps and early10s unsupported status also agree. The formerly
near-touch80s query resolves a small negative margin. The newly explicit15s
and same-clock60s failures illustrate why nominal support alone is insufficient.
These comparisons were exposed motivation, not targets used to tune guards.

The [source reconciliation](SOURCE_RECONCILIATION.md) preserves these limits:

- **Normalization:** HR_max algorithm, per-trace/per-condition denominators and
  maximum window remain unauthenticated. Different denominators may separate Y
  even under a common absolute-HR law. No such absolute law is excluded here.
- **Clock:** seconds are graphically recoverable; a common physical start event
  is not. With physical origin t0, duration scaling would use
  t_high=t0+r*(t_low−t0). No t0 is fitted; this is a published-clock result.
- **Observation:** HR uses reported corrected bed pressure divided by inlet-meter
  Q. Meter reference, instantaneous Q, bed-flow/storage mapping, response delays
  and apparatus correction remain qualified. Q_mean*t is a **mean-throughput
  proxy**, not cumulative inlet, through-bed or collected outlet volume. The
  mean-flow averaging interval remains unknown; caption/prose decimals stay separate.
- **Repetitions and variability:** envelopes describe represented curves, not
  authenticated instrument-file identities or population behavior. Graphical
  separation is not statistical rejection under unquantified experimental
  variation or measurement error. Bounds are source reading, not confidence limits.
- **Mechanism and lineage:** no gas displacement, consolidation, swelling,
  erosion or temperature mechanism is identified. Author interpretations remain
  interpretations. This observable/contrast joins the existing Corrochano/
  journal/Melrose lineage, adding no independent experimental campaign.

## Reproduction and disposition

```sh
python -m puckworks.analysis.corrochano2017_hydration_flow --output /tmp/hydration-flow --plot
python -m pytest -q tests/test_corrochano2017_hydration_flow.py
```

Routine production/tests use committed compact data only and never open/download
the thesis. Optional extraction is documented in dataset PROVENANCE.md and uses
PyMuPDF2.0. Exact numerical tables do not require plotting/PDF dependencies;
SVG replay uses Matplotlib3.11.2. Dataset loader:
`puckworks.data.rc17_fig6_22_hydration_flow()` returns original path coordinates;
the contract and producer supply calibrated readings and conservative bounds.

[PLAN.md](PLAN.md) was committed before the formal calculation. The independent
scientific review and software/hosted checks are recorded separately in
[REVIEW.md](REVIEW.md) and [VERIFICATION.md](VERIFICATION.md). This bounded result
completes the scientific task; final handoff retains one open draft PR, unmerged,
auto-merge disabled. Prior results, EWP, dependency pins and production defaults
remain unchanged. No successor is started.
