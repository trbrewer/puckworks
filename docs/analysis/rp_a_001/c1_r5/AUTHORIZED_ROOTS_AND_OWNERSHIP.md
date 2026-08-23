# Authorized roots and ownership

The production root universe is reconstructed from:

- `docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md`;
- `docs/analysis/rp_a_001/c1/correction_protocol.json`, C1-R1/C1-R2 protocols, and `c1_r3/correction_protocol.json`;
- `docs/analysis/rp_a_001/c1/case_matrix.json` and `measurement_assumptions.json`;
- `puckworks/models/__init__.py` registry identity;
- selected cards under `docs/cards/` and their manifest hashes;
- selected components and cards in `run_manifest`;
- canonical question, requirement, observation-contract, adapter, and gate constructors.

An authorized record is a root or is transitively owned by selected explanation, case, question/requirement/pair, channel/contract, and gate contexts. Full-atlas result cells, predictions, inventory, residual, and component-report rows may be unused by the final decision but are authorized only when their model, selected case, observable, contract-compatible context, and provenance all bind to those roots.

There is no general auxiliary-record allowance. The only permitted auxiliary data are the existing schema-defined full-atlas diagnostic/result records whose ownership is derivable from selected roots. Undeclared or disconnected material records are rejected.
