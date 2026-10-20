# Cameron conservation-gate correction — R-05/T06

## Bounded plan (recorded before gate edits)

G0 / NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Connect the registered conservation gate to the independent numerical inventory
requirements already in `tests/test_cameron_inventory.py`, demonstrate rejection
of the historical interpolation fault, and correct only its current claims and
dependent projections. No production model change, empirical accuracy requirement,
validation promotion, new scientific stage, or successor task.

Actual PW main/base: `faa532409c848b24f7b8554c4c4377d0f9b92c4b`, including merged
Fasano correction #346. Main matches the reviewed identity; open PRs contain no
equivalent correction. Cameron production repair #304 merged as
`15479363ab3bcd879364628a1938879f2db8c05c`. The original independent area
interpolation was inspected at `713c3c229568bb189c548f4c8a490b69a6319bef`.
Read-only EWP main is `7c025527da7e07982428d4c78a3e79bfa29a76ac`;
`dependencies/puckworks.lock.json` still selects
`fc61c4670ec7bf801e40bb391aab16048b8da26b` (tree
`1d553e44ee2f7480a5df521560801b478618cc84`).

The old gate returns PASS with EY=EY_solid=15.39 and ceiling=24.5 after display
rounding. Its 0.5 percentage-point EY screen admits the known historical
discrepancies. Independently, its sole GS 1.9 lies in the constant-boulder-radius
interval [1.5, 2.0], where independent area interpolation is effectively exact.
Tightening that case alone cannot detect the fault.

Declare exactly these cases, in this order:

| case | GS | N | M | support |
|---|---:|---:|---:|---|
| reference | 1.9 | 40 | 24 | existing gate and scalar diagnostics |
| first changing-radius interval | 1.1 | 20 | 12 | existing inventory test |
| second changing-radius interval | 2.1 | 20 | 12 | existing inventory test |

All use m_in=0.020 kg, m_out=0.040 kg, p_bar=P_REF=5 bar overpressure and
c_s0=C_S0=118 kg/m³ of grain. Effective unchanged integration defaults are
SciPy BDF, rtol=1e-6, atol=1e-8, n_save=120; q and t_shot use their existing
model defaults. This is finite verification support, not a convergence study.
Keep the broader inventory/geometry matrix, alternate 118/PHI_S concentration,
and existing axial-refinement test unchanged.

Independent accounting: V=pi*R0²*bed_depth(m_in);
M_initial=V*(phi1+phi2)*c_s0. For each final (N,M) solid field, reconstruct
radial nodes from physical radius and field shape, use midpoint interior faces
plus center/surface boundaries, and normalize differences of cubed faces by
radius³. Average shell-weighted concentrations over uniform axial cells and
multiply by V*physical phase fraction. Then
M_liquid_retained=V*(1-PHI_S)*mean(cl_final), M_cup=m_cup[-1], and
mass_residual=M_initial-M_solid_final-M_liquid_retained-M_cup (kg).
No production reducer, SphereGrid weights, BET-derived volume, unweighted radial
mean, or EY_solid enters this residual.

Inherited absolute-only budgets: |mass_residual|<=2e-11 kg,
|EY-EY_solid|<=1e-7 percentage points, final concentrations>=-1e-8 kg/m³,
all acceptance inputs finite, and 0<EY<100*M_initial/actual dry dose.
Mass/EY/concentration tolerances come from `tests/test_cameron_inventory.py`;
the positive/inventory bound comes from the existing gate. At 20 g, the two
tolerances represent the same mass scale, but the two diagnostics must be
computed separately because EY_solid uses the production reduction.
Evaluate unrounded values, preserve rounded reference scalars, and retain every
case's diagnostics and checks even when a case fails.

Test-local fixture: temporarily restore exactly the old
`np.interp(gs, GS_GRID, BET1_GRID/BET2_GRID)` areas, preserving measured fractions,
radius and every solver input. This reinstates the historical interpolation
fault in the current solver; it does not reproduce the entire old revision.
Exercise the callable selected from the built-in component registry by stable
gate identity: corrected PASS, fault FAIL at GS 1.1/2.1 independent mass budgets
with GS 1.9 passing, restored PASS. Check typed results and strict JSON.
Keep a separate hand-calculable shell-weight oracle.

Data-guide entry followed: this gate consumes numerical states and operative
source constants, with no MANIFEST empirical target. Related IDs
`cameron2020/psd_figure2` (measured PSD, reference-only) and
`cameron2020/fig5_grind_deviation` (three-grind streamtube comparison) were
identified from catalog metadata; neither supplies this gate's acceptance data.
Inspected source constants/code, model card, independent tests, dated local audit,
and F-O3-08/R-05 of the dated review. Original empirical files/publisher figures
are not newly inspected or scored. No source-exhaustion claim follows.

Affected authoritative descriptions: gate docstring, Cameron registry notes,
matching EVIDENCE_LINKS claim/observable/caveat/claim_not_supported, model card,
and only PV-01's comparator rationale. Preserve all stable IDs, evidence/provenance
classifications and public badges. Existing browser parity/convergence remain
separate historical evidence. Conservation does not license the ~23 s diffusion
comparator's parameters or applicability to measured fractions.

Expected commands (Python 3.12 environment; details/results appended below):
focused inventory/registered-gate/reducer/serialization tests; affected registry,
evidence, public, figure and Insight tests; Ruff/mypy; the normal suite
`python -m pytest -q -m "not slow and not live and not gpu and not external_data"`.
Regenerate registry artifacts, evidence graph, public export (without --slow),
Fig. 2 evidence-vector CSV using its existing exporter logic, then Insight last.
Verify registry artifacts, Paper 3 build/availability/corpus/evidence graph,
strict reconciliation for paper3/all, and Insight.
Active Protect main ruleset 19053322 requires quick (3.10), quick (3.12),
verify-generated, paper3-scope-strict, all-scope-strict. Deliver one open,
unmerged draft PR with auto-merge disabled.


## Executed result

[Machine-readable results](cameron_gate_correction.json) retain unrounded masses,
EY diagnostics and individual Boolean checks from actual registered-callable
executions in the implementation environment. Rounded values below are for review
only; acceptance uses the unrounded values.

| interpolation | GS/grid | independent residual, kg | EY−EY_solid, pp | case |
|---|---|---:|---:|---|
| corrected | 1.9 / 40x24 | 1.0408340855860843e-17 | −5.684341886080802e-14 | PASS |
| corrected | 1.1 / 20x12 | 2.992397996059992e-17 | −1.4921397450962104e-13 | PASS |
| corrected | 2.1 / 20x12 | 3.165870343657673e-17 | −1.652011860642233e-13 | PASS |
| historical fault in current solver | 1.9 / 40x24 | 9.540979117872439e-18 | −4.973799150320701e-14 | PASS |
| historical fault in current solver | 1.1 / 20x12 | −1.3755749885956126e-5 | 0.09844259092220753 | FAIL |
| historical fault in current solver | 2.1 / 20x12 | −1.246674603371141e-5 | 0.1015507687847883 | FAIL |

Overall corrected/fault/restored outcomes are PASS/FAIL/PASS. Restored diagnostics
exactly equal the corrected diagnostics in this environment. Both off-knot fault
cases fail the independent mass check as well as the separately calculated EY
check; the defect reaches the inventory reducer without a preliminary geometry
assertion. All three fault cases satisfy the former 0.5 pp screen. The 20x12
outputs above are newly executed, not substituted September 40x24 outputs.

Tests also cover a hand-calculable two-axial-cell/three-radial-node field with
unequal shell weights (1,26,37)/64, absolute-budget boundary controls, each final
concentration check, strict EY bounds and malformed/nonfinite states. Invalid
states use the existing typed ERROR convention; normal and historical-fault
results survive evaluate_gate, to_dict and json.dumps(..., allow_nan=False).
The fixture restores interpolation through a monkeypatch context even on an
assertion failure. The 48 existing inventory/geometry/refinement tests are
byte-identical to base.

## Reproduction and generated projections

Environment: isolated `/tmp/pw-cameron-venv`, installed with
`python -m pip install -e '.[dev]'`; Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1,
pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0 on Linux x86_64. This uses the same package
versions as the prior Fasano G0 environment. No optional plotting/GPU/external-data
extras were installed. Run the following from the checkout with this environment
activated (or an equivalent supported environment):

```bash
python -m pytest -q tests/test_cameron_inventory.py tests/test_cameron_conservation_gate.py \
  tests/test_registry_artifacts.py tests/test_registry_validation.py \
  tests/test_evidence_graph.py tests/test_evidence_vocabulary_coherence.py \
  tests/test_public_claims.py tests/test_public_dependencies.py \
  tests/test_figures_paper3.py tests/insights/test_foundry.py
python -m ruff check puckworks/ tests/
python -m mypy
python -m puckworks.paper3.registry_artifacts --write
python -m puckworks.paper3.evidence_graph --write
python -m puckworks.public export --out docs/public/generated
```

For Fig. 2 only, reuse `figures_paper3.export_source_data`'s evidence-vector
projection, column order, sorted components and standard csv.writer/newline
convention (all fields are strings, so its float-rounding branch is inapplicable):

```bash
python - <<'PY_FIG2'
import csv
from puckworks.paper3.evidence_graph import evidence_vectors
with open('docs/figures/paper3/source_data/fig2_evidence_vectors.csv',
          'w', newline='', encoding='utf-8') as fh:
    writer = csv.writer(fh)
    writer.writerow(['component', 'relation', 'scope', 'gate', 'outcome'])
    writer.writerows([[n, s.relation, s.scope, s.gate, s.outcome]
                     for n, vec in sorted(evidence_vectors().items()) for s in vec])
PY_FIG2
python -m puckworks.insights write
```

Reproduce the gate receipts directly through the test support (no duplicate gate
or saved failure is used):

```bash
python - <<'PY_GATES'
import json, runpy, pytest
support = runpy.run_path('tests/test_cameron_conservation_gate.py')
with pytest.MonkeyPatch.context() as patch:
    receipts = support['registered_gate_roundtrip'](
        patch, support['historical_interpolation'].__wrapped__())
print(json.dumps(receipts, indent=2, allow_nan=False))
PY_GATES
```

Registry artifacts and generated manuscript blocks were regenerated and reviewed:
registry_export, component_gate_matrix, appendix catalog, counts, overview,
measurement dictionary and manuscript remain unchanged because their projected
fields did not change. The Paper 3 evidence graph, CSV/Markdown matrix and priority
matrix now carry the corrected four claim fields. Fig. 2 changes only the Cameron
scope string; no Fig. 4–7 calculation or rendering was run to update that string.

Public export ran without --slow. PV-01's rationale and conservation scope changed;
all numeric results, including early/peak=0.968, early TDS=24.36%, peak TDS=25.16%
and diffusion comparator=23.1 s, remain unchanged. Its comparator_context role,
verification public evidence relation, independent measured finding and OBSERVED
badge remain unchanged. Other public claims change only verification commit stamps.

Insight changes comprise the Cameron registry note/card content, affected public
provenance and their source/card/payload hashes, plus producer commit stamps and
snapshot digests. All 898 entity/relation source stamps, 90 candidate stamps and
171 tension-row stamps are producer metadata, not new scientific results. The
append-only ID registry is byte-identical to base; IDs, evidence tiers, source
classifications and all unrelated evidence records remain unchanged. Available-data
register, local-family index and data-guide producers were not needed: no changed
source dependency or consistency failure required them.

## Verification and scope preservation

Focused selection: **238 passed, 1 skipped** in 15.97 s. The skip is the optional
matplotlib-dependent `tests/test_figures_paper3.py` module; the new dependency-free
Fig. 2 CSV test runs and compares the complete current projection to
`evidence_graph.evidence_vectors()`. The initial inventory/registered-gate run
before adding additional predicate/projection controls passed 58 tests in 5.97 s.
Ruff passes; mypy passes for 19 configured files (its existing untyped-body note
is informational). These commands pass:

```bash
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
python -m puckworks.paper3.availability --verify
python -m puckworks.paper3.corpus --verify
python -m puckworks.paper3.evidence_graph --verify
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope paper3
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all
python -m puckworks.insights verify
```

`git -c core.whitespace=cr-at-eol diff --check` passes, respecting existing CSV
line endings. All production model files are byte-identical to base, except
explicitly allowed registry prose in models/__init__.py; all other gate functions
have identical ASTs. Source tables/data, initial concentration and caller basis,
kinetics, diffusivity, geometry, integration settings, defaults, physical EY,
dated audits/review and frozen records remain untouched. The merged Fasano
correction and its records are preserved. EWP was read only and no dependency
update, port, EWP test or OpenFOAM run occurred.

This closes only the Cameron conservation-gate portion of R-05/T06.
Conservation is internal numerical verification, independent in its reduction
but conditional on shared geometry/source assumptions. It supplies no empirical
accuracy, Fig. 5 normalization repair, parameter fit, density reinterpretation,
validation promotion or pressure-mechanism feasibility result. Other R-05/T06
and R-04/T08 work remain separately scoped.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.


The complete normal repository selection passed: **6,838 passed, 70 skipped,
63 deselected, 1 warning**, in 1,312.32 s (21m52s):

```bash
python -m pytest -q -m "not slow and not live and not gpu and not external_data"
```

No task-specific exclusion was inherited. The warning is the existing Visualizer
fixture development-salt warning. Optional dependency skips remain explicit; no
EWP test, external-data campaign, GPU run, live service test or unrelated slow
campaign was added. The checked implementation is identified by immutable source
hashes in the JSON receipt; subsequent revision attribution is recorded below
and the final hosted CI receipt belongs to the PR/handoff.


## Revision attribution

The precommit implementation content that passed the full normal suite is
committed as `9ed5a5436c776e67e2858c3993adef78cdecd622` (tree
`94f4ff1dfce0a5b65c4c3e3d179c7b05d9614de2`). Its executable and test SHA-256 identities
match the gate receipts. The subsequent commit adds this attribution and updates
only documentation/result metadata and generated provenance; it changes no tested
executable, numerical model, source value or acceptance requirement.

To avoid attributing the changed PV-01 payload to an unmodified base revision,
the final public export was seeded with the **base committed** `claims.json`
before running the existing producer at the implementation commit:

```bash
git restore --source=faa532409c848b24f7b8554c4c4377d0f9b92c4b --worktree docs/public/generated/claims.json
python -m puckworks.public export --out docs/public/generated
python -m puckworks.insights write
```

This is a provenance seed, not a hand-edit of generated rows. PV-01's new payload
is now attributed to the tested implementation commit, while unchanged claims
retain their existing generation identities. All public verification stamps and
Insight commit stamps identify that implementation revision; subsequent hashes
reflect those producer outputs. No self-referential commit update is required.
The final candidate head and required hosted-check receipt are recorded in the
PR description/handoff rather than in a commit claiming its own SHA.

After this provenance-only refresh, the same focused selection passes again: **238 passed, 1 skipped** in 14.76 s. All eight generated verification/reconciliation commands above pass again. Executable and test hashes remain identical to the tested implementation commit. The full normal suite is attributed to that implementation; final hosted checks are attributed to the final PR head.
