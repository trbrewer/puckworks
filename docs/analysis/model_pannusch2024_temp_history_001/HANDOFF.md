# MODEL-PANNUSCH2024-TEMP-HISTORY-001 handoff

**Full capability qualification: INCOMPLETE.** G2 / NUMERICAL_METHOD_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Issue
[#313](https://github.com/trbrewer/puckworks/issues/313).
Draft PR only, unmerged, auto-merge disabled; no production adoption or successor.
The final exact head and independent nonhuman review/hosted-CI receipts belong
to the draft PR, avoiding a self-referential commit stamp in this document.

The reusable additive module is
`puckworks/models/pannusch2024/temperature_history.py`. Its immutable history,
settings and result contracts expose SI phase concentrations, cumulative solute,
hydraulic volume, requested/actual support, segment diagnostics and source/config
hashes. `COMPLETE` means integration/observer support completed; it does not
mean the call is qualified or physically validated. Each result explicitly
carries `NOT_ASSESSED_FOR_THIS_CALL`. The retained qualification finds substantial
negative interior-liquid states and three failed step-state comparisons.
Do not treat the default path as a verified nonnegative physical predictor.

[RESULTS.md](RESULTS.md) separates implementation, compatibility, temporal,
spatial/accounting, positivity and support/failure dispositions.
[RESULTS.json](RESULTS.json) contains every frozen case and numerical channel.
Original failed gates remain; the resource reserve is not used to retune settings
or replace the source stencil. Source equations/parameters/geometry, both legacy
APIs, registry strength and historical evidence remain unchanged.

## Reproduction and report-only commands

From this repository with `pip install -e '.[dev]'`:

```sh
# Full planned reproduction: choose a NEW directory outside the repository.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_temperature_history_verification execute \
  --evidence-dir "$EVIDENCE_DIR"

# Reduction of retained arrays only; this command never launches simulations.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_temperature_history_verification report \
  --evidence-dir "$EVIDENCE_DIR" --output-dir "$REPORT_DIR"

# Focused CI-sized checks; no external data or full qualification campaign.
python -m pytest -q tests/test_pannusch_temperature_history.py \
  tests/test_pannusch_temperature_history_verification.py
python examples/pannusch_temperature_history.py
```

The example deliberately uses nz=12 and is illustrative, not full-bed numerical
qualification. Runtime API defaults remain nz=200/fine. No generic controller,
new registry component, historical caller redirection or persistent numerical
cache was added. Retained NPZ evidence is immutable output, not a runtime cache.

`execute` resumes only unattempted planned cases. Any named replay consumes a
new execution identity; failures/cancellations remain. A direct worker requires
its reserved launch and single-use claim. The ordinary ceiling is 28 launches,
reserving four final-source correction slots; `--case-id ... --correction` is
only for explicitly identified affected correction evidence within the absolute
32/1800 ceilings. It is not permission for another scientific sweep.

All 27 planned executions completed, comprising **43 segment integrations**,
with **184.456388 charged numerical execution seconds**. Five execution slots
remain; four are still reserved for source corrections. No full-bed correction
or review replay has been performed. Four measured saved-evidence reductions/replays took 42.84 s in total;
including about 5 s of implementer/reviewer diagnostic arithmetic, numerical
work remained below 240 s of the 1800 s ceiling. Reductions do not launch full-bed solves. Raw arrays, logs, XML and local locators remain
outside Git. The committed JSON binds those arrays by SHA-256.

The frozen contract is commit `db83f8f`; pre-execution implementation/input
clarification and numerical source are `a8c94caf35bff300519af9bcffb7d4771c5e9553`.
Every numerical receipt retains that source commit and its exact file hashes.
A reporting-only clarification labels failed numerical qualification explicitly
and gates the resource ceiling. All original/final case metrics, comparisons
and derived observers are identical; that reporting clarification did not change
solver/reference/contract/case bytes or numerical arrays. Original reports are
retained outside Git.

The independent nonhuman review found one P2 input-contract defect: NumPy
complex values could lose their imaginary component during real conversion.
The bounded correction rejects complex scalar/vector/object-backed inputs
before integration. [VALIDATION_CORRECTION.json](VALIDATION_CORRECTION.json)
binds the original/corrected module hashes. Removing only the new rejection
helper and its standalone calls recovers the entire original module byte for
byte; equations, operator, integrator, observer, settings and references are
unchanged. The reporter accepts exactly that hash-bound correction, rejects
other source drift, and reproduces every saved report value unchanged except
its own updated reporter hash. No full-bed rerun or correction slot was needed.
The final focused capability/runner suite has 73 passing tests; the reviewer
checks this delta at the final head in a bounded addendum.

## Software QA and disclosure

Clean baseline: 4,831 quick tests passed, 64 skipped, 760 deselected; registry
66 PASS plus one acknowledged exception; ruff/core mypy/generated status pass.
Scientific-baseline lane: five passed, seven optional plotting-module collection
skips. Skips and deselections are unrun, not PASS. Affected implementation,
legacy and model-contract command: 108 passed; the new focused subset is 69.
Package build/inventory and an installed-wheel small-mesh API/strict-JSON smoke
pass. The generated workflow verifications pass. The candidate quick suite returned 4,897 passed, three failed (stale generated
snapshots, below), 64 skipped and 760 deselected. After regeneration, all 145
focused capability/discovery/status tests passed, including the three failures.
Required hosted CI and independent exact-head review are recorded separately
in the final draft PR receipt, with no automatic qualification upgrade.

The initial candidate suite encountered stale current discovery snapshots after
the live model-card change. The existing `puckworks.insights write` generator
refreshed those snapshots; 93 affected discovery/status/register/packaging tests
pass. No discovery identities, validation-strength labels or historical
scientific outcomes were promoted or restamped. The original failure log is
retained. Current snapshot commit provenance is expected generated metadata.

QA scope disclosure: both full local quick selectors excluded
`protected_target_integrity`. The separately targeted historical
`test_paper_a_model_contract.py` command did select that marked integrity module,
which internally reads legacy Angeloni records/metadata. This was outside the
intended local marker exclusion and is retained as a process deviation. The
isolated subprocess exposed only pass counts, no target values or new scores;
no observation entered parameterization, clocks, settings, thresholds, source
selection or qualification. The contract's baseline phrase “protected lanes
were not run” applies to its broad selector and was too broad for that separate
command; this disclosure corrects it without rewriting the frozen contract.
No further local protected-marked replay is used. Required existing hosted CI
retains its repository selectors; it is separate software integrity QA under
the minimum-governance standard, not scientific target use or capability evidence.

All EWP files/locks, source data/parameters, legacy Pannusch implementation,
Foster/Grudeva/Cameron code, registry, frozen Paper A/I-010/I-076 evidence and
historical release identities remain unchanged. No complete qualification claim
is allowed while the retained numerical failures remain.
