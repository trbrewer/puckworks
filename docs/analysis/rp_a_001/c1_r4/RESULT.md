# C1-R4 corrected producer result

Final replay authority: `61cafb5fbc5cfb42624763f9767009431049fc6f` / `67d63fa3a275abff1ac4fe7b2abb045926b32596`.

Two isolated executions of the corrected producer returned `RP_A_001_RUN_OK`; their independently reconstructive verification returned `RP_A_001_VERIFY_OK`. Both exports were byte-identical with SHA-256 `ade8dfeb2e1c599c47b67a4a8adb4c896e1d85195de3bb5e5a83587d5666e21b`. The only difference from the preserved C1-R3 v5 export is the execution commit and tree in `run_manifest`; deleting those two provenance fields produces identical canonical JSON.

The scientific state is unchanged and derived: 9 evaluations, 45 result cells, 37 supported, 6 unsupported for case, 2 unsupported relationships, zero numerical failures, four excluded requirements, zero measurement records, zero gate evidence/results, apparatus `NOT_EVALUATED`, incomplete global coverage, and `SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED`. The decision-input hash remains `11efe65820894e8bf3768c3c4e4a43c922f05139a06d4a26617cf621167df6b7`.

Physical validation remains `NOT_ESTABLISHED`.
