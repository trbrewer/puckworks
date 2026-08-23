# Reproduce

From exact commit `2cb75c1fdd8aae34abad66e8fb1d42b0630fdaad` with Python 3.12, NumPy 1.26.4,
and SciPy 1.11.4:

```bash
python3 -m puckworks.analysis.response_atlas validate
python3 -m puckworks.analysis.response_atlas run
python3 -m puckworks.analysis.response_atlas verify
python3 -m pytest tests/test_response_atlas.py -q
```

The run uses no OpenFOAM, randomness, or undeclared probability distribution.
