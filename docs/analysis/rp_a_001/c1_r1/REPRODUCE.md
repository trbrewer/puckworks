# Reproduce C1-R1

Checkout execution commit `a6e6cd1c46121a9338e4e8358bc68b9ad56d8e55`
(tree `c454deefc1a603ea4484b35a8ab3e455af1f66f6`) in the supported Python
environment, then run:

```bash
python -m puckworks.analysis.response_atlas validate
python -m puckworks.analysis.response_atlas run
python -m puckworks.analysis.response_atlas verify
```

Canonical scientific JSON uses sorted keys, two-space indentation, UTF-8, and a
terminal newline. `atlas_export.sha256` hashes the payload bytes without placing
the hash inside its own payload. `runtime.json` alone contains operational wall
duration and is explicitly excluded from scientific byte comparison.
