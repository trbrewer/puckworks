# Pocket Science Coffee spent-puck assay: calculation and qualification

SCI-MD-RADIAL-OBS-001; G1 / NO_GOVERNING_PHYSICS_CHANGE.
SOURCE_INTERNAL / TARGET_EXPOSED. This is an observation problem, with no protected
holdout, fit, model selection, native integration or production adoption.

Source: Pocket Science Coffee, [workflow (7 January 2024)](https://pocketsciencecoffee.com/2024/01/07/espresso-water-flow-part-0-workflow/)
and [results (27 February 2024)](https://pocketsciencecoffee.com/2024/02/27/espresso-water-flow-part-1-dispersion-puck-screens-and-baskets/).
Workbook and per-sheet exports share lineage. The reader uses formula and cached
views; openpyxl does not calculate. Only the enumerated arithmetic graph is
implemented. Unknown formulas fail; macros, external links and source code are
never executed. Full cell receipts remain external.

## Exact calculation map

Let D be whole initial dose, B whole beverage, t its selected TDS fraction,
H_j the dried residue actually weighed, b_j recovered beverage mass, and t_j
recovery TDS fraction. All interface masses are kg. Workbook masses are g and
TDS cells are numeric percent (9.5 means .095); Excel percent-formatted cells
store fractions (0.2 displays 20%). Center c and outer e are ordered throughout.

| Step | Formula | Sworks cells, row r | VST cells, row r |
|---|---|---|---|
| Recovery beverage | total vessel+brew minus tare | N=S-Q, P=T-R | same |
| Raw recovered solute | b_j t_j | intermediate | intermediate |
| Source corrected soluble mass U_j | (b_j + l H_j)t_j | AL=VK/100, AM=WL/100; l=U | AK=UK/100, AL=VL/100; l=0 |
| Remainder fraction of dried residue | U_j/H_j | V,W (display %) | U,V (display %) |
| Whole-shot anchor A | Bt/D | Y (display %) | X (display %) |
| Inferred initial section masses d_c,d_e | D(1-q), Dq | AF,AG | AE,AF |
| Apparent initial soluble fraction F | A+(U_c+U_e)/D | AQ | AP |
| Apparent section EY e_j | F-U_j/d_j (Sworks); F-U_j/H_j (VST) | AR,AS | AQ,AR |
| Absolute and signed workbook contrasts | abs(e_e-e_c); e_c-e_e | AT,AU | AS,AT |
| Published fractional edge loss | (e_e-e_c)/e_c | later derived, not a workbook column | same |
| Sample mass check | (D-B*t_unfiltered-H_c-H_e)/(D-B*t_unfiltered) | AD | AC |

Sworks applies literal recovery LRR 3.29 for Superjolly and 3.38 for Niche;
these are not spreadsheet links to the LRR means. The separate LRR sheet has
10 flush measurements: (water minus beverage)/dose, five per grinder, and two
AVERAGE cells. Never use these as in-shot pore water. VST has no LRR column or
correction. The source describes about 20:1 added recovery water but does not
record each recovery-water mass; recovered beverage is explicitly recorded.

Sworks Y54, labeled filtered EY, actually references C54 (unfiltered TDS), not
B54. Preserve it as source behavior. Excluded AL9 references V10*K10/100 across
rows. Excel blank-as-zero and error propagation are replayed only for source
cells; the scientific interface rejects absent primitives. Excluded rows 7,9,23
on Sworks remain excluded, including all errors and missing measurements. Shot
numbers repeat within groups: sheet+row is the unique identity. There are 40
Sworks and 20 VST experimental rows, 57 retained in 12 groups, plus 10 separate
flush rows. The 991-row Sworks extent includes formatting, not 991 shots.
Headers recur by block; no merged cells exist. Groups are sheet, grinder, screen
and dispersion, never individual refractometer readings. Condition means use
arithmetic shot means after explicit source rejection, with mean per-shot ratios
kept distinct from ratio of mean EYs. No new rejection threshold is invented.

The q formulas are Sworks 6.19/18.17 then 6.19/18.22 and VST 5.6/18.03 then
5.52/18.07. Their raw denominator is total mass: d_c+d_e=D. The misleading
outer-to-inner header occurs in both sheets. The headers call these original
puck ratios; underlying calibration weighing/geometry records are not supplied.
They are not each shot's measured spent-residue ratio H_e/(H_c+H_e), and deriving
an initial cutter radius still needs homogeneous initial density and geometry.
The EWP q=.31,.34 cuts are explicit synthetic initial-mass examples, not measured
source radii or basket replicas.

## Anchoring and observable dependence

Anchoring already enters both workbook sheets through F. In Sworks,
(1-q)e_c+qe_e=A identically. In VST this equality generally fails because the
subtracted mass basis is H_j rather than d_j. Neither sheet may be silently
replaced by a generic mass-weighted rescaling formula. The results post also
reports later box/smooth-plot anchoring and Monte Carlo uncertainty. Its precise
algorithm, correlations, distribution half-width convention and randomization
are not available here. No reproduction of its CIs or plotted values is claimed.
The rounded registry table is a card transcription, separate from workbook and
plot transformations; discrepancies remain visible, not fitted away.

Write z_j=U_j/d_j for Sworks and z_j=U_j/H_j for VST. Then

    delta = e_e-e_c = z_c-z_e
    fractional_edge_loss = delta / [A+(U_c+U_e)/D-z_c].

The common anchor and total F cancel from delta, but not the fractional ratio.
In Sworks e_c=A-q*delta; hence edge loss=delta/(A-q*delta). Changing A changes
that ratio with fixed recovery measurements. Initial mass q remains in Sworks
delta. In VST q cancels algebraically from F and delta; residue denominators
remain. Shared LRR changes both U values together and does not generally cancel:
d(delta)/dl=t_c H_c/d_c-t_e H_e/d_e (Sworks). Precision in measured TDS/mass is
separate from unmeasured physical assumptions; no confidence intervals are
invented. The executable examples preserve shared anchors and retention.

## Conditional model-to-assay map

EWP provides R=integral remainingExtractable dV (no porosity factor),
L=integral porosity*saturation*dissolvedConcentration dV. R is per bulk-bed volume;
concentration is per pore liquid. Initial inventories I0 and dry masses D0 are
separate scenario declarations. Native solvent mass is rho times pore-water
volume, with rho=965 kg/m3 in these scenarios; solute is additional mass.

Ideal no-loss drying gives H=(D0-I0)+R+L; solvent evaporates and dissolved
solute remains. H is neither D0 nor R. General declared survival factors give
H=a_N(D0-I0)+a_R R+a_L L, recovered solute U=e_R a_R R+e_L a_L L. All losses
are accounted separately. With added recovery water W and retained recovery
solution T, homogeneous dissolution gives t=U/(W+U), b=W+U-T. The source then
reports Uhat=(b+lH)t, which equals U only when T=lH (or a declared different
recovery correction makes it so). This calculation does not assume the source
measured any survival or recovery efficiency. Volatile/handling/drainage losses
and refractometer-equivalent versus model-soluble pool equality are unknown.

The illustrative EWP examples use a_N=a_R=e_R=e_L=1, added W=20H and T=l=0,
with either a_L=1 (retain pore solute) or a_L=0 (remove it). These are limiting
conditional scenarios, not estimated efficiencies or drainage histories. Both
workbook denominator conventions are applied; measured source-shot anchors are
never inserted. Synthetic anchor is A=S_cup/D. Its TDS is S_cup/(W_cup+S_cup)
and its beverage mass is W_cup+S_cup, using native cumulative cup quantities. A measured
anchor would instead have role MEASURED_CONDITIONAL and would not predict the
shot's absolute EY.

## Identifiability decisions and constructive proof

| Candidate | Disposition | Precisely what is available |
|---|---|---|
| Radial solid-depletion difference | NOT_IDENTIFIED_FROM_AVAILABLE_MEASUREMENTS | Conditional recovery of it needs initial regional inventory/dry mass, retained pore solute, handling/drainage and recovery efficiencies/pool equivalence. Sworks delta equals dry-basis solid-depletion contrast only with equal initial soluble fractions and U_j=R_j. |
| Radial recoverable-solute/residue contrast | IDENTIFIED_UNDER_DOCUMENTED_SOURCE_ASSUMPTIONS | U_c/d_c-U_e/d_e for Sworks with source LRR and asserted original mass fractions; U_c/H_c-U_e/H_e for VST without retention correction. These are operational composites, not measured regional delivery. |
| Apparent section-EY difference | IDENTIFIED_UNDER_DOCUMENTED_SOURCE_ASSUMPTIONS | Exact sheet-specific delta above; anchor cancels. Absolute apparent section EYs still use the shot anchor. |
| Fractional edge-loss ratio | IDENTIFIED_UNDER_DOCUMENTED_SOURCE_ASSUMPTIONS | delta/e_c from that sheet and its actual anchor; not anchor-independent or solid depletion. |

For model-to-source interpretation all four maps are
CONDITIONALLY_IDENTIFIED_WITH_NAMED_ADDITIONAL_ASSUMPTIONS. Identification of a
workbook function does not qualify a physical map.

The executable generic counterexample has D=(.014,.006), I0=(.00392,.00168),
R=(.0015,.0008), L=(.0005,.0002), solvent=(.004,.002) kg. A second state changes
R to (.0013,.0010) and L to (.0007,0), leaving every R+L, H, recovery-water mass,
recovery beverage, TDS, dose, initial regional inventory, global remaining R,
global retained L and cup solute .0026 kg unchanged. Initial .0056 kg equals
R+L+cup in both states; all compartments are nonnegative. Their dry-basis radial
solid-depletion contrasts differ. The same assay outputs for both sheet formulas
prove global non-injectivity. This is a generic synthetic example, not a fitted
ambiguity for a particular source shot. No Jacobian-only claim is made.

## Source context and publication limits

The primary workflow supplies a nominal flat 6-bar DE1 programme, not a measured
true puck-inlet transient. N means paper on top, not bare puck. The coffee was
an aged blended light/medium-light preparation; grinder and shot style remain
confounded, the treatment design incomplete, and post-stop drainage unmeasured.
Drying/sectioning and recovery can alter the assayed pool. These corrections
close no pressure-boundary or physical-validation gap.

The local workbook, CSV exports, PDF, source posts, notices, card and accepted
summaries are inspected with exact hashes. Repository records say permission
with attribution (2026-07-13), but no actual grant text extending to new aggregates
is present in the targeted source holdings or third-party notice. Consequently
new per-shot results and condition means remain external. Only code, formulas,
synthetic examples and bounded replay status are published. The existing card
note suggesting force-tracking raw sheets is not current publication clearance.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; NEW_NATIVE_INTEGRATIONS=0;
NEW_NATIVE_BUILDS=0; PRODUCTION_DEFAULTS_AND_LOCK=UNCHANGED. No successor.
