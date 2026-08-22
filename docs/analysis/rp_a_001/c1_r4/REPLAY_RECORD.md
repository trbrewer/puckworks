# C1-R4 replay record

The corrected producer was run in two clean disposable clones at exact commit `0624e69947bf17f19429e0ad7df2d89fc40c065d`. Each clone ran:

```text
PYTHONPATH=. python -m puckworks.analysis.response_atlas run
PYTHONPATH=. python -m puckworks.analysis.response_atlas verify
```

Both commands succeeded twice. Both scientific exports have SHA-256 `7256bb0bf1fedba43d2062e2ef3bd4e1114fe9feb55669111e0330902673cec8`; both run manifests have SHA-256 `904554b43d984a02a6b71a93640b138e011cce4e315e1509dd6f1d4f4cf707e1`. Runtime records differ only because wall duration is expressly noncanonical.

The original C1-R3 retained files were not modified. Disposable replay copies alone received generated changes.
