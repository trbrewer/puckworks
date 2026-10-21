# Verification and delivery identity

This record concerns software QA and delivery, separate from the scientific
finding and the [independent scientific review](REVIEW.md).
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Base and scientific candidate

The actual implementation base is
`58075bbbce548e63d94106c96b918c1464221514`. A fresh `git fetch origin main`
after local verification confirmed that current main still has that identity;
there is no delta from the owner's reviewed Puckworks revision. Work used the
isolated `research/sci-md-melrose-transient-hydraulics-001` branch. EWP was read
at `aace2cc6b6c2a393d2dbfb0274104192ca6c7203` and was not modified.

Commit `f63f3a6d307ffcad76bdac5e5ceb992a91b4dc83` binds the reviewed scientific
candidate and repository integration. The scientific identity is the 20-file
[SHA256 manifest](SCIENTIFIC_CANDIDATE.json), whose own SHA256 is
`2dbf237b78b4f9e747bf5eb52e8ba78ece1fa47e9d4c6903c196f566a0650a84`.
All 20 files were rehashed with exact agreement before that commit. The plan
was written at 14:14:13 UTC on 2026-10-21 after source inspection and before
coordinate transcription; the scientific manifest was frozen at
14:30:38.674764 UTC. This chronology is retrospective and target-exposed.

The reviewer completed scientific assessment at 14:31:29 UTC and inspected the
dependent count-only administrative delta at 14:33:18 UTC. REVIEW.md SHA256 is
`7299cc2d13356cbc47f68516ec2c98bb7c7dd49e97ec59f5884f08cdc5afbeaf`.
The subsequent commit adding this verification record changes no scientific
file. Its final head and hosted check links are recorded in the draft PR and
delivery handoff, avoiding a self-referential commit hash in its own content.

## Local execution on 2026-10-21

Commands ran in the isolated worktree with Python 3.12.3, using an external
virtual environment with the repository's existing development dependencies.
No dependency lock or CI source-download requirement changed. Full command logs
remain in the external task evidence directory; the commands and outcomes below
are sufficient to reproduce the checks.

| Actual command | Outcome |
|---|---|
| `pytest -q -m 'not slow and not live and not gpu and not external_data'` | 6,838 passed, 70 skipped, 63 deselected; 1 existing DEV-salt warning; 1,311.43 seconds. Collection began on the implementation base before the new tests existed, while task edits proceeded. This is ordinary local regression evidence, not a final-head full-suite claim. |
| `python -m pytest -q tests/test_melrose2019bed_transient.py` | 22 passed in 0.53 seconds, including independent LP checks and deterministic output reproduction. |
| `python -m pytest -q tests/test_melrose2019bed_transient.py tests/test_available_data_register.py tests/test_espresso_data_guide.py tests/test_local_corpus_family_index.py` | 31 passed in 0.71 seconds. |
| `python -c 'from puckworks.registry import run_all_gates, components; print(len(components()), "components"); run_all_gates()'` | 28 components; PASS=66, ACKNOWLEDGED_EXCEPTION=1; no failures. Existing exception unchanged. |
| `ruff check puckworks/ tests/` | Passed. |
| `python -m puckworks.paper3.evidence_graph --reconcile --strict --scope paper3` | Passed. |
| `python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all` | Passed. |
| `python -m puckworks.insights verify` | OK, including after the scientific commit. |
| `python tools/validate_local_corpus_coverage.py` | Valid: 39 mapped/registered families, zero unregistered. No new corpus census. |
| `git diff --check` | Passed. |

The first focused integration invocation used the console `pytest` entry point
and encountered two collection errors, `ModuleNotFoundError: tools`, because
the worktree root was absent from that entry point's import path. Running the
listed `python -m pytest` command resolved the environment issue; no production
or test code was altered for it.

All 11 run steps of `.github/workflows/generated-artifacts.yml`'s
`verify-generated` job were executed locally:

```bash
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
python -m puckworks.paper3.availability --verify
python -m puckworks.paper3.corpus --verify
python -m puckworks.paper_a.claim_coverage
python -m puckworks.paper_b2.claim_coverage
python -m puckworks.paper3.claim_coverage
python -m puckworks.analysis.lateral_coupling_discrimination --verify
python -m puckworks.paper3.evidence_graph --reconcile
python -m puckworks.paper3.evidence_graph --verify
python -m puckworks.paper3.archive create-archive --out /tmp/pa.tar.gz
python -m puckworks.paper3.archive create-archive --out /tmp/pb.tar.gz
cmp /tmp/pa.tar.gz /tmp/pb.tar.gz
python -m puckworks.paper3.archive verify-archive /tmp/pa.tar.gz
```

Ten steps initially passed. Paper 3 prose claim coverage initially failed on
four stale manifest-count references (118). Adding the recovered dataset makes
119 records; the existing generated table was regenerated and those four
dependent numeric references were corrected. The affected command then passed
with zero unaccounted claims. The manuscript's scientific argument was not
revised. The source-family alias keeps the shared Corrochano/Melrose campaign
count at 46. No unrelated registry or corpus framework was introduced.

The reviewer independently reproduced all four CSV/JSON outputs byte-for-byte,
checked every load-bearing image witness, and solved 42 separately formulated
linear programs. Maximum discrepancy from the producer's expansion minima was
2.220446049250313e-16 mL/s. See REVIEW.md for scope and timing; these checks do
not establish physical validity.

## Reproduction and required hosted checks

From an installed checkout:

```bash
python -m puckworks.analysis.melrose2019bed_transient
python -m pytest -q tests/test_melrose2019bed_transient.py
```

The producer uses committed coordinates/contracts only. To write the four
outputs elsewhere, add `--output /tmp/melrose-reproduction`; compare
`observations.csv` with the dataset copy and the other three outputs with this
analysis directory. Source PDFs, extracted images and inspection crops remain
external to Git and are unnecessary for offline software tests.

The active Protect main ruleset was re-read using
`gh api repos/trbrewer/puckworks/rulesets/19053322`. It requires strict,
up-to-date status checks: `quick (3.10)`, `quick (3.12)`, `verify-generated`,
`paper3-scope-strict`, and `all-scope-strict`. A legacy branch-protection response
was not used to override that ruleset. Hosted statuses are not inferred from
the local checks above: the draft PR's check records and final delivery report
bind the actual outcomes to the final pushed head. The authorized delivery is
one open draft PR, unmerged, with auto-merge disabled.
