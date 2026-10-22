# Dry loading-force increments and the additive-offset test

**EXCLUDED_BY_COMPLETE_INCREMENT_SEPARATION.** The represented dry-loading
measurements are inconsistent with a common force-versus-absolute-density curve
having only constant sample-specific additive force offsets, at the tested density
levels and under the declared graphical-reading contract.

G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NO_GOVERNING_PHYSICS_CHANGE. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

The authenticated thesis supplies twelve graphical sample curves (three each for
Psi_B/C/D/E), recovered from76 unique chunks painted twice. Duplicated painting
adds no samples. The offline producer preserves all source vertices,64 bounded
rounding joins, four excluded legend strokes, both-axis calibration and full query
support. Source method: Z030 tester, nominal0.1 mm/s and maximum300 N. The observed
curve endpoints, not that capacity, define support. See [source reconciliation](SOURCE_RECONCILIATION.md)
and [frozen plan](PLAN.md); the latter was committed at
ffb9a4d922fd0cef96c53a5e23324a3ae8d5fde9 before formal comparison.

## Full request/support accounting

| Request family | Total | SUPPORTED | AMBIGUOUS | UNSUPPORTED | Full-support bounds |
|---|---:|---:|---:|---:|---:|
| Force at fixed density | 60 | 47 | 2 | 11 | 49 |
| Density at fixed force | 72 | 72 | 0 | 0 | 72 |
| Same-sample increments | 24 | 22 | 2 | 0 | 24 |
| Total | 156 | 141 | 4 | 11 | 145 |

AMBIGUOUS is a separate disposition: those four requests have full supported
outer enclosures, not omitted branches. Zero numerically unresolved requests.
All eight grind increment envelopes are COMPLETE and all twelve cross-grind
comparisons qualify. Eleven unsupported rows are F(360) for B1–B3,C1–C3,D1–D3,
and F(400) for B2/B3. D2/D3 at360 have a nominal crossing, but the complete
admissible density interval crosses their recorded starts; the other nine are
outside nominal support too. No extrapolation repairs them.

B1 at400 and E2 at500 kg/m³ each have one nominal crossing but respectively three
and two disconnected intersections with the **admissible query strip**. Small
source path reversals near a strip boundary make the inverse ambiguous under
reading uncertainty. All intersections and their conservative force union/hull
are retained. E2's ambiguity propagates to both increment rows. The committed
contract explicitly permits complete conservative all-crossing enclosures to
qualify while retaining their ambiguity; it never selects a convenient branch.

[force_at_density.csv](force_at_density.csv), [density_at_force.csv](density_at_force.csv)
and [support_accounting.csv](support_accounting.csv) retain every prescribed level,
physical units, original-coordinate query/support intervals and exact reasons.
The full support intervals in RESULT.json are **nominal trace projections**;
request qualification additionally requires the complete anchor/trace allowance.

## Force required at equal absolute density

These are descriptive envelopes across the represented graphical samples,
not population intervals. A partial envelope is marked with its qualifying count
and is not a complete grind conclusion. Units N; outward six-decimal bounds.

| Grind | 360 kg/m³ | 400 kg/m³ | 480 kg/m³ | 500 kg/m³ | 520 kg/m³ |
|---|---|---|---|---|---|
| B | UNSUPPORTED (0/3) | [-0.726443, 4.349262] (1/3; incomplete) † | [9.242808, 17.250221] | [16.745182, 27.218247] | [29.189961, 40.923813] |
| C | UNSUPPORTED (0/3) | [0.431149, 5.904260] | [23.423219, 34.329992] | [39.556020, 53.806903] | [64.130626, 81.052629] |
| D | UNSUPPORTED (0/3) | [2.672343, 11.491198] | [53.434655, 78.032022] | [84.933332, 110.966905] | [126.886928, 157.089551] |
| E | [0.315734, 7.286481] | [8.892337, 23.353259] | [100.617527, 148.295289] | [147.873096, 207.646415] † | [206.909866, 277.951054] |

† Contains a fully supported ambiguous reading. All72 density-at-force requests
at25,50,100,150,200,250 N are supported; their full numerical readings are in the
linked table. No stress, porosity or strain conversion is applied.

## Same-sample force increments

For each sample, D=[L_next−U_previous,U_next−L_previous], followed by the grind
hull over all three D intervals. This is an **outer enclosure**; shared axes,
calibration and geometry mean its endpoints need not be jointly attainable.
No nonnegative sign constraint is imposed. Bounds below are rounded outward only
after exact rational arithmetic and classification. All units N. † retains E2's
multiple-intersection status, enclosed using its full force hull.

### 480→500 kg/m³

| Grind | Sample1 | Sample2 | Sample3 | Grind envelope | Status |
|---|---|---|---|---|---|
| B | [1.572881, 16.880719] | [1.313216, 16.788095] | [0.819129, 15.764289] | [0.819129, 16.880719] | COMPLETE (3/3) |
| C | [6.879592, 27.827959] | [7.671459, 29.033834] | [7.650116, 28.474135] | [6.879592, 29.033834] | COMPLETE (3/3) |
| D | [17.595493, 49.068462] | [15.948949, 46.685192] | [17.331722, 49.957884] | [15.948949, 49.957884] | COMPLETE (3/3) |
| E | [33.709034, 80.916876] | [30.325931, 76.136582] † | [27.816719, 70.720803] | [27.816719, 80.916876] | COMPLETE (3/3) |

### 500→520 kg/m³

| Grind | Sample1 | Sample2 | Sample3 | Grind envelope | Status |
|---|---|---|---|---|---|
| B | [3.853801, 22.100711] | [4.081724, 22.454378] | [4.182865, 22.420981] | [3.853801, 22.454378] | COMPLETE (3/3) |
| C | [12.879448, 39.264021] | [12.742541, 39.051178] | [12.133046, 38.284822] | [12.133046, 39.264021] | COMPLETE (3/3) |
| D | [24.383811, 63.288421] | [24.291944, 63.108580] | [24.074211, 63.695811] | [24.074211, 63.695811] | COMPLETE (3/3) |
| E | [41.370521, 95.946730] | [38.252525, 92.523477] † | [35.571536, 85.041596] | [35.571536, 95.946730] | COMPLETE (3/3) |

The individual enclosures, endpoint request IDs and exact force bounds are in
[sample_force_increments.csv](sample_force_increments.csv); complete membership,
missing/ambiguous IDs and exact grind hulls are in
[grind_increment_envelopes.csv](grind_increment_envelopes.csv).

## All twelve cross-grind comparisons

Difference is second grind minus first; positive separated bounds mean the second
grind requires more additional force. Exact rational signs decide classification;
outward display rounding never decides it. Units N.

| Increment (kg/m³) | Pair | Second-minus-first enclosure | Classification | More force |
|---|---|---|---|---|
| 480→500 | B–C | [-10.001127, 28.214704] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 480→500 | B–D | [-0.931770, 49.138755] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 480→500 | B–E | [10.936001, 80.097746] | STRICTLY_SEPARATED | E |
| 480→500 | C–D | [-13.084884, 43.078292] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 480→500 | C–E | [-1.217114, 74.037283] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 480→500 | D–E | [-22.141165, 64.967927] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 500→520 | B–C | [-10.321332, 35.410219] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 500→520 | B–D | [1.619833, 59.842009] | STRICTLY_SEPARATED | D |
| 500→520 | B–E | [13.117158, 92.092929] | STRICTLY_SEPARATED | E |
| 500→520 | C–D | [-15.189810, 51.562765] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 500→520 | C–E | [-3.692484, 83.813684] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |
| 500→520 | D–E | [-28.124274, 71.872519] | NOT_EXCLUDED_BY_THIS_COMPARISON | — |

There are three strict complete-envelope separations and nine non-exclusions;
none is incomplete. Conservative minimum gaps from **unrounded** bounds are:

| Increment | Separated grinds | Minimum gap, outward enclosure (N) |
|---|---|---|
| 480→500 | E above B | [10.936001, 10.936002] |
| 500→520 | D above B | [1.619833, 1.619834] |
| 500→520 | E above B | [13.117158, 13.117159] |

For the primary B/E comparison, the bound that limits B is B1's upper increment,
approximately16.880718671025 N; E is limited by E3's lower increment,
approximately27.816719749352 N. Their exact difference is approximately
10.936001078327 N >0. The secondary E/B gap is approximately13.117158710590 N;
the secondary D/B gap is approximately1.619833392455 N. Exact fractions and all
bounds producing these gaps are retained in
[cross_grind_comparisons.csv](cross_grind_comparisons.csv).

That table also preserves108 descriptive sample-pair comparisons (nine per grind
pair/increment). They are supporting evidence, not108 independent experiments or
an alternative decision surface. No individual separation is promoted to a
complete-envelope claim. Every primary decision uses all three samples per grind.

## Limited-null logic and exposure

Under F_j(rho_k)=a_j+f_k, subtracting two densities within the same sample cancels
a_j exactly. Every sample must then share the same increment. A strictly separated
pair of complete grind envelopes cannot contain that shared increment. One such
pair suffices; the three above independently satisfy the sufficient rule. No
sample offset, common curve or constitutive parameter was fitted.

Nonseparation in the other nine comparisons is only
NOT_EXCLUDED_BY_THIS_COMPARISON. Overlapping marginal increments do not prove
jointly compatible a_j and f_k: both increments share the500 kg/m³ reading and
all readings share axes/calibration. No joint-feasibility analysis was performed.
The unsupported360/400 requests remain missing; they are not needed for the
sufficient contradiction at480/500/520 kg/m³.

Selection followed a **non-blinded exploratory extraction**. The preliminary
whole-newton F480 and increment envelopes disclosed in PLAN.md are all reproduced
when these independently computed formal bounds are rounded outward to whole
newtons. Their agreement is a diagnostic, not a regression oracle or an acceptance
criterion. The formal method additionally exposes full support and inverse
ambiguities; no allowance, calibration, assignment or support rule was retuned.

## Interpretation ceiling and reproduction

This does not establish a statistically significant population-level grind effect,
a unique mechanical constitutive law, intrinsic modulus, elastic stress–strain
response, packing/friction mechanism, wet-bed consolidation or permeability
mechanism, EWP validation, or an independent experimental campaign. Instrument
calibration, compliance, force zero, initial-state and preparation/run identities
remain unresolved. Graphical bounds do not quantify those uncertainties.

In particular, **F_j(rho)=G(rho−b_j) is not excluded**. Nor is common behavior with
strain defined relative to sample-specific initial states. The registered null
concerns additive **force** offsets and absolute density only. No extrapolation
to the source's larger hydrodynamic-force estimate is made.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The [original four-panel analysis](comparison.svg) shows all twelve source curves,
fixed density levels, all156 support dispositions, individual increment enclosures
and complete grind envelopes. It uses a local VizSpec and does not bridge
unsupported gaps or extend curve endpoints. Source artwork remains external.

```sh
python -m puckworks.analysis.corrochano2017_dry_compaction --output /tmp/dry-compaction --plot
python -m pytest -q tests/test_corrochano2017_dry_compaction.py
```

Routine reproduction is offline from retained inputs. Optional exact-PDF audit:

```sh
python tools/extract_corrochano2017_dry_compaction.py SOURCE.pdf --output /tmp/dry-source-audit
```

See [independent scientific review](REVIEW.md) and [verification](VERIFICATION.md)
for separate review/test/CI receipts. One draft PR remains unmerged, auto-merge
disabled. No production adoption, EWP changes or successor task is authorized.
