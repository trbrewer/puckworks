# Reproduction and handoff

Task SCI-H1-PANNUSCH-EQUILIBRIUM-LIMIT-001 continues review R-03/F-O3-07.
G1 / NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
[Result](RESULT.md), [protocol/derivation](PROTOCOL.md),
[input and evidence-reuse manifest](INPUT_MANIFEST.json).

## What ran

- Exact analytical equilibrium front and fraction integrals; retained liquid
  inventory and homogeneous-scale proof for both arms.
- 96 FV integrations: 24 profiles at three grids plus N1600 split propagation.
- 16 successful synthetic integrations, plus two calculations completed before
  the first report-assembly failure; 18 charged total. The wrapper correction
  changed no numerical kernel, model choice, target or input.
- One paired target score after independent pre-score approval; all 144 scalars
  in 12 physical shots, paired species and six complete original vials.
- Retained C1 paired reference errors reused without fitting or recomputing its
  predictor; historical nodal predictions reused without rerunning that solver.
- Baseline plus all 16 predeclared deletion reductions, rebalanced without fits.

No OpenFOAM, new fit, assay-conditioned state, source campaign expansion,
protected-target scoring/access, acquisition, author message, new governing
closure, production adoption, automatic merge or successor. No evidence component
needed for the comparison was unavailable. The input/measurement uncertainties
listed in RESULT remain unquantified; physical validation is not established.

## Reproduction

Use an isolated checkout of the exact candidate and Python >=3.10 with the
project dev requirements. Tested interpreter/dependency identities and local
checks are recorded in QA.json. Do not put raw workbooks, detailed profiles,
private paths or complete logs in Git.

`EWP_REFERENCE` must identify the read-only EWP checkout at
7c025527da7e07982428d4c78a3e79bfa29a76ac. `C1_REFERENCE` must identify the
retained C1 `predictions/paired_shot_analyte_errors.csv`, SHA256
26289d2862500a5a0cb0fbb53b5e706fc94e7775624e1cc12c8012d97c072b8e.
`EVIDENCE_DIR` is a fresh external working directory. Resolve source originals
through `PUCKWORKS_EXTERNAL_DATA_ROOT` or the existing
`~/.config/puckworks/data_sources.json` entry
`PANNUSCH2024_MENDELEY_FULL_REPOSITORY`. An unavailable mount is known evidence
unavailable here, not nonexistent data. The loader fails closed on changed bytes.

```bash
python -m pip install -e '.[dev,reconstruct]'
python -m pytest -q tests/test_pannusch_equilibrium_limit.py
python tools/pannusch_equilibrium_limit.py prepare \
  --private "$EVIDENCE_DIR" --ewp "$EWP_REFERENCE" --reference "$C1_REFERENCE"
python tools/pannusch_equilibrium_limit.py verify --private "$EVIDENCE_DIR"
python tools/pannusch_equilibrium_limit.py predict --private "$EVIDENCE_DIR"
python tools/pannusch_equilibrium_limit.py score \
  --private "$EVIDENCE_DIR" --ewp "$EWP_REFERENCE" --reference "$C1_REFERENCE" \
  --audit docs/analysis/sci_h1_pannusch_equilibrium_limit_001/PRE_SCORE_AUDIT.json
```

`freeze` is a preparation/audit command, not part of result reproduction: use the
committed approved freeze. Reproduction creates fresh numerical records under
the corrected freeze; the first execution's records retain INITIAL_FREEZE's
identity. Numerical arrays are expected to agree at the declared allowances;
execution/provenance hashes need not match across library versions or original
versus corrected wrapper identities. Existing same-freeze per-profile cache
files permit interrupted prediction runs to resume without duplicating completed
profiles. Do not reuse a cache from another freeze. No score can change solver
inputs: score verifies frozen input equality and retained evidence identities.

## Artifact semantics

`LOSSES.csv` includes ALL and each condition, BOTH and each analyte. `finite`
and `equilibrium` are means of six-share per-profile RMSEs. Positive
`gain_finite` favors finite rate. `gain_allowance` is the sum of arm loss
allowances under the same balancing. Reference errors are fixed retained
artifacts; their empirical/measurement uncertainty is not modeled. The finite
versus reference allowance is `finite_allowance`; the equilibrium versus
reference allowance is `equilibrium_allowance`.

`finite_historical_max_share_delta` in LOSSES/DELETIONS/RESULTS is the balanced
**mean of per-profile maximum share differences**, not the global maximum.
The global maximum is 0.0007938934734253, separately reported in RESULT.
`DELETIONS.csv` has 17 reductions × three analyte summaries; these are one
finite sensitivity family, not independent population replicates.
`RESIDUALS.csv` retains all six positions and source IDs. `FAST_TRANSFER.csv`
separates rate-to-grid-limit and grid-to-continuum-front discrepancies.

Private artifacts preserve exact primary membership, source fraction IDs, vial
quantities, times and gaps, all per-profile predictions/allowances, and all
144 detailed observed/predicted fraction rows. Their identities are bound by
FREEZE, NUMERICS and RESULTS. Only reviewed aggregate source-derived evidence
is committed. The raw-source manifest and source-rights notices remain intact;
source-derived values retain CC-BY-NC-3.0 with Pannusch/Mendeley attribution.

## Review, software QA and repository disposition

[PRE_SCORE_AUDIT.json](PRE_SCORE_AUDIT.json) records independent nonhuman approval
of corrected freeze d8e946d416698462794d8e929f67b998026cd433ce30fb843b00954ed9bc9be4.
The reviewer independently verified all five original hashes, the 24 input
profiles, retained reference identities, and the unchanged numerical kernel
used by the original prediction freeze. After scoring, the reviewer independently
reduced all deletion and fraction diagnostics and checked allowance propagation;
no additional full numerical integrations were executed for review.

Final review and check outcomes are in QA.json and the final draft PR receipt.
No source law, parameter file, solver default, archived review or historical
bundle changed. EWP is read-only. Starting Puckworks main remains
6f7e95fc5fe8aa7bc6fa0984e77d558cd3af7dbf; EWP main remains the identity above.
The final commit/tree and draft-PR URL are reported outside this commit to avoid
self-reference. Stop at the unmerged draft PR with auto-merge disabled.
