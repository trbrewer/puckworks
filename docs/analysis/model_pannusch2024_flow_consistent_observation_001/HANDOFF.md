# Flow-consistent observer 001 handoff

G2 / NUMERICAL_METHOD_CHANGE / RESEARCH_ONLY.
**VERIFIED_ON_DECLARED_CASES** applies only to
`pannusch2024.flow_consistent_observer.volume_clock.v1` on the frozen synthetic matrix.
Runtime accuracy remains NOT_ASSESSED. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Result and limits

The explicit `observe_flow_consistent_fv` entry point reconstructs interiors in a
prescribed-volume clock and directly evolves local delivery. All original primary
states, whole-step deliveries and checkpoint identities remain authoritative.
It validates current-source identity, physical views and contiguous checked
support, independently checks new phase states and actual-Q closure, and publishes
only complete checked fractions. The entire frozen generator, including phase
exchange, is clock-scaled; this is a numerical continuous extension, not exact
continuously varying chemistry or a new physical rate law.

The controlling window remains exactly [2.737002188183808, 2.74] s.
Concentrations are kg/m^3; signed errors use original C*=9.172575 kg/m^3.

| h (s) | Old | New | Physical-time reference | Old error/C* | New error/C* |
|---|---:|---:|---:|---:|---:|
| .04 | 3.42241630940 | 3.42314777231 | 3.42314923737 | -7.99042763e-5 | -1.59721694e-7 |
| .02 | 3.42128802772 | 3.42314884636 | 3.42314923737 | -2.02910268e-4 | -4.26277041e-8 |
| .01 | 3.42238278103 | 3.42314914141 | 3.42314923737 | -8.35595614e-5 | -1.04620018e-8 |

| New/reference maximum normalized error | .04 | .02 (default) | .01 |
|---|---:|---:|---:|
| Liquid phase | 1.41159599e-6 | 3.66696589e-7 | 8.45250361e-8 |
| Fine phase | 1.33868470e-6 | 3.35871527e-7 | 7.72887479e-8 |
| Coarse phase | 8.74382614e-8 | 1.85419782e-8 | 3.82554979e-9 |
| Outlet | 2.71418025e-7 | 7.04197533e-8 | 1.62570469e-8 |
| Root delivered mass | 6.88929132e-8 | 1.72844964e-8 | 4.32111711e-9 |
| All 17 fractions | 1.59721694e-7 | 4.26277041e-8 | 1.04620018e-8 |

[RESULTS.md](RESULTS.md) lists every mandatory gate and all comparison channels.
[RESULTS.json](RESULTS.json) retains old/new errors, all 17 old/new/reference
fractions at all levels, 86 observation summaries, original endpoint comparison
support, signed inventories, local/root scales, volumes and reference controls.
Complete phase values remain in externally retained, hash-bound arrays.
The single tighter Radau control differs by at most 1.08803e-12 on the original
scales and resolves both absolute gates and aggregate ordering; this is a
resolution control, not a rigorous error certificate.

The default controlling-window actual-Q GL8/direct closure is 3.30872e-24 kg
(8.27138e-17 on concentration/C*), against the frozen 8.00041e-19 kg local allowance.
GL8/GL4 differs by zero there. N400/N800 maxima are 5.81984e-4 for capacity-weighted
fields, 2.78153e-4 for mass and 3.82555e-4 for fractions, within the unchanged .005
allowances. This is bounded mesh sensitivity, not continuum validation.

## Dispositions

| Dimension | Disposition |
|---|---|
| Implementation | IMPLEMENTED; opt-in only |
| Conservation / signed nonnegativity / volume | PASS |
| Actual prescribed-flow consistency / local closure | PASS |
| Temporal accuracy / reference resolution / aggregate decrease | PASS |
| Mesh sensitivity | PASS on declared N400/N800 comparison |
| Genuine stopped-prefix/resume / lineage-checked recombination | PASS; same-schedule differences zero |
| Explicit branches / independent physical-time reference | PASS |
| Same-environment numerical repeat | PASS for every saved numerical array; runtime metadata separate |
| Ordinary software QA | See [QA.json](QA.json); no historical selector exception |
| Hosted CI | Pending at bundle authorship; exact final-head receipt belongs to the draft PR |
| Independent review | Pending at bundle authorship; one nonhuman exact-head review and any bounded addendum belong to the draft PR |
| Physical validation | NOT_ESTABLISHED |

## Provenance, execution and resources

Live PW main matched b9ad38c6ebfe96d90462254dfb664dd789036b31 (tree
9f1f93cf0147784055e9e9d2110b66b9e5ed2074); EWP main matched
16eec1dda24ebf658965eddcf1a6fffa81903b32. Both remained unchanged at final refresh.
No equivalent work was found; #321 was excluded and completed #324 was not reopened.
The feature worktree preserves all dependency-hashed legacy numerical modules,
historical 004 evidence, 005/006/007 operators, workflows, dependencies and defaults.

All 29 candidate/legacy/reference integrations are **new**, produced at commit
780fbda0edb27ffcd2bae85bc10650a41612df17, tree
d30b328c19e726f27ff31e72042aaef1e0f3eac6. Attached observers are charged with their
producing integration. Later runner edits affect reporting only: bounded-memory
reduction, full saved-array repeat comparison and strict-JSON scalar conversion.
The numerical runner blocks and all numerical dependency hashes are verified
unchanged before reduction; original producer identities are never rewritten.

[RESOURCES.json](RESOURCES.json) records 29/36 execution slots and
1212.6755001830024/3600 charged seconds: 1111.2660759529972 integration seconds,
12.212339675999829 archive-audit seconds, a retained failed 44.50836168299429-second
report attempt (NumPy boolean JSON serialization), and a successful
44.68872287101112-second report. Zero integration failures or correction replays;
all seven correction slots remain unused. Maximum integration invocation was
100.50022652299958 seconds, below 120. One numerical worker and one BLAS thread;
every numerical/auxiliary process is capped at 2 GiB. Reservations are held in the
existing Git-common-directory authority; external receipts, logs and arrays have
one bound location. Ordinary small tests and silent integrity QA are separate.
No numerical successor follows this campaign.

[EVIDENCE_REUSE.json](EVIDENCE_REUSE.json) verifies original producer, source,
input, plan, array and checked-support bindings. Its reuse is historical comparison,
source lineage and the diagnostic attributed to original producer
d691b055e8900f6547d4a5d4e5ec9f58f093bc8c (~99.81%, 99.98%, 99.99% flow-weighting
explanation). No legacy checkpoint is deserialized, migrated or presented as a
current result. All necessary current checkpoints and reference samples were
newly produced. Inspected repository equations, capacities, geometry, parameter
and provenance records; reused the recorded original MATLAB/source inspections.
No new original-source acquisition or experimental-value access occurred.
Pannusch et al. DOI 10.1016/j.jfoodeng.2023.111887, Mendeley
10.17632/y2tz67f6ry.1, and Schmieder shared lineage retain their attribution.
Source-derived output remains CC-BY-NC-3.0, separately from first-party software.

## Reproduction

Small offline example and focused QA, with existing project dependencies:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m examples.pannusch_flow_consistent_observer
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q tests/test_pannusch_flow_consistent_observer.py tests/test_pannusch_flow_consistent_verification.py tests/test_pannusch_stateful_fv.py tests/test_pannusch_stateful_fv_verification.py
```

Recorded bounded campaign commands (outside normal CI; `EVIDENCE_DIR` denotes
the private bound evidence location, not a public raw-data path):

```bash
python -m tools.pannusch_flow_consistent_verification audit --evidence-dir "$EVIDENCE_DIR"
python -m tools.pannusch_flow_consistent_verification execute --evidence-dir "$EVIDENCE_DIR"
python -m tools.pannusch_flow_consistent_verification report --evidence-dir "$EVIDENCE_DIR"
```

The authority skips attempted integrations and retains failed auxiliary work.
Reproduction does not grant a new budget or an automatic retry. The archive-audit
command requires the original private retained evidence; public summaries are
not a substitute for unavailable bytes. Full ordinary QA commands, selectors,
versions and log hashes are in QA.json. The draft PR supplies its final exact
head/tree, hosted checks and independent-review disposition.

No merge or auto-merge, release, production adoption, EWP/Guided Pull change,
parameter retuning, experimental fit/score, envelope extension or successor.
Measured initial state, empirical accuracy, source sensor/flow equivalence,
new hydraulic prediction, taste and physical validation remain unestablished.
