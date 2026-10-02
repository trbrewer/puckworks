# MODEL-GRUDEVA2026-REDUCED-001 results

**GRUDEVA2026_STANDALONE_NUMERICALLY_VERIFIED_REFERENCE_INCOMPLETE**.
G2 / NUMERICAL_METHOD_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
The standalone equations are numerically verified on the declared cases.
Published Figures 3/4 are **not reproduced** at the source parameters and frozen
budgets; Figure 5 remains **FIG5_REFERENCE_INCOMPLETE**. Issue #67 is incomplete.
This is neither physical validation nor rejection of the model's physics.

| Gate | Disposition / actual evidence |
|---|---|
| Source/math contract | PASS: primary Eqs.67–75, corrected grouping and clocks; independently derived kernel; explicit source/configuration identities |
| Analytic grain/front | PASS: independent scalar analytic fixtures, constant-front root, flux and grain mean, time shifts, equilibrium and uptake |
| Conservation/boundedness | PASS: all six qualification runs; max normalized residual 1.78e-9; positive-pore synthetic case 1.48e-9; no clipping |
| Spatial refinement | PASS: 128 to 256 graded cells, max smooth outlet change 1.1551e-4, event change 3.1561e-6 |
| Time refinement | PASS: tolerances /10, max step /2; outlet 1.4110e-8, event 4.8549e-9 |
| Grain modes | PASS: 32 to 64 plus conservative positive tail; outlet 6.0180e-9, event 1.1337e-8 |
| Figures 3/4 | FAIL reproduction: Figure 3 max selected smooth concentration error .09753, front error .01345; Figure 4 smooth error .14133, event error .12085 |
| Figure 5 | INCOMPLETE: full-model spatial arrays, exact diffusivity coefficient and author observation grid unqualified |
| Native Laboratory | Implemented: dedicated reference case, source/use preflight, canonical card, no common-scenario adapter; full integration tests recorded in HANDOFF |
| Regression / hosted QA | See HANDOFF; separate from numerical/reference dispositions |
| Independent review | Pending exact candidate review; receipt will identify the reviewed PR head |

The numerical budgets remain 1e-3 for outlet/event refinement and 1e-6 for
normalized conservation. The initial uniform-mesh 512/1024-cell trial failed
outlet refinement (.002844 at t=6.53). A mesh graded toward newly activated
grains resolves the spatial short-age layer. That numerical correction changes
neither equations nor published parameters. The development record is in
CONTRACT.md; the failed trial is retained outside Git.

For the explicit Eq.76/Eq.77/Table-2-dimensionless case, desaturation exits at
**6.5043092876**. The digitized Figure 4 event is **6.3834586466 ± .0100251**
(pixel-location uncertainty), versus the frozen .025 acceptance budget. This
mismatch persists under all three refinements. No initial concentration,
phase fraction, Q value or budget was adjusted to make it reach 6.4.
Table 1's 310/224 is retained as an inconsistent source alternative, not used to
retune the Figure case. No claim is made about which undisclosed author setting
or printed/source implementation detail caused the discrepancy.

Smooth concentration error excludes the full interval between the two displaced
jumps, with margins; front/event displacement is scored separately. The original
observation implementation excluded only each endpoint's margin, wrongly leaving
part of the displaced-jump interval in a smooth metric. This bookkeeping was
corrected using the unchanged, hash-verified numerical outputs. Neither reference
verdict changed. Selected raster samples have explicit concentration/coordinate
uncertainty; these are resolution-supported comparisons, not the authors' arrays.
The Figure 5 error curve alone supplies no independent test of this solver.

Inventory unit: phi_T*A*L*c_sat. Initial inventory is beta*c_f_init +
delta*c_b_init; wet boulder inventory includes the intragranular pore refill once.
The ledger separately carries external liquid, fines, boulders and discharged
solute. Before drip, discharge is identically zero. First drip=1 is model-derived
under prescribed flow; it is not an independent hydraulic measurement. The
positive-pore synthetic run tests redistribution that the publication's zero-pore
case cannot test. Finite-mode short-age regularization, incomplete/censored events
and unsupported saturated-layer conditions are explicit API states.

Normal reference runtime was about 7.7 s in the recorded environment; the runner
is conservatively `batch-only`. No refinement sweep executes in the runner or on
import. Runtime is excluded from scientific hashes. The quick gate performs real
analytical-fixture comparisons and a short coupled conservation run, not a saved
PASS lookup. Tests cover units, inventory conversions, separate clocks, partial
horizons, invalid inputs, grain uptake, canonical serialization and import behavior.

Reproduce (NumPy/SciPy plus project dependencies, no network):

```bash
OPENBLAS_NUM_THREADS=1 python -m puckworks.models.grudeva2026 \
  --refine --output /tmp/grudeva2026-results.json \
  --raw-directory /tmp/grudeva2026-runs
python -m pytest -q tests/test_grudeva2026.py
python -c "from puckworks.product.lab_runners import execute_runner; print(execute_runner('grudeva2026.reduced'))"
```

Fixture extraction is a separate offline provenance tool, requiring PyMuPDF and
Pillow, with an explicitly supplied article PDF (never downloaded on import):

```bash
python tools/grudeva2026_extract_reference.py \
  --article-pdf ARTICLE.pdf --output /tmp/publication_reference.json
```

Small source fixtures and attribution are in `puckworks/data/grudeva2026/`.
RESULTS.json contains exact metrics, numerical controls, inventory ledger,
source/fixture hashes and environment. Complete successful/failed raw runs and
test logs remain outside Git. EWP, its dependency lock, all previous scientific
results and the existing Grudeva/Cameron implementations remain unchanged.
