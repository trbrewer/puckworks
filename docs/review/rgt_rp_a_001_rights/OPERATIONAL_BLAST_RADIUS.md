# Operational blast radius

The use-specific callers are `puckworks.product.lab_rights_gate`, Lab matrix/explorer helpers, public-app request construction, and release/reporting utilities that call `may_execute_in_public_batch`, `may_publish_outputs`, `may_include_code_in_release`, or `may_include_data_in_release`.

- Cameron and Foster: public code execution becomes affirmative because their code is independently reimplemented; public artifact publication remains blocked by `RIGHTS_REVIEW_REQUIRED` output states.
- Wadsworth: public code execution becomes affirmative, but global output publication remains fail-closed. The narrow RP-A finding does not add the component to broader public-product or manuscript surfaces.
- Release semantics remain intentionally distinct: a review gap is reportable but not a hard release block under existing policy. The determinations do not create a blanket component-cleared shortcut.

Tests retain unresolved, blocked, unknown-component, zero-producer, local/public separation, output-publication, and no-bypass cases. No service was deployed and no scientific public batch was run.
