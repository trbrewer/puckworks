# Independent scientific and source-reading review

**PASS for the bounded graphical analysis, after the corrections below.** Three
source groups require a positive shared-clock penalty beyond their independent
monotone baselines. Medium roast at 25 °C has an attained shared witness at its
large baseline tolerance. These conclusions apply to the retained Figure 10
representation. Source-coherent physical trajectories and mechanism adequacy
remain unresolved. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

This is one independent AI review by Codex agent `/root/scientific_review`, separate
from the implementation author. It covers actual source artwork, mathematical
contracts, numerical evidence, comparison figures and RESULT interpretation.
Corrections are part of this bounded review, not successive governance rounds.
This is neither human GitHub approval nor independent experimental validation.
The checked scientific bytes are bound in [review_receipt.json](review_receipt.json).
Hosted CI and final delivery identity are separate verification matters.

## Source inspection and corrections

I independently hashed and opened the published Hargarten, Kuhn and Briesen article
(DOI 10.1002/jsfa.10440), inspected the microscopy methods and Eq. 4 on printed
p. 3963, the Figure 7 artwork/caption on p. 3966, and Figure 10 and Table 2 on
p. 3968. Original raster hashes match the retained contract. Enlarged source crops
and coordinate/identity overlays were checked directly. No dissertation reprint
or source-card summary substituted for this inspection. The PDF and artwork stay
external under the authors' CC BY-NC provenance.

The captions authenticate the same 17 particles: circles are hot microscopy and
triangles are 25 °C, with grayscale distinguishing individual diameters. Figure 7
extends to 1200 s, whereas Figure 10 extends only to 300 s. Microscopy hot water is
approximately 80 °C inside the flow cell, with the reservoir reaching about 60 °C;
the separate diffraction preparation starts at 90 °C. Eq. 4 normalizes diameter
**growth** to growth at 20 minutes. Projection-area-equivalent diameters do not
authenticate three-dimensional spherical radii.

I confirmed these material intake corrections, preserved in the retained
[source correction record](../../../puckworks/data/hargarten2020/swelling_kinetics_001/source_corrections.json):

- `f10a-edge-914` lies left of the right frame, near x = 967.5 pixels. Its tick
  connection had incorrectly suggested x = 982 and an exact 300 s coordinate.
- The Figure 10 right-frame gray triangles initially assigned to light 589 and
  light 520 are respectively light 520 and light 568. Interior gray levels and
  visible outlines identify them.
- Figure 7's upper light right-frame triangle is one light 589 marker, centered
  near y = 1193. It does not also provide a separate light 520 reference.
  The lower overlapping light 520/568 cluster remains unsupported.
- Three distinguishable rightmost Figure 10 light circles were clipped by the
  extraction mask; their manually bounded readings were retained. Dry origins
  and unresolved right-frame features were added as explicit coverage records.

Remaining supported isolated-marker assignments agree with the inspected shape,
shade and admitted ±3-pixel reading allowance. Ambiguous clusters remain explicit;
the 64 unsupported feature records are not an inferred missing-measurement count.
Only 116 Figure 10 points enter the primary comparison. Light 462 has just two
supported early readings, sufficient for their vertical discrepancy but not a
complete kinetic characterization. There are 226 supported native markers across
both figures and four definition-only origins. The reviewer did not independently
repeat the producer's bounded configured-holdings search.

Methods specify a first 10 s frame, but several plotted coordinates appear earlier,
and later coordinates differ by trace. No source explanation was located. Native
pixel-derived times must therefore remain graphical coordinates. Figure 7 medium
hot final circles are near 1154 s; light hot final circles are near 1196 s and
partly overlap the frame. They are not invented exact 1200 s references.

I directly identified a substantial Figure 7/Figure 10 inconsistency. The retained
formal comparison uses medium 543 near 120 s, where both readings are supported:
Figure 7 gives roughly 4.54% growth against roughly 5.02% at the reference, while
Figure 10 gives roughly 139% progress. Under the explicitly conditional same-frame
mapping, outer graphical bounds remain separated by `3469/8165` in fraction units,
or about 42.49 percentage points. The independently checked table contains all
22 admitted frame-pair comparisons. Overlapping time intervals alone do not prove
frame identity. Keeping these representations separate is appropriate.

The source documents bubbles, image processing, detached fragments and reference
measurement error. It supplies no calibrated graphical-to-experimental error
budget. No negative marker was authenticated; synthetic negative-input tests are
appropriate. Table 2 remains separate because weighting and clock reconciliation
are incompletely specified. Statistical nonsignificance does not prove absence
of a kinetic size effect.

## Mathematical and numerical review

For each fixed supported trace, bounded monotonicity follows from p(0) = 0 and
p(1200) = 1. The maximum of endpoint violations and half the ordered interval gaps
is both necessary and sufficient for the stated maximum-distance metric. Equal
times receive both ordering constraints. I independently reconstructed all 17
optima and checked every rational monotone witness against its own intervals.
These optima are mathematical comparators, not measurement-error bounds.

At fixed epsilon, the shared problem is exactly represented by nonnegative
multiplicative inequalities on the union of rational scaled times. Repeated times
share one variable; near ties are not rounded together. Every finite collection
of positive reference values can be scaled so all references are at least one.
Thus this convention is equivalent to strict positivity, without imposing an
upper scale cutoff or admitting zero denominators. A positive-reference path
into a fixed-zero node, a negative normalized upper bound, or a reachable cycle
with product greater than one supplies an exact infeasibility certificate.
The finite feasible vector extends to a nondecreasing H; no analytic law or
ordinary unnormalized collapse is imposed.

The independent checker reconstructs the complete constraint graph from retained
coordinates, verifies all rational upper witnesses, and verifies lower certificates
by multiplying the named edges exactly. It does not import the producer or invoke
its longest-product feasibility routine. For the general family the reported
bracket concerns the infimum; its upper witness is attained. The medium/25 °C
case additionally attains the exact baseline value.

| Group | max B / pp | Shared discrepancy bracket / pp | Additional penalty / pp |
|---|---:|---:|---:|
| light hot | 35.365854 | [52.262357, 52.267382] | [16.896503, 16.901528] |
| light 25 °C | 14.982578 | [17.111227, 17.116874] | [2.128648, 2.134296] |
| medium hot | 14.086957 | [20.866927, 20.872602] | [6.779970, 6.785645] |
| medium 25 °C | 47.391304 | exact 109/230 in fraction units | exact 0 |

Displayed brackets above are outward rounded. The large medium 543 overshoot
already dominates its group's baseline; zero added penalty is weak compatibility
at that tolerance. Source incoherence prevents interpreting any group as physical
acceptance or rejection. Hot-clock findings additionally depend on the constant
clock approximation during cooling.

The calibration/time/radius sensitivity removes constraints and permits marginal
choices that need not coexist. Its nonempty solutions are correctly labelled
`NONEMPTY_OUTER_FEASIBLE_SET_ONLY`. I found and required correction of an initial
outer-baseline witness that omitted each point's own lower bound; the first checker
run rejected it. The corrected partial-order witness now passes, and its label
explicitly says necessary-only. No optimum, tolerance or source value was changed
to secure that correction.

For Mo I inspected the unchanged kernel and observation mapping, checked individual
radius conversion and frozen parameters, and independently reran N240 predictions
for all 17 particles without the analysis wrapper. Maximum discrepancies, increments,
mesh comparisons and integrator-tolerance metadata reproduce. The recorded state
ranges satisfy the stated concentration bounds. The smallest Mo increment is about
0.422 pp, whereas observed N120-to-N240 changes are at most about 0.033375 pp;
this comparison is numerical sensitivity, not a continuum error certificate.

The raw kernel's boundary quadrature gives nonzero normalized progress at t = 0
and slightly exceeds the physical equilibrium volume bound. I independently
confirmed the initial-volume identity `1 + 1/(2N²) + 1/(6N)` and discrete equilibrium
ceiling `(1 + 1/(2N²))/(1-C_M)`. These failures remain explicit; the comparison uses
the unchanged positive-time outputs without clipping or initial-volume subtraction.
No diffusivity, amplitude, timing or temperature parameter was fitted. Hargarten's
role in the calibration lineage prevents independent-validation claims.

The comparison figures were visually inspected through native Matplotlib PNG
renders after a local ImageMagick SVG conversion failed to render paths correctly.
They show supported data and their reading bounds, distinguish the separate Figure 7
observable, and label synthetic connecting lines. No source artwork is committed.

## Independent offline reproduction

```sh
python docs/analysis/sci_md_hargarten_swelling_kinetics_001/review_check.py
python docs/analysis/sci_md_hargarten_swelling_kinetics_001/review_check.py --output /tmp/hargarten-kinetics-replay
```

The first command passed with socket connections/name lookup disabled, PDF access
blocked and PyMuPDF unavailable. It reconstructed mappings, optima, certificates,
source-frame consistency, requested-time interpolation and fixed Mo values.
Six deliberate alterations were all rejected: baseline, shared witness, outer
classification, Mo increment, Mo prediction and conditional figure gap. The producer
hash manifest was updated for each alteration, so arithmetic/semantic checks—not
only stale checksums—detected them. These trials are recorded in the review receipt.
Ordinary tests and hosted CI are reported separately in VERIFICATION and the PR.
