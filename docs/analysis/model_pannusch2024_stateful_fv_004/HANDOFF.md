# MODEL-PANNUSCH2024-STATEFUL-FV-004 handoff

G2 / NUMERICAL_METHOD_CHANGE, including an explicit initial-condition extension.
RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED; runtime accuracy NOT_ASSESSED.
Governing balances, source parameters, source geometry and constitutive laws
are unchanged. No production adoption, empirical scoring, fitting or coupling.

## Recorded outcome

**IMPLEMENTED_QUALIFICATION_INCOMPLETE**. All 28 planned integrations completed;
no failed trajectory, correction replay or extra prefix. All four correction
slots remain unused. One failed reporting-only reduction (strict JSON NumPy
scalar conversion) is retained and charged; only the metric reporter changed.
Execution wall time 577.091886 s; total with
three reductions and the constructor-only identity proof 781.137745 / 1800 s. Every invocation was <=120 s.

| Disposition | Result |
|---|---|
| Implementation | Implemented; explicit state/stop/resume/branch API |
| Input-state verification | PASS on declared synthetic fields and small tests |
| Same-schedule continuation | PASS; S/L primary masses bitwise equal; fields/mass/fractions zero difference |
| Branching | PASS; worst fixed-scale reference difference 4.68656135e-14 |
| Temporal checks | FAIL aggregate decrease; all individual 5e-4 bounds pass |
| Mesh checks | PASS; bounded N400/N800 sensitivity only |
| Software QA | PASS: full unprotected regression, affected correction tests and packaging; QA.json |
| Hosted CI | PENDING; excluded protected-target lanes are in current selectors |
| Independent nonhuman review | Initial review required one input correction; final bounded addendum on draft PR #318 |

The frozen short fraction [2.737002188183808,2.74] s controls the temporal
aggregate: .04/.02/.01 errors are 7.99042763e-5 / 2.02910268e-4 /
8.35595614e-5 C*. These do not decrease monotonically above the 1e-10 floor.
No window is dropped, threshold widened, aggregate redefined or method replaced.
The failure is retained; it blocks VERIFIED_ON_DECLARED_CASES even though all
other mandatory numerical gates pass. No new campaign or successor is started.

Worst equilibrium compatibility: 2.07072454e-13; worst U/S independent reference: 1.34287207e-13
on the corresponding fixed concentration/inventory scales. Default/finer:
0.000119350706. N400/N800 weighted field,
mass and fraction errors: 0.000581983846,
0.000278152878, 0.00038255497.

| Independent accounting | Worst scaled error | Case |
|---|---:|---|
| local_inventory | 9.51560671e-14 | B.trigonelline.ORDERED |
| origin_inventory | 9.51560671e-14 | B.trigonelline.ORDERED |
| local_volume | 2.32881094e-16 | D.caffeine.PREFIX |
| origin_volume | 2.32881094e-16 | D.caffeine.PREFIX |
| numerical_flux | 1.86036814e-16 | A.tds.EQUILIBRIUM |
| prescribed_flux | 8.21192625e-07 | D.coarse |
| numerical_GL8_GL4 | 1.86036814e-16 | A.tds.EQUILIBRIUM |
| prescribed_GL8_GL4 | 1.86036814e-16 | A.tds.EQUILIBRIUM |

All phase-positivity and monotone outlet-increment checks pass without clipping.
RESULTS.json retains absolute and signed initial/final/min/max residuals, local
and root scales, every fraction error, and exact schedule/raw-state comparisons.

## Bounded input-validation correction

Independent nonhuman review of `0db72e9d252c926f13ccc6b634a5ab0d6bf77866`
found that an original `Fraction`/extended-precision concentration could round
to zero before the inherited real-number conversion checked it. Both a tiny
positive inventory and a tiny negative input could therefore be hidden.
Corrected code `fb7b9d38a75d4050742a6690117b86d7ec62fc3c` adds model-local
rejecting guards. All 189 affected tests pass, including all phases, positive
and negative underflow, extended precision and representable rational inputs.
The legacy history conversion and FV propagation are unchanged.

[EVIDENCE_REUSE.json](EVIDENCE_REUSE.json) binds exact old/new runtime and
loader identities. Removing only the inserted guards recovers the complete
original runtime file byte-for-byte. All 15 declared fresh constructor uses
retain bitwise-identical binary64 fields, phase masses and inventories. The
proof ran zero integrations and rechecked all 28 original receipt/array hashes.
Original qualification remains attributed to producer
`d691b055e8900f6547d4a5d4e5ec9f58f093bc8c`, not to the corrected head. The
updated report separately records current reporting and original producer
identities; every gate, error, accounting value and disposition is unchanged.
Only this complete exact identity pair is eligible for saved-evidence reuse.

The correction changes source/checkpoint identities. Retained frozen checkpoint
payloads remain evidence at their actual producer version; the corrected public
API deliberately rejects them as migration inputs. New current-version runs
create compatible current-version checkpoints. No checkpoint is relabelled or
migrated. No correction trajectory or successor was started.

## Public operations

Import the model-local API from `puckworks.models.pannusch2024.stateful_fv`:

1. Construct an immutable `FVChemicalState.source_equilibrium(...)` or
   `FVChemicalState.from_cell_averages(...)`. The latter requires separate
   liquid/fine/coarse arrays, source mesh edges, species, grind and finite
   absolute time. Each array is in kg/m^3 on its own source phase basis.
   Fresh calculation starts with zero collected mass and volume at that time.
2. Construct `FVPlan(temperature_history, flow_history, full_span, settings)`.
   Use `simulate_stateful_fv(plan=..., initial_state=..., stop_time_s=...)`
   to stop at an existing endpoint of this original full plan. Export via
   `result.checkpoint(time_s)`, then use
   `simulate_stateful_fv(checkpoint=..., observation_times_s=...)` to resume.
   The saved exact endpoints and midpoint forcing remain authoritative.
3. Construct a new plan starting at checkpoint time and call
   `branch_stateful_fv(checkpoint, plan=..., observation_times_s=...)`.
   This explicitly changes future forcing and preserves chemistry, root clock,
   earlier mass/volume accounting and parent identity. The checkpoint can be
   reused independently. Supplying changed forcing as a resume is rejected.

Each result exposes root time, continuation start and actual end; phase fields,
remaining inventory, segment/origin solute and segment/origin prescribed volume.
Requested observations carry individual support reasons. `primary`,
`raw_primary_masses_kg`, diagnostic samples and quadrature retain finite raw
numerical diagnostics; `exportable_primary` identifies the admissible checked
prefix. Raw diagnostics are not supported accuracy certificates. Unsupported
requested observations and public fraction concentrations are absent with
reasons. Signed initial/final and worst local/origin/interval residuals are
retained. Integration completion, sampled admissibility and accuracy are distinct.

The interval outlet accumulator starts from zero for each exponential action;
phase masses carry unchanged. Historical offsets remain separate terms, so a
small local delivery need not disappear when a rounded cumulative scalar is
unchanged. Fractions integrate local delivery directly. Hydraulic volume uses
the prescribed history's analytic integral. A zero-duration/zero-volume
concentration is undefined. A truly zero root inventory stays numerical zero;
an unresolved positive-state increment is not reported as exact zero.

The [offline example](../../../examples/pannusch_stateful_fv.py) uses only these
public operations with N4 and 0..0.11 s. Its five small integrations are API
illustrations, separate from qualification; it contains no manufactured checkpoint.
The unchanged legacy API remains available with its existing result meanings.

## Evidence and reproduction

[CONTRACT.md](CONTRACT.md) and [CASES.json](CASES.json) were frozen before full
qualification at `d691b055e8900f6547d4a5d4e5ec9f58f093bc8c`.
[RESULTS.md](RESULTS.md) and [RESULTS.json](RESULTS.json) contain every frozen
numerical gate, fixed scale, signed residual, comparison and failed/incomplete
execution. [RESOURCES.json](RESOURCES.json) records each pre-reserved launch and
report-only reduction. [QA.json](QA.json) separates software checks from
numerical qualification, hosted CI and the independent exact-head review.
Detailed arrays, full logs, checkpoint payloads and the task authority stay
outside Git. No source/data/001/002/003 evidence was restamped.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m tools.pannusch_stateful_fv_verification execute \
  --evidence-dir "$EVIDENCE_DIR"

# Saved-evidence reduction only; no numerical integration.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m tools.pannusch_stateful_fv_verification report \
  --evidence-dir "$EVIDENCE_DIR" --output-dir "$REPORT_DIR"

python -m pytest -q tests/test_pannusch_stateful_fv.py \
  tests/test_pannusch_stateful_fv_verification.py -m 'not protected_target_integrity'
python examples/pannusch_stateful_fv.py
```

The Git-common-directory task budget is bound to the evidence location;
changing output directories cannot reset it. Every launched baseline, prefix,
suffix, reference, branch, failure and repeat counts. No automatic retry occurs.
Only a named affected correction can consume a reserved correction slot.
Full qualification is outside ordinary CI. Ordinary regression and N<=12 tests
are separately identified and contain no hidden full-bed campaign trajectories.

## Authority and unsupported scope

Actual reviewed Puckworks base: `58b6cd2f29af3fa4372119ba59f8a6a1446369cc`,
containing merged PR #317. Reviewed EWP main:
`73ec476ffe6ac626705ca949e28b32935ddf2992`; the owner's EWP checkout remains
unchanged at `78cbd59c751393cddfe539e4c69e43a224329bca`.
The sole feature worktree uses `model/pannusch2024-stateful-fv-004`.
[SOURCE_IDENTITIES.json](SOURCE_IDENTITIES.json) proves preservation of prior
runtime files and 001/002/003 historical artifacts. Current 003 lifecycle
metadata records the actual #317 merge. No automatic successor was selected.

[INTAKE.json](INTAKE.json) gives every reused original filename and SHA-256:
eight original MATLAB text inspections from the existing 001 receipt, verified
through the scoped 003 reuse mechanism. No original external file was freshly
inspected or executed. Repository source equations, geometry, parameter tables,
code provenance, catalog metadata and retained EWP flow/input-mapping results
were inspected. Relevant IDs are `pannusch2024/table2_params`,
`pannusch2024/experimental_kinetics`, and literal `pannusch2024 (Mendeley repo)`.
Schmieder fractions have shared lineage, not independent observations.
Unavailable external originals are known evidence unavailable here, not absent
or exhausted. No assay value or protected prediction target was needed.

The immutable types check structural/numerical compatibility; they cannot prove
a caller's concentrations were measured or truthfully labelled. Checkpoint
hashes detect corruption, not authenticity. Cross-model conversions, remeshing,
arbitrary-observation restart, old-version migration, general cross-checkpoint
fraction queries, coupled hydraulic/thermal solving and global shot-chain
interfaces remain unsupported. Qualification does not extend to every possible
supplied state or history. N400/N800 is bounded mesh sensitivity, not an
asymptotic order or continuum/physical validation. Prescribed histories are
synthetic, not experimental reconstructions. EWP flow-authority/input-mapping
restrictions remain. No whole-shot, taste or predictive-improvement claim.

Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887; source code/data DOI
10.17632/y2tz67f6ry.1. Source-derived artifacts retain CC-BY-NC-3.0 separately
from first-party code licensing. No rights-restricted original is copied.

The deliverable is [draft PR #318](https://github.com/trbrewer/puckworks/pull/318),
unmerged with auto-merge disabled. The exact final head and independent nonhuman
review/addendum are recorded on that PR. Hosted
quick/quality selectors currently include protected-target lanes excluded by
this authorization; workflow thresholds remain unchanged, and skip-CI commit
markers prevent that unintended execution. Hosted CI therefore remains pending,
not green. Independent nonhuman review is a separate exact-head receipt on the
PR. No release, dependency-lock change, laboratory operation, contact or successor.
