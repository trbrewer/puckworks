# C1-R4 replay record

The corrected producer was run in two clean disposable clones at exact commit `e43d5f3e6140721f0c9923428f2c7503f43433de`. Each clone ran:

```text
PYTHONPATH=. python -m puckworks.analysis.response_atlas run
PYTHONPATH=. python -m puckworks.analysis.response_atlas verify
```

Both commands succeeded twice. Both scientific exports have SHA-256 `01a8a1a2047a8d942925914885dc984bf665d0e719ac1f49b170ec9f10758d16`; both run manifests have SHA-256 `94b5aff7487d7e8b7e22502779d662915a9d4afce4574ba38413346fccf97b68`. Runtime records differ only because wall duration is expressly noncanonical.

The original C1-R3 retained files were not modified. Disposable replay copies alone received generated changes.
