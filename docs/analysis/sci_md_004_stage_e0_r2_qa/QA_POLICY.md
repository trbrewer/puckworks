# SCI-MD-004 Stage E0 R2 silent target-integrity QA

This is a QA-only recovery from the frozen R1 scientific candidate. The scientific subtree `docs/analysis/sci_md_004_stage_e0/` remains byte-identical.

The historical R1 detector is classified `NON_PROVENANCE_AWARE_TARGET_STRING_SCAN`, with `R1_RESULT = FAILURE` and `CAUSE = UNADJUDICATED`. It is preserved outside Git as R1 evidence and is not an R2 gate. Its matching token or context was not inspected.

R2 enforces provenance rather than target-string comparison. Every `protected_target_integrity` test receives a static opaque ID. Test-originated stdout, stderr, logging, or warnings cause a generic redacted failure. Assertion and exception representations are replaced before terminal and JUnit serialization. Unmarked protected-target file access fails closed. Pytest framework progress and aggregate counts are not test-originated output and are not compared with target cells.

Visible protected-test failure text is limited to:

```text
PROTECTED_TARGET_INTEGRITY_TEST_FAILED
OPAQUE_TEST_ID=<ID>
FAILURE_PHASE=<PHASE>
GENERIC_FAILURE_CLASS=<CLASS>
NO_TARGET_VALUE_DISCLOSED
```

No protected scoring is authorized in Stage E0 R2.
