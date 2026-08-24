# SCI-MD-004 Stage E0 R3 collection-pure protected-target QA

Change declaration: `NO_GOVERNING_PHYSICS_CHANGE`.

This QA-only child of the frozen R2 candidate preserves the V1, R1, and R2 failures. It does not inspect target content, change the scientific bundle, parameterize a model, generate a prediction, or score a holdout.

The launcher installs its Python audit hook before importing pytest. Protected opens during collection are always blocked. After collection, a read is permitted only while the isolated runner executes setup, call, or teardown for an item statically declared with `protected_target_integrity`; the item, opaque ID, artifact category, process, read mode, and candidate identity must match the committed manifest. No semantic Stage E0 module receives this capability.

Passing output contains only opaque identity, status, and aggregate counts. Test-originated stdout, stderr, logs, warnings, assertion details, exception arguments, dynamic parameter representations, captured sections, and JUnit representations are redacted. A failure exits nonzero and exposes only:

```text
PROTECTED_TARGET_INTEGRITY_TEST_FAILED
OPAQUE_TEST_ID=<ID>
FAILURE_PHASE=<PHASE>
GENERIC_FAILURE_CLASS=<CLASS>
NO_TARGET_VALUE_DISCLOSED
```

The Python audit hook is not a sandbox. The segregated execution retains independent operating-system open tracing as corroborating evidence.
