# Tested commands

Run from the repository root in the recorded environment, with PYTHONPATH=. and one BLAS/OpenMP thread. Detailed logs remain private; QA.json contains identities and outcomes. Stage execution and private path resolution are in [REPRODUCE.md](REPRODUCE.md).

```bash
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python -m ruff check puckworks/ tests/
python -m mypy
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
python -m puckworks.statusdoc --verify
python -m pytest -q -m scientific_baseline
python tools/build_espresso_data_guide.py --check
python tools/readme_governance.py verify
python -m mypy puckworks/analysis/early_assay_5cqa_delivery.py puckworks/analysis/early_assay_5cqa_training.py puckworks/analysis/pannusch_early_assay_5cqa_delivery.py
python tools/update_readme_pulse.py --verify
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope paper3
python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all
python -m puckworks.paper3.archive create-archive --out "$TASK_EVIDENCE_ROOT/qa/archive-a.tar.gz"
python -m puckworks.paper3.archive create-archive --out "$TASK_EVIDENCE_ROOT/qa/archive-b.tar.gz"
cmp "$TASK_EVIDENCE_ROOT/qa/archive-a.tar.gz" "$TASK_EVIDENCE_ROOT/qa/archive-b.tar.gz"
python -m puckworks.paper3.archive verify-archive "$TASK_EVIDENCE_ROOT/qa/archive-a.tar.gz"
git diff --check
```

Focused pre-fit run (154 passed):

```bash
python -m pytest -q tests/test_early_assay_5cqa_delivery.py tests/test_early_assay_5cqa_training.py tests/test_pannusch_early_assay_5cqa_delivery.py tests/test_assay_conditioned_5cqa_delivery.py tests/test_assay_conditioned_5cqa_training.py tests/test_pannusch_assay_conditioned_5cqa_delivery.py tests/test_conditional_5cqa_delivery.py tests/test_conditional_5cqa_training.py tests/test_pannusch_conditional_5cqa_delivery.py tests/test_conditional_tail_delivery.py
```

New Python AST and JSON parsing, documented-shell syntax, local Markdown links, private-path/credential pattern scanning, retained-public byte comparisons, and preservation of every base file except the three normal planning records passed. EWP stayed unchanged. No native OpenFOAM execution or protected scoring was part of QA.
