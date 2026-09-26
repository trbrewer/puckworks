# Recipe-conditioned delivery research

Explicit MT/MF/MTF, frozen M0 and SETTING_AWARE_EMPIRICAL model selection;
constant nominal settings, kg interval solute and average TDS percent. No
hydraulics or physical-mechanism prediction. See MODEL_CARD.md and PROTOCOL.md.

From this producer checkout with NumPy/SciPy available, offline synthetic
nonzero-slope example (three different temperature recipes):

```bash
python -m puckworks.analysis.conditioned_mass_delivery
python -m puckworks.analysis.conditioned_mass_delivery \
  --model docs/analysis/sci_md_mass_delivery_002/models/MTF.json \
  --temperature-K 363.15 --source-flow-setting-code 1.7 --stop-kg 0.04
PYTHONPATH=. python -m pytest -q tests/test_conditioned_mass_delivery.py
```

The loaded fitted model reports its actual coefficients, including small slopes;
the example does not substitute synthetic slopes into a fitted artifact. Every
family uses the same declared mass/design domain. A stop integral is conditional
on attaining that measured beverage mass, and modeled gaps are not measured cup
totals. Unsupported requests fail explicitly, or return reasons with strict=False.

Permissioned-data reproduction uses the existing Puckworks data-source config
or PUCKWORKS_EXTERNAL_DATA_ROOT; install the reconstruction extra for openpyxl.
EVIDENCE must be an owner-local directory outside Git. Reproductions are a new
execution, never a new independent validation claim. Preserve the task-wide
nonlinear ledger across failed/corrected attempts; do not reset its count.

```bash
python -m puckworks.analysis.pannusch_conditioned_mass_delivery prepare \
  --output "$EVIDENCE/run1" --budget-ledger "$EVIDENCE/nonlinear-budget.jsonl"
# Commit implementation and compact artifacts, then:
python -m puckworks.analysis.pannusch_conditioned_mass_delivery freeze \
  --output "$EVIDENCE/run1"
# Only after independent exact-freeze pre-score approval:
python -m puckworks.analysis.pannusch_conditioned_mass_delivery score \
  --output "$EVIDENCE/run1" --review "$EVIDENCE/pre_score_review.json"
```

The scorer verifies code, source registers, fitted artifacts, predictions and
review identities, writes a single-use receipt before chemistry access, and
checks M0 replay before issuing a disposition. Failed attempts stay retained.
No automatic candidate selection by target performance. MT/MF are diagnostics.
No variable-setting prediction, ramp rescue, target calibration or TIME search.

**SOURCE.json, models, training diagnostics and result tables are source-derived
CC-BY-NC-3.0 material, distinct from first-party code licensing.** Attribution:
Pannusch et al., data for *Model-Based Kinetic Espresso Brewing Control Chart for
Representative Taste Components*, with related Schmieder source measurements,
[Mendeley Data v1, DOI 10.17632/y2tz67f6ry.1](https://doi.org/10.17632/y2tz67f6ry.1),
[CC-BY-NC-3.0](https://creativecommons.org/licenses/by-nc/3.0/). These are newly
transformed/fitted artifacts, not original source coefficients. Raw workbooks,
MAT files, measurement/prediction rows and full traces/logs remain external.

SOURCE_INTERNAL; TARGET_EXPOSED; RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON.
PHYSICAL_VALIDATION = NOT_ESTABLISHED. NATIVE_EWP_RUNS = 0.
PRODUCTION_DEFAULTS_CHANGED = false. PRODUCTION_DEPENDENCY_LOCK_CHANGED = false.
NO_SUCCESSOR_AUTHORIZED. Both task PRs remain open/unmerged for owner disposition.
