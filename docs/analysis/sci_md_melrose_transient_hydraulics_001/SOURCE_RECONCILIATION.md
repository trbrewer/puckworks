# Sources, collection observer and applicability

G1 / NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
The primary numerical population is the displayed Figure 2 markers only.

The inspected [packed-bed preprint](https://www.researchgate.net/profile/John-Melrose/publication/333220524_Modelling_polydisperse_diffusion_kinetics_of_Coffee_Brewing-bed/links/5da0b0d5299bf116fe9ec762/Modelling-polydisperse-diffusion-kinetics-of-Coffee-Brewing-bed.pdf)
is dated 26 September 2019 on its title page, 29 PDF pages, SHA256
`20b7990af4a9026b44d56a29b559ab0d02f4a094d5a3e171b8d1bb41ae58c6ed`.
ResearchGate's landing-page May 2019 listing and October 11 upload metadata
are not the title-page version date. Figure 2 is printed/PDF p.11; Figure 1a/b
and its caption are pp.9–10. The [thesis](https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf)
has 359 pages, SHA256
`f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818`.
Both held originals match the requested review copies exactly. Actual original
pages/images were inspected, not only OCR or the repository cards.

| Fact | Source/page (printed / PDF) | Inspected statement, paraphrased | Applicability to Figure 2 | Conflict or missing linkage | Adopted treatment |
|---|---|---|---|---|---|
| Campaign | Preprint 2–3 / 2–3 | Further analysis of Corrochano's packed-bed measurements | Same campaign provenance | Not an independent replication; later presentation need not have identical pointwise aggregates | Thesis methods support; no thesis ordinates added or double counted |
| Primary quantity | Preprint 10–11 / 10–11 | Each aliquot volume divided by the collection interval gives flow during that interval | Direct Figure 2 description | No instantaneous-flow reconstruction | Analyze interval-average plotted ordinates |
| Identity convention | Preprint Figure 1 caption 10 / 10 | B triangles, C squares, D diamonds, E circles; open 480/closed 400; convention extends to other figures | Direct convention, checked against native Figure 2 | Two LF triangles look open; dense overlaps hide glyphs | Separate observed fragments and candidate condition sets; no forced fill assignment |
| Intended grid and thesis coverage | Thesis Table 7.1, 276 / 301 | Fifteen entries; B480 has LF only | Supports campaign condition vocabulary | Does not prove B480HF absent from later preprint | B480HF not distinguishable in Figure 2, unresolved representation; never fabricate a sixteenth curve |
| Fixed pressure | Preprint §2.3 4 / 4 and 10 / 10 | Fixed applied overpressures LF 1.75/HF 3.75 bar; nominal mean flows 1.3/3.7 mL/s | Direct source statement | Applied pressure is not demonstrated constant bed drop | Retain values as preprint-reported applied overpressures, 175000/375000 Pa; nominal flows are not imposed constant flow |
| Pressure selection | Thesis 90,273 / 115,298 | Tank pressure chosen by grind and packing to obtain LF/HF | Same campaign method | Conflicts with a universal numerical assignment of LF/HF pressures | Retain both accounts; no cross-pressure calculation or silent choice |
| Pressure nodes | Thesis 63–64 / 88–89 | Regulated compressed-air tank, upstream flowmeter; separate pre-cell transducer; empty-cell losses subtracted for bed drop | Apparatus context | No Figure 2 synchronized bed-drop trace; exact gauge/outlet reference and dynamic validity not joined | Fixed tank head, pre-cell pressure and bed drop remain distinct; no imported numerical loss adapter |
| Collection/timing | Thesis 90,274 / 115,299 | Weighed aliquots; 5 s HF and 10 s LF; 7 and 8 samples in described experiments | Authenticates campaign interval-rate method | Does not prove exact Figure 2 endpoints, time alignment or hidden sample counts | Durations recorded with linkage qualification; endpoints null; order supported by successive aliquots and separated displayed times |
| Origin | Preprint 11 / 11 | Zero when first drop leaves bed | Direct | Not valve opening or shared physical state across conditions | Within-profile first-drop time only; abscissa end/midpoint convention unknown |
| Mass-to-volume | Thesis 90,274 / 115,299 | Mass converted assuming approximately water density at same temperature (~1000 kg/m3); concentration-dependent error reported 1–3% | Supports method behind volume-rate ordinate | No pointwise density series, correction signs/correlation or uncertainty distribution | Keep separate from reading enclosures; no synthetic symmetric pointwise experimental errors |
| Repetitions | Preprint Figure 1 caption 10 / 10 | Data averaged over 3–4 repetitions; shown bars are sample SD | Explicitly Figure 1 | Does not specify Figure 2 members, aggregation operation or weights | UNSPECIFIED_PUBLISHED_AGGREGATE; no manufactured replicate rows or physical-brew count |
| General statistics | Thesis 65 / 90 | General plus/minus SD reporting, typically three samples; propagation rules | General campaign reporting convention | Wording does not establish Figure 2 SD/SEM, pointwise membership or fixed weights | No Figure 2 error bars claimed; no confidence intervals or independent digitized-point resampling |
| Early outlet observer | Thesis 274 / 299 | Inlet and outlet flows differ early because upstream circuit fills and grounds absorb water | Direct warning relevant to observer | No time at which storage becomes negligible is established for every profile | Inlet=outlet=collected flow unqualified; no hydraulic eligibility based only on nominal pressure |
| Thermal transient | Preprint 4 / 4 | Inlet set 85°C, outlet initially~60°C then75–80°C after 5–10 s | Direct campaign statement | No in-bed temperature/viscosity field; interval endpoints unknown | Early HF witnesses involve this region; no post-hoc cutoff or later isothermal claim |
| Gas and authors' interpretation | Preprint 11–12 / 11–12 | Most HF curves fall toward~20 s; LF falls toward~40–60 s then rises mildly; gas observed in clear outlet tube; fines/gas suggested | Qualitative authors' interpretation | Not a mechanism identification or quantified storage correction | Keep authors' description separate from recovered finite comparisons |
| Resistance sign | Preprint 11 / 11 | Text describes rising resistance as falling flow but also says changes are proportional to flow | Literal proportionality wording is inconsistent with fixed-drop R=P/Q | Applied pressure vs bed drop adds qualification | Record text inconsistency; resistance is inverse to Q at fixed relevant drop; no flow-to-intrinsic-permeability conversion |
| Cross-presentation identity | Thesis Figure 7.1, 274 / 299 | Example E traces and average/cumulative presentations | Supports observer only | LF E presentations are visibly different from preprint circles; no point-for-point join authenticated | Never recover hidden preprint markers from thesis values, functions or curve shape |

Preparation statements carried in `contract.json`: grinds B/C/D/E with reported
volume mean sizes 200/260/325/360 µm and fines fractions 36/27/20/17%; cell
 diameter 3.7 cm; doses 8 g at 400 kg/m3 and 9.5 g at 480 kg/m3; reported 480-bed
height 1.8 cm. These are source statements, not per-replicate records. An
unassigned triangle's density and dose remain candidates, not known covariates.

## Source access and nondeduplication

Existing external-data config resolved the authorized inventory and source root.
The pre-existing inventory was queried for Melrose/Corrochano names, without a
new corpus scan. Eleven relevant existing structured files (2015 table and 2017
tables/fit summaries) were opened and rehashed; all matched inventory identities.
None contains a verified machine-readable mapping to Figure 2's temporal
ordinates. The later-held PDF subtree supplied the exact two originals; PDFs
were individually hashed, not treated as new measured datasets. Direct preprint
curl returned403; browser access worked. A slow thesis HTTP request timed out;
the held exact-hash original supplied the source, so this did not block recovery.
No absence or exhaustion claim about uninspected holdings follows.

Repository result/code searches and GitHub searches for Melrose, task ID and
fig2_flow_transient found no equivalent intake. The existing Melrose card and
blocked-intake item were reused and corrected narrowly. The Corrochano
permeability tables describe a different observable/steady-state regime and
are not substitutes. EWP's accepted result was read directly with `git show`
at its supplied revision; EWP was not changed.

## Bounds, order and coverage

Figure 2's embedded JPEG is 957×678 pixels (object29, ~209ppi in the PDF).
`contract.json` records its hash, axes, shared calibration uncertainties and
internal tick checks. `source_coordinates.csv` contains actual visible-glyph
rectangles before the declared 1 px raster guard. Coordinates are native, not
upsampled. A null y center means the marker's identity/presence and enclosure
are retained without inventing its hidden center. The affine-corner transform
produces the normalized bounds in `observations.csv`. Full glyph footprints
make conservative reading bounds; these are neither experimental errors nor
replicate variability. Shared calibration couples the readings; rectangular
compatibility is explicitly a relaxation.

All retained within-fragment x enclosures are separated. Thus the actual
supported order here is total within each fragment, and its all-pairs closure
is used. The general code also handles partial orders without arbitrary time
sorting. Independently, the collection description supports successive
nonoverlapping aliquots in the described experiments. This does not authenticate
pointwise aggregation across repetitions. Different LF triangle fragments are
not joined across the obscured middle.

`condition_results.csv` covers all 16 planned slots. Ten conditions have
recognizable assigned markers. Two distinct LF triangular tracks are visibly
present, but their density mapping and continuity through the dense region are
unresolved: four fragments are retained, never credited to both candidate
conditions. At least12 distinct traces are distinguishable (7 HF, 5 LF); total
Figure 2 profile and observation counts cannot be established reliably.
B480HF, D400LF, D480LF and E400LF have no separately identifiable assigned
markers in this recovery; this does not prove their absence from the source.
The ledger's blank counts in `ambiguous_regions.csv` mean UNKNOWN, not zero.
Regions can overlap retained glyphs: they account for unresolved remainder,
not additional observation rows. Every recognizable glyph was considered;
none was selected for decline strength or excluded merely for flatness.
