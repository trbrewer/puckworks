# PR 321 targeted correction handoff

**IMPLEMENTED_QUALIFICATION_INCOMPLETE.** All eight maxima qualify; seven of the
original eight comparisons qualify as NO_MATERIAL_DIFFERENCE. The historical
N400/h=.01 unconditioned minimum prefix discrepancy remains unexplained. A single
fresh diagnostic pair passed bitwise checks but does not erase that blocker.
PHYSICAL_VALIDATION=NOT_ESTABLISHED throughout.

[Complete before/after gaps, bounds, paired masses and sensitivity](CORRECTION_RESULTS.md),
[machine-readable results and reuse bindings](CORRECTION_RESULTS.json),
[all-eight reconstruction diagnosis](CORRECTION_MAXIMUM_DIAGNOSES.json),
[prefix diagnosis and missing-field reasons](CORRECTION_PREFIX_DIAGNOSTIC.json),
[cumulative accounting](CORRECTION_RESOURCES.json), and
[external artifact index](CORRECTION_EXTERNAL_EVIDENCE_INDEX.json) form the audit trail.
Original CONTRACT/RESULTS/HANDOFF, numerical campaign and external index remain
historical evidence; this package appends the authorized correction.

## Code and evidence

Native empty queries now check the existing legacy reconstructed state directly,
retaining the raw LP vector and legacy repair separately. Three native maxima
needed no further repair LP. The 007-local bounded joint concentration proposal
uses unchanged 006 LP/checking helpers. Five other maxima passed reconstruction,
all original and actual observation rows, concentration bounds, prediction
allowances and same-state paired replay. The mass-change cap is unchanged.
Optional slack permits equalities/dependent rows without a strict interior;
no observation is dropped and no positive residual is accepted.

The default failed inward problem is independently shown nonempty: the translated
search produced a representable state satisfying its original tightened rows and
boxes exactly, after the historical solver returned status 2 at zero iterations.
That demonstrates a scaling remedy for the reproducer, not a claim about the
internal cause of every old optimizer failure.

The failed minimum was diagnosed with two fresh complete forwards, archived
before process transport, after transport and after immutable-array freezing.
Fresh A/B traces are bitwise identical and match historical A. Old B differs,
but its complete trajectory was not archived. The old first differing index,
time, phase/cell, raw values and ULP distance remain unavailable. No roundoff
allowance, deterministic-execution patch, operator change, favorable-hash retry
loop or qualification promotion was introduced to cover the gap.

Both original complete plans and their prescribed/compiled common pasts are
validated at every operator level under new 007 receipts. All 16 native responses,
original U/bands and checked outer certificates are reused by verified hashes;
original-kg weak duals are independently rechecked. Seven successful minima reuse
their **unaltered historical replay receipts**, bound separately to new validation
identities after exact state/row/prediction/gap and source-function delta checks.
Missing old full trajectories are an explicit limitation of that reuse.
Sixteen fresh maximum trajectories plus two diagnostic trajectories are retained
outside Git with complete inputs/outputs, content/source hashes and failure-safe
indexes. No new backward pass or dense transition operator was used.

The complete post-run archive audit also found two h=.005 future concentration
views altered between child serialization and parent receipt (raw masses and
prefix fields unchanged). The runner now uses checksum/content-verified archive
transport, failing closed on a mismatch. An independent bit-corruption regression
passed before `007-transport-validation-v1` reexecuted all paired checks for the
two affected maxima using four complete verified pre-transport outputs and exact
input identities. This used zero new propagations/LPs and retained the original
receipts independently. [Detailed transport audit](CORRECTION_TRANSPORT_AUDIT.json)
records indices, times, phase/cell, kg values, concentration values/ULPs, operator
inputs, outlet increments and volumes. The internal transport-failure cause and
its relationship to the unavailable historical B trace remain undetermined.

A final reporting-only change counts nested prior repair LPs in the public
`optimization_calls` field. Numerical-run source snapshots and the exact reporting
delta are archived; historical numerical receipts are not restamped. Persistent
budget accounting is authoritative for actual attempts versus reused work.

## Budget and unchanged question

Cumulative **67/80 propagations, 77/160 LPs, 648.190972/1800 charged seconds**;
528,908 exponential actions. Stopwatch campaign time is 588.190972 s; an explicit
conservative 60 s charge covers pre-budget array/hash/state inspections, including
the measured 10.097655 s initial maxima diagnosis. The original task-wide receipt
and evidence directory were reused. Per-call deadlines/action limits and one-thread
settings remain in force. Remaining ceilings do not authorize another campaign.

No original U, band, species, grind, history, primary partition, clock, branch,
target window, operator level, equal-child mapping, volume convention, epsilon
(1e-9 kg), delta (1e-6 kg), response allowance or replay tolerance changed.
Forward modules, `state_envelope.py`, `prefix_conditioned.py`, parameters,
defaults, historical 004–006 artifacts, dependency locks and EWP remain unchanged.
No scientific-stage or registry-rung promotion, empirical score, private-corpus
inspection/exhaustion claim, laboratory work, recipe/taste claim or successor.
First-party licensing remains separate from Pannusch/Schmieder source-derived
CC-BY-NC-3.0 attribution and the existing DOI references.

## Reproduction and delivery

Small, public verification (no private observations or full campaign):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m pytest -q tests/test_pannusch_common_past_correction.py \
  tests/test_pannusch_common_past_contrast.py \
  tests/test_pannusch_common_past_contrast_verification.py
python examples/pannusch_common_past_contrast.py
```

Owner-retained evidence resolves from the same task locator as the original
external index, with the relative `corrections/007-prefix-diagnostic-v1/` and
`corrections/007-joint-witness-v1/` paths. Verify the index hashes before loading
owner-created pickle archives. Pickles retain complete failure/nonfinite outputs;
public JSON remains strict, using null with reasons for missing fields.

The authorized correction commands were:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. \
python -m tools.pannusch_common_past_contrast_verification \
  --output "$EXISTING_007_EVIDENCE_DIRECTORY" --correction 007-prefix-diagnostic-v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. \
python -m tools.pannusch_common_past_contrast_verification \
  --output "$EXISTING_007_EVIDENCE_DIRECTORY" --correction 007-joint-witness-v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=. \
python -m tools.pannusch_common_past_contrast_verification \
  --output "$EXISTING_007_EVIDENCE_DIRECTORY" --correction 007-transport-validation-v1
```

These names are already consumed and deliberately reject repeated execution.
Changing output directories does not reset the budget. Reproduce checks from the
archived arrays and receipts; this handoff authorizes no additional propagation.

[PR #321](https://github.com/trbrewer/puckworks/pull/321) remains the single draft,
unmerged, with auto-merge disabled. Starting reviewed head:
`28fe6c36873fa52965b9413dd3ab7d2b6316a773`, tree
`ccc9a1752355afd1650c733c14c2554c5a6ad1d1`. Actual base/main:
`f08677b177d9569068941cbb602c7b88f3aca769`, tree
`1c372d9845e4f71997d0939de12ff5cc368d1df4`. EWP:
`73ec476ffe6ac626705ca949e28b32935ddf2992`, tree
`8ced37ad5b294616b8935d92a57e3845321d5eed`; lock SHA256
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
The exact amended head/tree and same-head hosted results are recorded on the PR
and final delivery receipt, avoiding self-referential commit claims in this file.
[Changed files](CORRECTION_CHANGED_FILES.json), [QA](CORRECTION_QA.json),
[preservation](CORRECTION_PRESERVATION.json), and
[ordinary review](CORRECTION_REVIEW.md) distinguish software, numerical,
review and hosted infrastructure status. No merge, release or production adoption.
