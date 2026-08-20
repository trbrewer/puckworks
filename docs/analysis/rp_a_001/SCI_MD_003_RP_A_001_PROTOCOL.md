# SCI-MD-003 / RP-A-001 frozen programme protocol

Protocol `sci-md-003-rp-a-001/v1` extends, without modifying, `component-response-atlas/v1`.
It freezes a bounded three-component pilot before comparative outputs are inspected.

The scientific question is which apparent disagreements survive explicit observable, pressure-node,
reference-basis, control-mode, valid-range, initialization, and observation contracts, and which
synchronized measurement could distinguish the remaining explanations. It does not select a global
best model, create a consensus model, promote evidence, or establish physical validation.

The selected components are `foster2025.machine_mode` (fixed-bed machine/apparatus null),
`wadsworth2026.inertial` (static hydraulic response lens), and
`cameron2020.extraction_bdf` (downstream extraction observer). Authoritative producers are called;
their equations are not copied into the analysis layer. Baselines are the Wadsworth producer's exact
Darcy limit and Foster's fixed-bed machine response. Cameron uses its legacy scalar-q path; arbitrary
transient hydraulic-history transfer is frozen as unsupported.

The cases, native mappings, summaries, two derivative steps, tolerances, uncertainty treatment, seed,
and caps are machine-readable in `protocol.json`, `case_matrix.json`, and
`measurement_assumptions.json`. Source bounds without distributions use deterministic endpoints or
one-at-a-time perturbations. Missing uncertainty is never converted into a distribution.

Comparative classification order is sign, pressure ordering, grind direction, curvature/regime,
timing/phase, cross-condition transfer, then aggregate error only when a common target exists. Numeric
residuals require comparability level 1 or 2. Additive decomposition requires a nested producer pair
and frozen closure tolerance. The claim ceiling is `MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED`.

