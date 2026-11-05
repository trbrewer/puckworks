# Reproduction and evidence

Scope: offline metadata qualification only; no hydraulic outcomes, fits,
segmentation, API query, new acquisition or user TDS/EY/sensory analysis.
`FILES_INSPECTED`, not catalog-only: authenticated source bytes, canonical and
aligned Bronze metadata, accompanying local sidecars and the referenced records.
Raw/normalized shots, identifiers, user hashes and private audit logs stay outside
Git. Reproduction requires the permissioned retained collection and its inventory;
the public bundle does not redistribute them.

## Identity and ordering

- Puckworks fetched main/base: `4c5ebab5df79929813949df7113c21290dde40cc`.
- Pre-census plan commit: `748bd94` (no outcomes exist before or after it).
- Logical snapshot: `VISUALIZER_COFFEE_API_CRAWL_2026_07_15`, schema 6,
  Bronze schema 1; 23,169 canonical records and stored versions; zero revisions,
  timestamp conflicts or missing update timestamps.
- X1-compatible aggregate SHA-256 (465 Bronze/normalized/index files):
  `6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`.
- Owner inventory content identity:
  `f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
- Index SHA-256:
  `2c570cc441dac5256736214b109649688a6153550b1194baf1c7c2836b9cd751`.
- All 11 registered non-array metadata files (excluding the secret harvest salt)
  rehash identically. A bounded file-name comparison under the registered
  Visualizer collection finds no additions. Cursor/list-page sidecars carry
  pagination/update state, not added machine or sensor authority. Older stores
  and normalized copies are not extra evidence or shots.

The EWP [private-work record](https://github.com/trbrewer/espresso-whole-pull/blob/67bead2a25bd7e61c16c4fe2c104d885d8d26dd9/docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md)
and [C1 result](https://github.com/trbrewer/espresso-whole-pull/blob/67bead2a25bd7e61c16c4fe2c104d885d8d26dd9/docs/analysis/espresso_corpus_leverage_002/RESULT.md)
were read without modifying EWP. Their local checkout bytes match that EWP main
pin. The private-work record's source/full-store digests use different scopes
from X1's sorted file-map aggregate; they are not substituted for it.

Relevant authority: [X1](../PRESSURE_PEAK_X1/SUMMARY.md),
[native reconciliation](../../../puckworks/data/visualizer/reconciliation/ewp_rwb_001/RESULT.md),
[disclosure rules](../../../puckworks/data/visualizer/reconciliation/ewp_rwb_001/PRIVACY_AND_DISCLOSURE.json),
[source card](../../cards/visualizer_coffee.md),
[data-use guidance](../../visualizerCoffee_DATA_USE.md) and
[publication guidance §6.6](../../PAPER_3_PUCKWORKS_DRAFT.md).
The card's §5.9 reference is to ROADMAP's pressure-node convention.
Historical generic scale-channel descriptions do not satisfy this task's stronger
native-lineage requirement. No deployed parser revision or sensor identity is
inferred from the version-matched public source candidate.

## Commands

From this checkout, with the existing development environment, set `VIS_STORE`
to the retained `visualizer/crawl_v6_20260715` directory, `VIS_INVENTORY` to the
owner inventory, and `VIS_PRIVATE` to a new directory outside Git. These are
owner-local locators, deliberately not published. No salt or network is needed.
The execution environment used Python 3.12.3 on Linux. Independent read-only
review and its one corrected reproduction defect are recorded in [REVIEW.md](REVIEW.md).

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH="$PWD"
mkdir -p "$VIS_PRIVATE"
/usr/bin/time -f 'user_seconds=%U\nsystem_seconds=%S\nelapsed_seconds=%e\nexit_status=%x' \
  -o "$VIS_PRIVATE/audit.time" \
  python -m puckworks.analysis.vis_turnover_001 \
  --root "$VIS_STORE" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE"
diff -u docs/research/VIS_TURNOVER_001/QUALIFICATION.csv "$VIS_PRIVATE/QUALIFICATION.csv"
python -m pytest -q tests/test_vis_turnover_001.py tests/test_visualizer_store.py \
  tests/test_visualizer_contract_shapes.py tests/test_visualizer_harvest.py \
  tests/test_data_privacy.py tests/test_pressure_peak_x1.py
ruff check puckworks/ tests/
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python tools/readme_governance.py verify
```

The metadata check uses X1's authentication and `CorpusSnapshot.latest()`; Bronze
joins must be unique and exhaust the same `(id, updated_at)` set. It reuses the
explicit parser mapping, without structural recovery, normalization or sorting
of traces. It only counts nonempty containers/scalars at the CSV's exact paths:
an array of nulls still counts as present. No numeric sample validity, estimator
support, lineage or pressure-control meaning follows. All source-outcome fields
are ignored. Exact-path absence is not a claim that every conceivable source
schema field was searched; unchanged hashes and retained provenance supply the
broader no-new-authority conclusion.

`SUPPRESSED` covers unsafe nonzero or complementary cells. The existing minima
are 20 shots and 10 distinct linked users; the complement check conservatively
requires 10 users not in the present-cell user set. Corpus-wide zero/complete
coverage does not identify a rare subgroup. No user counts or matching-context
values are released here; there are no cross-field intersections or selected
groups. The same 1,004/22,165 format totals were already disclosed by C1.

## Checks and computational accounting

Focused tests cover explicit-format versus hardware distinction, generic channel
names versus lineage, absent/null/zero/-1 goal ambiguity, canonical/Bronze joins,
no user-outcome access, and cell/complement disclosure. Pressure-priority,
flow-limited and flow-priority stage classifiers, time-weighted shot reduction
and a pre-outcome execution gate are **not applicable**: Step 0 stopped and no
outcome evaluator exists to run. No unqualified substitute classifier is added.
Local checks: 92 focused tests passed (one existing development-salt warning),
Ruff passed, registry gates passed (66 PASS and one existing acknowledged
exception), and README governance passed. Required hosted CI is recorded on
the PR at its final head.

Actual single-thread CPU accounting (user + system; retained private time logs):

| Attempt | CPU seconds | Outcome |
|---|---:|---|
| Initial X1 authentication | 1.14 | matched |
| Metadata audit 1 | 1.05 | failed: literal parser token was incorrectly `Beanconqueror` |
| Metadata audit 2 | 25.21 | completed after using native `Parsers::Beanconqueror` |
| Accompanying metadata check | 0.44 | 11 matches; no additions |
| Final combined audit/export | 25.46 | completed; same coverage; inherited mapping reused |
| LF-only CSV re-export from saved counts | 0.36 | removed CRLF whitespace warnings; counts unchanged |
| **Total** | **53.66** | **0.014906 core-hours** |

The failed traceback/timer and successful attempts are retained outside Git.
The fix changes token bookkeeping, not qualification or any scientific rule.
Core-hours exclude interactive file reading, tests, CI and independent review;
no optimizer or simulation ran. Times are measured at 0.01-s precision.

## Code and input hashes (SHA-256)

| Artifact | SHA-256 |
|---|---|
| PLAN.md | `cf6987b78762d1fefc74ab15e79f00e3add45e2c94b04cc582efa87907c71f1d` |
| `puckworks/analysis/vis_turnover_001.py` | `5f25c7c64040a4ee811c1292755867241794b7766b96002c813853e709f633a3` |
| `puckworks/analysis/pressure_peak_x1.py` | `5a6ba598b90d6277458969414b590617e209da7a76266b5a3d373f7e05288708` |
| `puckworks/data/visualizer/integration_contract.py` | `2eeebda9fbac62d3c0e1a4b82dddd996ac798796527b8d831bf76cf6c1cd4c64` |
| EWP private-work record | `04776d834668eefcc3b2e6fca7ed582ab8e8a8803791b44b57c8bef7b1a23f27` |
| EWP C1 RESULT.md | `26bc5ac53071f905545880f2bcefd3fedf6d07eb52fd8c67d97f6fa1e24faeec` |
| EWP C1 summary.json | `16c65084f5f5459274c5fc1a6e753d6c7f9aef30fdbf44b11a78588fb4e38213` |

Data source: Visualizer; thanks to the contributing users who made their shots
public. Permission is owner-attested; raw redistribution is not permitted.
