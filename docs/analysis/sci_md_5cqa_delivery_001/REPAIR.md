# WP6 fixed-history prerequisite repair

G0 / NO_GOVERNING_PHYSICS_CHANGE; bounded SCI-MD-5CQA-DELIVERY-001 amendment.
The original clean baseline failed
`test_screen_wp6_lateral_identifiability.py::test_no_foundry_infrastructure_was_added_or_modified`.
The assertion compared a completed screen to moving HEAD. Puckworks #296 later
appended I-094/I-095 and T-0176/T-0177, preserving all earlier ID assignments.
That change is outside the screen's historical claim.

The fixed base is `f77d0e328496dc1e85bf00fdb06ccdc52d8b2108`, the result's
`source_commit`. The completion endpoint is
`13c398e038c94ae8f95c8106e327e47d3d5f5345`, the final reviewed branch commit of
[PR #233](https://github.com/trbrewer/puckworks/pull/233), merged as
`bbbc2b5f44be3bc5f0ee5951985e5f8594bbc6e1`. It contains the final structural-versus-
numerical-degeneracy correction and the exact current result blob
`c3c751247307382e98295eab2ce8fd05e979c6bb`. Both objects exist; the base is an
ancestor of completion. Endpoint selection follows the original PR and result
provenance, not an empty-diff search. All three protected paths are unchanged
across this historical range.

Only the named test module and this explanation change. Historical flags,
protected paths, scientific/source-binding assertions, and present-day I-045
registry-preservation checks remain active. The existing unavailable-base
shallow-checkout convention is retained; local acceptance requires execution,
not a skip. Every helper Git command must succeed before its output is used.
Disposable-history regression checks cover a later change and a protected change
inside the checked range. Failed object, ancestry and diff commands fail closed.
No real registry, source, result, model, generator or QA configuration is changed.

The original blocked-run evidence remains immutable. Repair-only validation,
exact candidate tree, separate repair commit and actual results are recorded in
the task's retained continuation evidence and final QA record. No 5-CQA draft is
installed before that baseline passes. This repair establishes no model adequacy.
