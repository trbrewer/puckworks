# EWP-RWB-001 C1 result

## Disposition

`EWP_RWB_001_RECON_C1_PARTIAL_PROVENANCE_RECOVERED_NO_PRESSURE_BEARING_OVERLAP`

The retained 23,169-record Bronze corpus recovers explicit `brewdata.parser` provenance for
1,004 Beanconqueror records contributed by 41 linked users. Those records contain zero valid
commanded-pressure and zero valid achieved-pressure channels. The unchanged frozen structural
rules recover no family among the remaining 22,165 records. No EWP pressure lane reopens.

## Authority and Attempt 1

Puckworks base `a3428a4d4ad571ef3168a70e8a04620fca5d3520`, merged EWP authority
`97d586fe21ca28cf7ef80a03ec0e15f3032ac0b5`, and version-matched Visualizer source
`c46dda76c8271a2ae22531fa4ee9bb81728ed128` were verified. The public source is a strong
version-matched candidate, not proof of the deployed production revision.

Attempt 1 correctly stopped: naïve replay from privacy-filtered Bronze changed
`context.profile_present` in 23,168 records and `context.n_tags` in 82. It changed no hydraulic,
outcome, units, QC, identity, or user-linkage data. Those losses were not permitted.

## C1 gate and circuit breaker

The private aggregate gate ran twice with identical SHA-256
`202a73ec8bd3cf144f0b73a7b5263a43c16f16a8afae00eea553bc9f70148402`. The only recovered
family was `VISUALIZER_BEANCONQUEROR`: 1,004 explicit records, 41 contributors, zero command
overlap, zero achieved overlap. Structural recovery, conflicts, and ambiguities were all zero;
22,165 records remained unresolved.

The pressure-bearing gate therefore failed scientifically. Under the owner-authorized circuit
breaker, preserving migration, schema v7, future-normalizer changes, and pressure-semantic
adjudication were `NOT_EXECUTED_NOT_JUSTIFIED`. Schema remains 6 and every historical normalized
field remains unchanged.

Allowed EWP lanes are empty. The Visualizer transfer route is closed unless new explicit
pressure-source authority or a rights-cleared source export becomes available. The selected
successor is `OBS-PANNUSCH-FRACTION-WINDOW-001`; it was not implemented.

No network acquisition, private-record use, raw/per-record publication, hardware inference,
permeability or resistance work, EWP modification/execution, OpenFOAM run, physics/default
change, or laboratory work occurred.
