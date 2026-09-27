# SCI-MD-MASS-DELIVERY-007

[Puckworks issue #291](https://github.com/trbrewer/puckworks/issues/291),
[EWP issue #197](https://github.com/trbrewer/espresso-whole-pull/issues/197).
G1 / NO_GOVERNING_PHYSICS_CHANGE; fixed C2 primary, zero fits or native runs.
[Protocol](PROTOCOL.md), [model use](MODEL_CARD.md),
[scoped preflight](DATA_AVAILABILITY_PREFLIGHT.json), [parent pin](PARENT_006_HANDOFF.json).

Use the existing Python environment with NumPy/SciPy. Resolve SOURCE_ROOT from
owner-local configuration and prior GRUDEVA-CLOCK-001 evidence; OUT must be a
new private directory outside Git. Preserve all failed attempts. These commands
are distinct operations, not an automatic execution script:

```bash
python -m puckworks.analysis.grudeva_pooled_tail_delivery prepare --source-root "$SOURCE_ROOT" --out "$OUT"
python -m puckworks.analysis.grudeva_pooled_tail_delivery retain-reference --prior "$PRIOR_GRUDEVA_EVIDENCE" --out "$OUT"
python -m puckworks.analysis.grudeva_pooled_tail_delivery predict --out "$OUT"
# Run the exact EWP consumer on serialized early inputs and coordinate-only queries;
# retain verified parity receipt, then freeze both committed candidate identities.
python -m puckworks.analysis.grudeva_pooled_tail_delivery freeze --consumer "$EWP" --out "$OUT"
# ONLY after fresh independent exact-freeze approval:
python -m puckworks.analysis.grudeva_pooled_tail_delivery score --review "$REVIEW" --source-root "$SOURCE_ROOT" --consumer "$EWP" --out "$OUT"
python -m puckworks.analysis.grudeva_pooled_tail_delivery report --out "$OUT"
python -m pytest -q tests/test_grudeva_pooled_tail_delivery.py tests/test_conditional_tail_delivery.py
```

Prepare constructs geometry/pools without fitting. Predict sees typed arm inputs
and coordinates only. Score has one exclusive start/completion pair. Report only
reads hash-bound retained scores. Optional saved MASS rows are a source-trained
diagnostic with different information privileges, never a selection arm.
No raw data or source-derived rows are public. No merge, adoption or successor.
