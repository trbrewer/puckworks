# Qualification and reproducible checks

G1 / NO_GOVERNING_PHYSICS_CHANGE. Numerical and software qualification do not establish physical validation. Native EWP runs: zero. Models and frozen science bytes remain unchanged after the sole score.

Puckworks: 84 focused new/006 tests passed; the preimplementation quick baseline passed 4,188 tests (32 skipped, 766 deselected); the existing historical scientific baseline passed 5. Registry verification passed 65 checks with one preexisting acknowledged exception. Ruff on added modules/tests, README governance, status-document verification and the existing data-guide generator check passed.

EWP: all 5 new consumer tests passed with the exact evaluated producer, including real producer parity and synthetic hash/schema/namespace adversaries. Static validation passed 39/39 gates. Source, historical baseline, governing/change contract, release and applicable retained boundary verifiers passed. All JSON, shell and secret/path/production-boundary checks are recorded separately at closeout.

The initial EWP full suite ran 1,609 tests with 2 failures, 2 errors and 15 skips. Its original log is retained, not relabeled PASS: historical tests lacked explicit authority paths; the consumer lacked its executable Git mode; package-manifest aggregate fields were stale. After correcting those environment/bookkeeping issues, all 47 affected tests passed. There are 1,635 discovered tests; discovery is not execution. No solver run or historical scientific fitting/scoring was performed.

The independent review reproduced all retained objectives, development selections, 384 slots/380 qualified predictions, 96 states and exact EWP parity. Its receipt documents the nonblocking held-development allowance-summary omission. The result-integrity addendum audits retained outcomes and arithmetic without another score. Hosted CI is reported live in the linked draft PRs and owner report; a pending check is not PASS and earlier-head success does not certify a later head.

Use the repository's existing scientific Python environments and configured external resolver. EXECUTION.json is the immutable pre-score execution snapshot; SCORE_COMPLETION.json records the one completed final score. Exact numerical-library versions and fitting counts remain in EXECUTION.json. Public synthetic commands:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q tests/test_conditional_caffeine_delivery.py \
  tests/test_conditional_caffeine_training.py tests/test_pannusch_conditional_caffeine_delivery.py \
  tests/test_conditional_tail_delivery.py tests/test_conditional_tail_training.py \
  tests/test_pannusch_conditional_tail_delivery.py
python -m pytest -q -m scientific_baseline
python -m puckworks.statusdoc --verify
python tools/build_espresso_data_guide.py --check
python tools/readme_governance.py verify
```

In EWP, set SCI_MD_CAFFEINE_DELIVERY_001_PRODUCER to a clean checkout of evaluated producer 3389f8f4d41cfcbb965e38e9ceaed0840f9a41ea, as recorded in HANDOFF.json. Historical authority variables are distinct from this new research producer and must continue to identify their existing pinned authority:

```bash
python -m unittest -v tests.test_research_conditional_caffeine_delivery
python scripts/verify_source_manifest.py --root .
python scripts/static_validate.py --root .
python scripts/verify_v0_1_4_baseline_integrity.py --root .
python scripts/verify_governing_physics_change.py --root .
python scripts/verify_change_contract.py --root .
```

The fitting/freeze/score command transcript is in README.md and private retained logs. Those are historical execution commands, not authorization for a second real score. To read the completed score without fitting, predicting or joining outcomes:

```bash
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery report --out "$PRIVATE_RUN"
```

Detailed source rows, optimizer/fold logs, joined outcomes and review scripts remain outside Git in the configured caffeine-delivery-001-evidence collection. Model-content hashes, model-file hashes, evaluated and publication commits are separate identities; HANDOFF.json and RESULT_BINDING.json retain the evaluated scientific identities.

PHYSICAL_VALIDATION=NOT_ESTABLISHED. Source-derived CC-BY-NC-3.0 treatment remains separate from software licensing. No merge, production adoption, new acquisition, laboratory work or successor is authorized.
