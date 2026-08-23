# C1-R4 replay record

The corrected producer was run in two clean disposable clones at exact commit `61cafb5fbc5cfb42624763f9767009431049fc6f`. Each clone ran:

```text
PYTHONPATH=. python -m puckworks.analysis.response_atlas run
PYTHONPATH=. python -m puckworks.analysis.response_atlas verify
```

Both commands succeeded twice. Both scientific exports have SHA-256 `ade8dfeb2e1c599c47b67a4a8adb4c896e1d85195de3bb5e5a83587d5666e21b`; both run manifests have SHA-256 `b322ebce5c6f2174faedd13a1041c3b5eea2e77714b51ce4854df69f9d55abec`. Runtime records differ only because wall duration is expressly noncanonical.

The original C1-R3 retained files were not modified. Disposable replay copies alone received generated changes.
