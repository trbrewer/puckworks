# Single-anchor delivery research

See MODEL_CARD.md and PROTOCOL.md. Exact frozen 001 MASS/empirical and 002
setting-aware empirical curves receive one analytical fraction-1 amplitude update.
The numerical API needs NumPy/SciPy, no external corpus. Returned predictions
include numerical allowance and analytical anchor-error amplification.

```bash
python -m puckworks.analysis.anchored_mass_delivery
python -m puckworks.analysis.anchored_mass_delivery --model docs/analysis/sci_md_mass_delivery_001/models/MASS.json
python -m pytest -q tests/test_anchored_mass_delivery.py
```

Both demos are SYNTHETIC_ANCHOR_INPUT. A fitted base plus synthetic anchor is
not a reproduced physical shot. For a supplied observation in Python:

```python
from puckworks.analysis.anchored_mass_delivery import (
    FrozenBase, anchor, synthetic_observation, IntervalQuery, AnchoredState,
)
base = FrozenBase.load("docs/analysis/sci_md_mass_delivery_001/models/MASS.json")
state = anchor(base, synthetic_observation())
future = state.predict_intervals([IntervalQuery(.004, .01), IntervalQuery(.01, .02)])
remaining = state.remaining_solute(.04)  # Prediction object: solute_kg + allowance
assert AnchoredState.from_dict(state.to_dict()) == state
```

Real AnchorInput objects require measured-mass conversion basis, mass-basis
percent TDS, source/shot identity and rights. Use NominalSetting(K, source_code)
only for the frozen setting-aware base. Queries contain only interval endpoints.
Nonfinite/reversed/negative/unsupported windows fail; zero-width average TDS is
None. Unresolved denominator, concentration bound or prediction allowance fails
explicitly. No clipping or denominator epsilon. Real serialized states are private.

Permissioned-source execution uses the existing Puckworks data configuration
or PUCKWORKS_EXTERNAL_DATA_ROOT and the reconstruction extra (openpyxl).
EVIDENCE is an owner-local private directory outside Git. The information
contract is committed before prepare. Preparation does not attach later TDS.

```bash
python -m puckworks.analysis.pannusch_anchored_mass_delivery prepare --output "$EVIDENCE/run1"
# Commit the implementation, then freeze:
python -m puckworks.analysis.pannusch_anchored_mass_delivery freeze --output "$EVIDENCE/run1"
# Only after independent exact-freeze approval, once:
python -m puckworks.analysis.pannusch_anchored_mass_delivery score --output "$EVIDENCE/run1" --review "$EVIDENCE/pre_score_review.json"
```

The scorer verifies the receipt, frozen code, source registers, artifacts and
predictions, then writes an exclusive score receipt before reading outcomes.
Existing output directories and score receipts cannot be overwritten. Preserve
failed attempts. No fitting, optimization, nonlinear search or target retuning.

Source-derived summaries and states: Pannusch et al., *Model-Based Kinetic
Espresso Brewing Control Chart for Representative Taste Components*, with related
Schmieder source measurements, [Mendeley Data v1](https://doi.org/10.17632/y2tz67f6ry.1),
[CC-BY-NC-3.0](https://creativecommons.org/licenses/by-nc/3.0/), distinct from
first-party software licensing. Raw workbooks, actual anchors, per-shot reports,
row predictions and full logs stay outside Git.

SOURCE_INTERNAL; TARGET_EXPOSED; RETROSPECTIVE_EARLY_ASSAY_CONDITIONED_COMPARISON.
PHYSICAL_VALIDATION = NOT_ESTABLISHED. NATIVE_EWP_RUNS = 0.
PRODUCTION_DEFAULTS_CHANGED = false. PRODUCTION_DEPENDENCY_LOCK_CHANGED = false.
NO_SUCCESSOR_AUTHORIZED. Paired task PRs remain open/unmerged.
