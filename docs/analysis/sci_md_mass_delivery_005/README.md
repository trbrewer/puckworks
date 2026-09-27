# Two-assay amplitude-and-decay prediction

G1 / NO_GOVERNING_PHYSICS_CHANGE. Primary TWO_ASSAY_MASS; research only.
[Model card](MODEL_CARD.md), [protocol](PROTOCOL.md), [source preflight](DATA_AVAILABILITY_PREFLIGHT.json)
and [fixed support](SUPPORT.json) define the task before conditioning access.
Puckworks [#285](https://github.com/trbrewer/puckworks/issues/285); EWP
[#191](https://github.com/trbrewer/espresso-whole-pull/issues/191).

Offline synthetic API example (no private data):

```bash
python -m puckworks.analysis.two_assay_mass_delivery --stop-kg 0.04
python -m pytest -q tests/test_two_assay_mass_delivery.py tests/test_pannusch_two_assay_mass_delivery.py
```

Source-qualified commands, from this exact producer checkout with NumPy/SciPy
and the reconstruction extra installed. PRIVATE_RUN must name a NEW directory
outside Git. Existing Puckworks configuration or PUCKWORKS_EXTERNAL_DATA_ROOT
resolves accepted originals. No source download occurs.

```bash
python -m puckworks.analysis.pannusch_two_assay_mass_delivery prepare --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_two_assay_mass_delivery freeze --out "$PRIVATE_RUN"
# Independent reviewer, not the author, supplies the exact-freeze approval.
python -m puckworks.analysis.pannusch_two_assay_mass_delivery score --out "$PRIVATE_RUN" --review "$INDEPENDENT_REVIEW"
python -m puckworks.analysis.pannusch_two_assay_mass_delivery report --out "$PRIVATE_RUN"
```

The authorized real scoring pass is exclusive. These commands document its
reproduction; they do not authorize another score after completion. Preparation
contains all 1008 statuses, states/failures, numerical call counts, and the exact
161-window support mask. Actual observations, predictions, per-shot reports and
logs remain private. Published hashes identify them without redistribution.
Restricted observed-support success cannot establish full-intended-suffix success.
004 remains FROZEN_EMPIRICAL_TRANSFER_INADEQUATE; all prior artifacts are unchanged.

The immutable API is `Observation`, `ObservationPair`, `FrozenBase`,
`FittedState`, `IntervalQuery`; `predict_intervals` and `remaining_solute` accept
only mass coordinates after assay 2. `to_dict/from_dict` and `save/load` bind
base bytes, runtime modules, units, roles and recomputed diagnostics. Six explicit
arm names are in `ARMS`. Zero delivery records unidentified k as null. No later
chemistry, condition coefficient, global fit or model selection is accepted.

Source-derived coefficients/states/results retain Pannusch/Schmieder attribution,
Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0, separate from first-party software.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No production default/lock changes, native
EWP runs, laboratory work, merge or successor is authorized.

Executed disposition: [RESULT.md](RESULT.md); [numerical qualification](QUALIFICATION_CARD.md); [QA/review](QA.md).
