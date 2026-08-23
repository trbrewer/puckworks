# Reproduce C1-R3

From execution commit `2d04a56127869b4d4da8524166ff026890e9fa53`
(tree `cef3f264b1906424fc6d00622a9e15fb45874829`), in the supported environment:

```bash
python -m puckworks.analysis.response_atlas run
python -m puckworks.analysis.response_atlas verify
```

Canonical JSON uses sorted keys, compact deterministic separators, UTF-8, and a
terminal newline. SHA-256 is calculated over `atlas_export.json` and retained in
`atlas_export.sha256`; the payload does not contain its own hash. Only runtime
wall duration is retained separately in `runtime.json` and excluded from
scientific byte comparison.

Expected export SHA-256:
`17b19c7a44cd9307ea798643e6f7e26827924dbe02dfe65c272e1d485bd8203e`.
