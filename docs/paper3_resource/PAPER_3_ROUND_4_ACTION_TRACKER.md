# Paper 3 — round-4 review action tracker

Review: [`PAPER_3_DETAILED_REVIEW_352DACD_2026-07-27.md`](PAPER_3_DETAILED_REVIEW_352DACD_2026-07-27.md)
(against `352dacd`). Branch `review-round-4-2026-07-27`.

| # | Item | Status |
|---|---|---|
| **P0-1** | The "producer-generated and CI-guarded" sections have drifted | ✅ **DONE.** Confirmed exactly: inline Appendix A carried **25** rows against the registry's **27**, missing `maille2024.two_regime` and `maille2024.phi_closure`, and Table 6a had two stale rows. The duplicate authoring path is **removed** — both blocks are spliced between markers from the same `generate()` / `run_benchmark()` output that writes the generated files — and `verify()` now covers the manuscript, not only `docs/paper3_resource/generated/`. Exact ordered membership and every Table 6a row are bound by tests, each confirmed to fail when the observed drift is re-injected. **The incident is disclosed in new §10.4** rather than quietly repaired: an infrastructure claim that has never been falsified in practice is weaker evidence than one that was, and was then closed. |
| **P0-2** | Evidence selection proves identity, not commensurability | ⚠️ **PARTIAL.** Selections are now mandatory and role-typed (below), but a machine-checkable *commensurability* predicate — that a selected record's observable, dataset and conditions match the claim's — is not implemented. Recorded as owed rather than claimed. |
| **P0-3** | Empty selections preserve the whole-inventory inheritance path | ✅ **DONE.** `evidence_profile()` **has no fallback**: it returns selected evidence, always. The load-bearing coverage check ran inside `if self.evidence_selections`, so the one case where inheritance actually happened — a claim with *no* selections — skipped it entirely. An unscoped component dependency is now a validation error, exempt only by explicitly declaring `context_only` / `tooling_only`. The review's counterexample fails validation and serialises an **empty** profile against a non-empty inventory. |
| **P0-4** | Public `evidence_strength` is authored, ungrounded and lossy | ✅ **DONE.** `within_campaign_held_out` no longer maps to `independent`: the public vocabulary distinguishes independent / held out within the same campaign / same campaign not held out / post-fit reconstruction / source-curve reproduction / verification / qualitative. `validate()` rejects an authored relation stronger than the **licensing** selections support, and `relation_detail()` exposes the registry-level detail beside the scalar. The cap respects licensing role — a comparator-context model does not drag a measured claim down to its tier, which would have falsely downgraded PV-01. |
| **P0-5** | Badge derivation is not genuinely non-authored | ⚠️ **PARTIAL.** Derivation fails closed and is enforced against the authored badge; orthogonality to outcome is not separately demonstrated. |
| **P0-6** | Dataset and campaign lineage lost before claim validation | ❌ **NOT DONE.** Owed. |
| **P0-7** | Numeric results are authored snapshots verified within tolerance | ❌ **NOT DONE.** Owed. |
| **P0-8** | Commit provenance is not persistent or current | ✅ **DONE.** `generated_from_commit` was stamped only `if ... is None`, but claims are rebuilt from source in every fresh process where it is *always* `None` — "immutable" held only inside one Python object's lifetime. Provenance is now read back from the committed artifact and carried forward **only while a new `payload_sha256` is unchanged**; a changed payload starts a new generation. Driven end to end by a test that exports at one pretend commit and re-exports at another. `regenerate()` also deep-copies: it was mutating the module-level claim singletons, so any export was a process-wide side effect. |
| **P0-9** | The scorecard performs component-level evidence roll-up | ⚠️ **PARTIAL — two of five parts done.** The **stale machine-boundary caveat** is corrected: it denied the existence of a typed node field after schema 0.8 added `PressureNode`/`require_node`, and now states the real remaining gap — the type exists and fails closed, but *this source trace's* node is unresolved. The **fragile open count** is fixed: `status == "open"` compared against a joined presentation string, so `"verification + open"` escaped the count; open state is now a predicate over the status components. **Still owed:** per-row claim-support records with exact evidence IDs, dataset/campaign IDs and node/unit contracts; status derived from the row's selection rather than the component inventory; and the two extraction branches described as separate observables. |
| **P0-10** | Appendix B overclaims schema coverage | ✅ **DONE (regenerated).** Appendix B is generated from the live schema and picked up the new fields. Its splice marker was **destroyed and restored** during this round — see below. |
| **P0-11** | Public exports discard the evidence-selection architecture | ⚠️ **PARTIAL.** `payload_sha256` and the relation detail are exported; a full selection-aware export surface is owed. |
| **P0-12** | Correct the mutation-suite class table; narrow the "production guard" claim | ✅ **DONE.** Table 6a is generated from `run_benchmark()` with controls in their own column, never in the injected denominator. "15 executable mutations that perturb a real input and run the production guard" was too broad: each case now declares the path it traverses, and the honest figure is **10** production-path mutations (8 caught), plus 3 integration sentinels, 2 static manuscript checks and 3 limitation analyses. "Independent structural groups" is now "declared structural families", because independence was never established. |

## What the round exposed beyond the review

- **A splice can destroy another splice.** Inserting the Appendix A markers by scanning forward to
  the next `## ` heading consumed the `<!-- appendix-b:begin -->` marker that sat immediately
  before the following heading. Appendix B's *content* survived, but its splice target did not, and
  `appendix_b.verify()` began reporting "missing markers" instead of comparing anything — a check
  that silently stopped checking. A structural marker-integrity test now asserts every pair is
  present, ordered and non-overlapping, whichever producer caused the damage.
- **A test can pin a defect in place.** `test_commit_provenance_separates_generation_from_verification`
  asserted the literal string `if c.generated_from_commit is None:` in the exporter's source — and
  that line *was* the P0-8 bug. Asserting an implementation rather than a property made the test an
  obstacle to fixing it. Rewritten to drive the exporter and check the behaviour.
- **My own additions had to be producer-bound too.** The new §10.4 disclosure and the execution-path
  table are both numeral-bearing manuscript prose; both are bound to `run_benchmark()` and
  mutation-tested, on the same standard the paper demands of everything else.

- **"0 unaccounted" was true for the wrong reason.** The numeral audit keys dispositions by the
  token's VALUE, not its context, so §10.4's count of 25 components was reported as accounted with
  the explanation *"draft date (25 July 2026)"* — the right disposition class attached to an
  unrelated fact. The audit still cannot report zero while a numeral is genuinely unregistered;
  what it cannot do is guarantee each numeral is accounted for the *right* reason. The limitation
  is now documented at the disposition table, and §10.4 states "two components short of 27" rather
  than carrying a colliding bare numeral.

## Standing lesson, restated

The paper's central claim is that duplicated generated material drifts. This round found that claim
falsified **inside the paper itself** — and the useful response was not to hide the incident but to
remove the duplicate authoring path and report it as evidence.
