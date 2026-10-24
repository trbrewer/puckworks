# Retrospective source, observation and correction contract

The machine contract and visual regions are in
[`smrke2024/s1`](../../../puckworks/data/smrke2024/s1/contract.json), bound by
[CONTRACT_FREEZE.json](CONTRACT_FREEZE.json) before calculating contrasts. Its explicit qualification-correction attachment supersedes the original rules where independent review found defects; original hashes remain preserved.
They specify native ticks, affine transforms, residuals, allowances, colour/style
rules, masks, support, phase, identities, and both fixed window lattices.

Source: Smrke, Eiermann & Yeretzian (2024), *The role of fines in espresso
extraction dynamics*, Scientific Reports 14, 5612,
[DOI](https://doi.org/10.1038/s41598-024-55831-x), Supplementary Figure S1.
[Official supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-024-55831-x/MediaObjects/41598_2024_55831_MOESM1_ESM.docx).
Source and annotated derivatives: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Annotations, masks and conservative reading enclosures are this task's additions.

## What was intervened on and measured

Settings 250/210/190 encode solid/dashed/dotted; they are apparatus settings,
not particle diameters or transferable grind coordinates. Yellow/magenta/purple/
blue encode 0/1/2/4 g of the <120 µm sieved fraction replacing coffee within a
nominal 20 g dose. Zero replacement retains native fines. Neither replacement
mass nor the sieve cut equals total volume share below 100 µm. Twelve intended
cells × nominal three replicates = 36 intended extractions, not 36 recovered
trajectories. The 40 g beverage target is manually controlled, not an exact area.

S1 is a derivative of measured beverage mass in g/s. Nominal 9 bar supplies no
synchronized measured puck-pressure trace. Machine-displayed extraction time
does not authenticate alignment of all plotted traces. Pump-on, first drip,
pump-off, balance response and differentiation/smoothing details remain unknown.
Graphical interior is distinct from authenticated interior brewing.

## Native support and identities

All admitted coloured runs within the plot are recorded with native x and y
extent. Generic fragments are maximal one-to-one adjacent-column chains.
Any branch/merge ends that identity; no `run_index` rank is followed. Generic
style membership remains ambiguous among 190/210/250, with fines nominal colour recorded. The reviewed qualification correction conservatively admits all fines levels for generic mixed/antialiased ink; only audited regions have definite condition labels.
Tiny strokes are observations, not independent shots or temporal samples.
Unknown phase is retained. Diagnostic boxes identify startup, an endpoint-linked
terminal candidate/tail, same-colour crossing, patterned gaps and clipping.

The original candidate blue corridor is split at every unbridged gap. Independent review retires x479–528 for branch mixing; only two earlier disconnected fragments remain, each with at most one complete window per lattice. The original region and retired readings remain available for audit.
Two short solid-branch bundles retain every visible continuation inside broad
slabs without assigning persistent identities through crossings. Their condition
completeness is unresolved: outside patterned/baseline ink remains in the source
inventory and nominal n=3 cannot settle hidden membership. They can bound the
means of retained paths in a common window, but cannot support a fixed-pair
multiplier or a fines-wide shape claim. Selected regions are subsets of the
generic ink inventory, not additional trajectories.

Only bounded narrow other-colour occlusions/raster gaps qualify under the explicit
four-missing-column bridge rule. Known dash/dot gaps are not bridged. A bridge is
a conditional graphical reading premise, not evidence of physical smoothness.
Any unsupported gap or unbounded clipping makes a whole-window mean unsupported;
visible duration never replaces requested duration. The yellow top contact is
not an upper bound of 7 g/s on hidden continuation. Blue right-boundary contact
does not authenticate an endpoint. The initial 85 s nominal domain is corrected to the native affine right edge, 124880/1469 s. This extends only incomplete remainders; the uncertain frame neighbourhood remains missing support.

## Integration and tests

For every literal-time window, split into fixed 0.05 s integration cells with
partial boundary cells. Map each entire cell back to the range of x allowed by
all shared calibration choices. Require source support throughout that range;
take extrema of all intersected native reading cells and all y-anchor corners.
Their exact rational duration-weighted integrals enclose the full-window mean.
This outer relaxation permits more freedom than a common calibration, hence
cannot falsely exclude an admitted global choice. JSON stores exact fractions;
CSV decimal bounds round outwards. No statistical inference from raster density.

Enumerate all ordered complete-window pairs on persistent fragments, every
successive complete-interior triple, and necessary constant intersections across
all supported windows. Report nonempty intersections only as not excluded.
Request every fragment/window on both lattices, including remainders. Generic
unqualified fragments remain unsupported with their identity/phase/gap reason.

For each setting enumerate six unordered fines pairs (18 total); 0-vs-added
pairs are primary. Compare every eligible retained-object pairing at common
complete interior windows and retain the coverage/spread qualification. A
difference uses [L_B-U_A,U_B-L_A]. No aggregate shot mean or replicate variance.

For a fixed persistent pairing use every maximal common complete interior
window, at least two. Solve k*L_A<=U_B and k*U_A>=L_B for k>0 exactly, including
zero bounds. Intersect per fixed pairing, then union across alternatives.
No partner switching, clock shift, selected subinterval or common k across
unrelated pairs. Nonempty necessary outer support is not joint realizability.
Failure cannot exclude time shifts/rescaling or general permeability explanations.

Normalized shape: UNRESOLVED_SOURCE_SUPPORT. Graphical findings cannot identify
migration, deposition, erosion, channels, intrinsic permeability or equivalent
pressure, and supply no new continuum closure or physical validation.
