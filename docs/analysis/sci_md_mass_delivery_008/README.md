# SCI-MD-MASS-DELIVERY-008

[Executed result](RESULT.md): `ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED`. One independently approved score; final publication review and CI remain separate PR statuses.

One-calibration-shot source adaptation, fixed primary A2. G1 /
NO_GOVERNING_PHYSICS_CHANGE. [Model card](MODEL_CARD.md), [protocol](PROTOCOL.md),
[preflight](DATA_AVAILABILITY_PREFLIGHT.json), [source/cohort](SOURCE_COHORT_CONTRACT.json).
Linked issues: [Puckworks #293](https://github.com/trbrewer/puckworks/issues/293)
and [EWP #199](https://github.com/trbrewer/espresso-whole-pull/issues/199).

The exact frozen producer implements preparation, calibration, prediction,
freeze, one approved score and saved-result report as distinct operations.
All real artifacts must be outside Git. Resolve source/prior locations from the
existing owner configuration and accepted 007 evidence locators.

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.grudeva_one_shot_calibration prepare \
  --source-root ACCEPTED_ORIGINALS --prior ACCEPTED_007_RUN --out NEW_PRIVATE_RUN
python -m puckworks.analysis.grudeva_one_shot_calibration calibrate --out NEW_PRIVATE_RUN
python -m puckworks.analysis.grudeva_one_shot_calibration predict --out NEW_PRIVATE_RUN
# Commit the consumer handoff and verify its complete saved-matrix equivalence.
python -m puckworks.analysis.grudeva_one_shot_calibration freeze \
  --out NEW_PRIVATE_RUN --consumer EXACT_CONSUMER_CHECKOUT
# Only after the fresh independent reviewer approves the exact freeze:
python -m puckworks.analysis.grudeva_one_shot_calibration score \
  --out NEW_PRIVATE_RUN --consumer EXACT_CONSUMER_CHECKOUT --review PRIVATE_APPROVAL
python -m puckworks.analysis.grudeva_one_shot_calibration report --out NEW_PRIVATE_RUN
```

Reports need only saved scores and their completion binding; no originals,
calibration, new predictions or source access. Exclusive start/completion files
preserve attempts and prevent replays. Synthetic checks use only invented data:

```sh
python -m pytest -q tests/test_source_calibrated_tail_delivery.py \
  tests/test_grudeva_one_shot_calibration.py
```

007's failed zero-shot transfer remains unchanged. 008 expressly reuses one
other physical shot as calibration information in each fold. All shots train
other folds; 110 ordered pairs are not independent experiments. The source
varies across repeated shots and does not establish a controlled fixed-recipe
calibration campaign. Rights, limitations and numerical versus physical
qualification are preserved in the model card.

MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false;
PRODUCTION_DEPENDENCY_LOCK_CHANGED=false; NATIVE_EWP_RUNS=0;
NO_SUCCESSOR_AUTHORIZED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
