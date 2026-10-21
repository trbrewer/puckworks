# Source, observation contract and reconciliation

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Only Figure6.23 is scored. Source facts, declared assumptions and unresolved
joins below have different roles; none is silently promoted to a measured fact.

## Inspected identities and availability

The [thesis](https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf) held from
the prior source intake was reopened and hashed:359 pages,
SHA256 `f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818`.
The live PDF browser request exceeded the browser's file-size limit; the exact
held copy supplied source access. This is underlying-file inspection, not reliance
on catalogue metadata. PyMuPDF2.0 enumerated PDF291 images and extracted actual
objects3223/3226, each512×384 JPEG, with the owner's expected hashes:
flow `9812ced032ea7a8a4a3a2ab24c5d0fcfcdbd6599356042d8b327e07d00788c9b`;
pressure `9ce1ffc678791654b61c1966ca98ede419dbc5b2dbf88ab9032ebdd997234240`.
Object numbers are observations about this copy, not assumptions for rewritten
PDFs. Image and page inspections used Pillow/PyMuPDF outside Git.

The existing resolver found the registered collection and inventory mounted.
A bounded inventory selection found11 relevant CSV files and one filesystem
metadata file; the CSV bytes were opened, their comments and tables inspected,
and all11 hashes matched the inventory. They contain2015 permeability and2017
transport, steady permeability, inventory and fit-error summaries; none provides
an authenticated Figure6.23 run-level join. The metadata file was hash-only.
No new broad census, unrelated source search, author contact or raw-data absence
claim follows. The held PDF is a separately verified underlying source, not a
new experimental campaign. Current-tree/task-branch/PR searches found no equivalent
Figure6.23 intake. Existing Melrose/Fasano/EWP studies are not rerun or superseded.

## Source-to-observer crosswalk

Page references below are printed pages; add25 for PDF page number.

| Item | Source-supported fact | Assumption or unresolved item / adopted treatment |
|---|---|---|
| Conditions | p.266, Figure6.23: Psi_B, initial400kg/m³,15°C and80°C; three repetitions displayed | Three flow strokes per condition are distinguishable somewhere; no physical-run list. Initial density and grind do not establish common later geometry/internal state. |
| Temperature discrepancy | Generic methods p.86 name20/80°C; cold-specific p.231 and Figure6.23 name15°C | Preserve15°C figure labels and20°C generic-method discrepancy. p.231's15-minute cold hydration concerns steady permeability, not first-minute prehydration. |
| Colour | Native flow panel has blue upper and red lower traces; p.266 explains lower cold hydraulic resistance; p.267 Figure6.24 is explicitly one cold continuation, in blue | Blue=cold, red=hot supported by explanation/continuation. Caption dashes do not distinguish colours or provide a run key. |
| Meter location | Figure3.1/p.62 and p.63: ultrasonic USC-731 after tank/timed valve, before heaters | Recorded m³/s is inlet-meter indication; local/standard volume reference, compensation and meter temperature/density unknown. No bed-temperature or density conversion. |
| Pressure | pp.62–64,88, Eq.3.21:0–6bar RS348-8087 before cell; reported bed pressure=Ptrans−DeltaPelements | Not an independent direct two-tap differential. Dynamic pressure reference/outlet equivalence and correction implementation for this figure are unqualified. |
| Correction | p.64: empty-cell measurements at varying Q for shower head, wall and bottom filter; quadratic correlation | Q-dependent correction couples numerator and denominator. No second subtraction, no reconstructed transducer curve, no imported EWP loss law. |
| Acquisition | p.63: temperature, pressure and flow logged together at10 measurements/s with LabView | Figure pixels are continuous plotted traces, not recovered10Hz samples. Channel response/filter/delay and figure-specific panel alignment unknown. |
| Clock | p.63: brewing cycle starts when timed valve opens; Figure6.23 uses displayed seconds | Valve-opening origin is plausible but exact figure trigger/offset is not authenticated. Ratios at common displayed time are not qualified synchronized physical observations. |
| Steady protocol | pp.86–88: hydrate600s, pressure steps, average last30 of60s for steady permeability; p.231: cold900s | These are not the observation operator or hydration state for Figure6.23's first minute. |
| Startup/storage | pp.250–251: early peak linked to filling low-resistance upstream circuit; p.255: front time estimated2–4s, absorption also present | PRIMARY starts10s to avoid earliest startup only; it does not certify negligible storage, fully established saturation or constant temperature. |
| Thermal state | p.255: typical hot inlet70–80°C after3s; actual thermal histories differ, source assumes influence small | No synchronized Figure6.23 spatial temperature/property bounds. Nominal80°C is not the meter reference condition. |
| Low indication | p.253: some finest-grind recorded-zero intervals corresponded in practice to dripping, then continuous flow | A bounded plotted indication can be divided by positive reported P; floor-limited readings do not establish zero physical Q, detection threshold, physical upper Q or infinite resistance. |
| Inlet/outlet | p.274 explicitly distinguishes meter inlet from collected outlet flow during filling/absorption | Not saturated through-bed discharge or collected beverage flow. No transfer of the outlet aliquot/density observer used in Melrose. |
| Figure6.15/6.16 | pp.250–251 describe transient Q and reported bed-pressure behavior | Context only; no additional scored brew or calibration of Figure6.23. |
| Figure6.24 | p.267 is one previously displayed cold trace at longer time | Colour/continuation context only; not an independent cold repetition or extension of scored grid. |
| Statistics | p.65 generic repeated-sample SD convention; Figure6.23 explicitly says three repetitions | No Figure6.23 experimental-error bars or probabilistic uncertainty supplied. Source-reading bounds are separate. |
| Pairing | Q and pressure are panels of one condition/repetition description | Same represented condition population is a source-based assumption. Individual cross-panel identities and raw pairing remain unauthenticated; pressure merges prevent six qualified permutations. |
| Campaign | Same thesis/2015/Melrose source lineage already registered | Dataset addition adds no independent campaign; no pointwise cross-presentation identity asserted. |

## Pressure calibration discrepancy and support

The printed Figure3.3 caption on p.64/PDF89 is inspected directly. In SI it says

    h(Q) = 1.8e14 Q² + 5.3e8 Q + 1.9e3 Pa.

At Q=1e-5m³/s this is18000+5300+1900=**25200Pa**. The displayed circle/curve
near the same abscissa is approximately**21000Pa**, enclosed conservatively by
20000–22000Pa for this provenance check. The caption expression therefore does
not describe that displayed ordinate within its reading enclosure. The intercept
is **not changed to a minus sign**, coefficients are not refitted, and no assumption
about which expression the author implemented reconstructs Ptrans. Primary
analysis uses only reported Figure6.23 pressure ordinates. Their interpretation
as corrected physical bed pressure remains qualified by this discrepancy.

The calibration displays six experimental circle locations, about3.2e-6 through
1.66e-5m³/s. Conservative endpoint readings are[3.0,3.4]e-6 and[1.60,1.70]e-5m³/s;
these are source-reading enclosures of the observed support extrema, not new
instrument calibration uncertainties. The zero and2e-5 axis limits are not
observations. Each recovered flow enclosure is labelled WITHIN, BELOW, ABOVE
or AMBIGUOUS relative to these uncertain support endpoints. An interval straddling
a support boundary or mixing below/within indications is AMBIGUOUS, not cleared.
Calibration temperature, extrapolation error and how the correlation was applied
at near-floor indications are unreported. No numerical calibration uncertainty
budget is invented; no polynomial extrapolation is applied to repair readings.

## Viscosity provenance and volumetric mapping

pp.256–257/Figure6.19 infer a relative-viscosity/concentration relation by joining
external Navarini extracted-volume curves; measurement temperature is unspecified,
and coffee/water temperature dependence is assumed. Figure6.20 uses different
Psi_B/480kg/m³ conditions: inferred viscosity from1.2e-6m³/s,72°C extraction
aliquots; its caption describes resistance at2.1e-6m³/s. These are neither
synchronized measured viscosity for Figure6.23 nor an empirical bound on it.
The p.257 maximum is printed3.3–3.6 **Pa s**; that unit is unresolved against its
relative-viscosity/water-based provenance. No silent mPa s repair is made.
The author's qualitative viscosity argument is retained as interpretation,
not adopted as a viscosity-only rejection here.

Where actual bed discharge and reported-to-actual pressure equivalence are
supported, define alpha_T(t)=Q_meter,T/Q_bed,T. A hypothetical single-phase,
quasi-static Darcy description gives G_app,T=alpha_T C_geom,T/mu_T. If geometric
conductance is additionally common across the groups, then

    mu_hot/mu_cold = (alpha_hot/alpha_cold) (G_app,cold/G_app,hot).

Only the explicit EQUAL-alpha scenario identifies the plotted ratio with a
required viscosity ratio. Unknown alpha leaves the physical ratio unresolved.
Unknown meter reference density/temperature and storage prevent inventing alpha,
a mass-balance conversion or a density correction. Equal nominal grind and
initial density supply no proof of common later geometry. The published
condition groups are not matched physical cold/hot brews.

## Reading coverage and dependence

The committed contract/coordinates/coverage ledger record anchors, full horizontal
bands, ordinate extrema before guards, identities and unsupported regions. Native
x-axis centre66..464 represents0..70s; y29..342 represents maximum..zero. ±1px
shared anchors contain the axis strokes and internal tick checks. Full horizontal
bands are inverse-affine unions plus2px, rounded outwards. Ordinate ink enclosures
include raster noise/overlap/grid obstruction and add2px before affine conversion.
No central estimate is asserted for envelopes. At a floor, negative lower reading
bounds are clamped to zero for a nonnegative *indication*, with censoring retained.

All retained full condition bands enclose every represented coloured stroke.
Their total hidden/physical count remains UNKNOWN, and there is no all-physical-
repetitions claim. Both pressure and flow coverage are required for a complete
ratio envelope. Overlap does not authorize hidden trajectories or track labels.
The late upper red flow fragment is separately followable25–55s; the earlier
10–20s merged strokes are not bridged into it. Other within-panel tracks are not
reconstructed. Every unknown pressure partner is enclosed by the entire hot
pressure band. No changing-rank pair series is called a physical trajectory.

Pointwise rectangles relax common calibration, displayed time, fixed pairing,
within-panel identities and the Q-dependent pressure correction. Infeasibility
excludes every joint reading contained in the rectangles. Feasibility means only
not excluded by this relaxation; no joint physical/calibration witness is claimed.
