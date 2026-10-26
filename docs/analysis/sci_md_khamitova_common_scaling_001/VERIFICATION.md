# Verification and handoff

Actual Puckworks current-main base:
`43a0d0cc70a556de6892772b735952675a04666d`.
Branch: `science/sci-md-khamitova-common-scaling-001`, isolated clean worktree.
No pre-existing user work reset. The final submitted/tested commit and live
hosted outcomes are recorded in the draft PR and final handoff, outside the
deterministic scientific files. No merge or auto-merge; no successor.

EWP was read-only. Remote main was confirmed as
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516` with `git ls-remote`; the GitHub
connector independently read its lock at main, retaining Puckworks pin
`fc61c4670ec7bf801e40bb391aab16048b8da26b`. The existing local EWP checkout
remains at its own historical HEAD `78cbd59c751393cddfe539e4c69e43a224329bca`;
it was not moved to remote main. No EWP file, lock, local ref or remote content
was written. Production solvers/defaults, Matias, I-024 and predecessor bundles
are unchanged.

## Scientific reproduction

Use the existing analysis/dev environment (no dependency changes). In this run,
`python` denotes `/home/tim/ci-work/quality-budget-20261007-venv/bin/python`,
Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2.

```bash
python -m puckworks.analysis.khamitova2020_common_scaling \
  --output /tmp/khamitova-common-scaling --plot
python -m puckworks.analysis.khamitova2020_common_scaling_check \
  --results /tmp/khamitova-common-scaling/results.json \
  --output /tmp/khamitova-common-scaling-check.json --lp
python -m pytest -q tests/test_khamitova_common_scaling.py \
  tests/test_khamitova_tamping_chemistry.py
```

- All 135 matrices supported: 27 primary and 108 symmetric omission diagnostics.
  Exact checker: 1728 intervals / 3456 one-sided inequalities, positive factors,
  normalized gauge, all predictions, all expected constraints/matrices/ratios,
  oriented cycle/root identities, certified M and reciprocal brackets, strongest
  four-cell bounds and exact gap relations verified. No unsupported source cells.
- Independent log LP: all 135 agree within the sole numerical-agreement tolerance
  of 1e-9 dex; observed maximum absolute difference 1.7433970933566911e-16 dex.
  [Combined exact/LP receipt](independent_check.json). No LP tolerance determines
  an exact compatibility verdict. Epsilon/gap displays are independently checked
  by deterministic Decimal formatting, without floating agreement tolerances.
- Focused suite with predecessor tests: **94 passed in 8.13 s** before the bounded
  review/display changes. After the display-check correction, **57 new-task tests
  passed in 7.38 s**; after adding readable decimal CSV factor/prediction columns,
  the final focused run passed **57/57 in 8.02 s**. Accepted predecessor code/data
  and exact result bytes are unchanged by these display changes.
- Fixtures cover exact rank one, gauge and analyte-unit invariance, oriented
  four-cell obstruction, the six-cycle obstruction invisible to all four-cycles,
  both required cycle counts, malformed/nonpositive values and support by layer,
  missing/duplicate source keys, incomplete matrices, source qualifications,
  tampered bounds/cycles/costs/factors/predictions/brackets/coverage, independent
  M=1 floors, all-source LPs and fixture LPs. Separate-constructor independence
  is also tested. The approximately 3-second double-CLI reproducibility test is
  marked `slow` under the existing convention and explicitly included above.
- Two independent temporary CLI output directories produce byte-identical exact
  JSON and all four CSVs, also equal to the committed scientific artifacts.
  Timestamps, output paths and run/CI metadata do not enter those files.
- Matplotlib 3.11.2 figure was rendered and visually inspected: labels, all nine
  strata, all 16 residuals, legend and representation-error limits are legible.
  [VIZ_SPEC](VIZ_SPEC.json) records mappings and ceilings; PNG cross-version byte
  identity is not asserted.
- [Independent review](REVIEW.md): one concrete display-check contract finding
  corrected, no unresolved material findings. Separate combinations/permutations
  cycle enumeration reproduced all 135 optima and all 1728 interval checks.

The initial focused run had **2 failures / 91 passes**: an incorrect hand-written
four-cell test witness (corrected g=(1,1/2), a=(2√2,√2)) and an overly strict
positive lower-endpoint test for a reciprocal bracket smaller than 1e-12. Zero
is a valid certified lower display endpoint for that positive root; the bracket
checker was corrected to allow it. The next focused run passed 93/93; the
constructor-independence test subsequently brought that to 94. These attempts
are not relabelled as passes. None changed the source optima.

## Preservation and affected projections

[input_sha256.json](input_sha256.json) records all 23 unchanged input/predecessor
identities, checked before analysis and again by the independent verifier. The
18-entry predecessor manifest and its own reviewed SHA256 remain untouched;
all four source CSV byte identities and their original line endings are preserved.
Accepted observations.csv is the full-value/qualification regression reference;
no duplicate raw dataset, source PDF or source artwork was created. The accepted
PDF identity is carried from source_metadata.json, not newly authenticated.

Only the existing Khamitova MANIFEST analytical-use field and available-register
authority block were extended; the predecessor link remains explicit. Source
rights, dataset/campaign/replicate counts and data-only/card status are unchanged.
Existing producers, in dependency order:

```bash
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.insights write
python -m puckworks.insights verify
python -m pytest -q tests/test_available_data_register.py \
  tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py \
  tests/insights/test_foundry.py
```

Insight verify: **OK**. Affected discovery suite: **74 passed in 3.16 s**.
The larger generated Insight diff updates source-commit provenance from the
previous producer stamp to the actual base. After removing only those commit
stamps for comparison, the corpus map changes two entities (Khamitova card and
dataset) and their two input hashes. Corpus counts, candidate IDs and evidence
labels remain unchanged. No census, new component or validation edge is added.
Hand-curated guide header and ordinary ROADMAP §7.1/SPRINTS pointers are updated;
generated authority is regenerated, not hand-edited.

## Repository checks and submission

```bash
python -m ruff check puckworks/ tests/ tools/build_available_data_register.py
python -m mypy
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python -m pytest -v -m 'not slow and not live and not gpu and not external_data' --durations=15
```

Ruff: **all checks passed**. Configured mypy: **no issues in 19 source files**.
Registry gates: **66 PASS / one pre-existing ACKNOWLEDGED_EXCEPTION**.
The single full local quick-lane run passed: **7377 passed, 36 skipped,
74 deselected**, 10 warnings, in **1544.15 s (25m 44s)**. It used the unchanged
repository selector above. The bounded display-only corrections made while
this run was active were separately reverified by the final 57-test focused
run; exact results.json and the LP/exact receipt stayed byte-identical. No
repeated full-suite campaign was performed.

Additional existing generated registry/build/availability/corpus, status-truth,
evidence-graph reconciliation/verification and all three manuscript claim-coverage
checks passed. The active GitHub ruleset requires quick (3.10), quick (3.12),
verify-generated, paper3-scope-strict and all-scope-strict, with strict latest-base
checking; no CI rules or budgets were changed.

Hosted checks have not run at this pre-submission packet-creation point; their
actual final-head outcomes will be reported on the draft PR and final handoff. No unrun, pending or cancelled check is counted
as passing. The draft remains open/unmerged regardless of CI disposition.

Mathematical exactness is restricted to the specified observation-representation
problem. Mean/RSD aggregation, cross-analyte covariance, shot joins and grind
chronology remain unresolved; no causal/kinetic inference or practical tolerance.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.
