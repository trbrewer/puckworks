# Reproduce C1-R2

Checkout execution commit `a8f2679985948bf82443aee30f35ff4e504fc74a`
(tree `0707f3b3a1bfa5b4f2887c46d40bdbf5402e101e`) in the supported Python
environment, then run:

```bash
python -m puckworks.analysis.response_atlas validate
python -m puckworks.analysis.response_atlas run
python -m puckworks.analysis.response_atlas verify
```

Canonical scientific JSON uses sorted keys, two-space indentation, UTF-8, and a
terminal newline. `atlas_export.sha256` hashes the payload bytes without placing
the hash inside its payload. `runtime.json` alone contains normalized operational
duration. The Git commit retaining the generated bundle supplies its immutable
result identity without creating a circular self-reference.
