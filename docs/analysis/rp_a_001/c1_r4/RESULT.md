# C1-R4 corrected producer result

Execution authority: `e43d5f3e6140721f0c9923428f2c7503f43433de` / `a5fbfe2ab542ea1405763cd3b8b730c90a843c10`.

Two isolated executions of the corrected producer returned `RP_A_001_RUN_OK`; their independently reconstructive verification returned `RP_A_001_VERIFY_OK`. Both exports were byte-identical with SHA-256 `01a8a1a2047a8d942925914885dc984bf665d0e719ac1f49b170ec9f10758d16`. The only difference from the preserved C1-R3 v5 export is the execution commit and tree in `run_manifest`; deleting those two provenance fields produces identical canonical JSON.

The scientific state is unchanged and derived: 9 evaluations, 45 result cells, 37 supported, 6 unsupported for case, 2 unsupported relationships, zero numerical failures, four excluded requirements, zero measurement records, zero gate evidence/results, apparatus `NOT_EVALUATED`, incomplete global coverage, and `SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED`. The decision-input hash remains `11efe65820894e8bf3768c3c4e4a43c922f05139a06d4a26617cf621167df6b7`.

Physical validation remains `NOT_ESTABLISHED`.
