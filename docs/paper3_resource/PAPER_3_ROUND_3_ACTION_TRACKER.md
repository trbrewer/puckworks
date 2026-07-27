# Paper 3 — third-review action tracker (`a0db098`)

**Source review:** [`PAPER_3_DETAILED_REVIEW_A0DB098_2026-07-26.md`](PAPER_3_DETAILED_REVIEW_A0DB098_2026-07-26.md)
(26 Jul 2026; verdict **major revision**).
**Actioned:** 2026-07-27.

The review's framing is accurate and worth restating, because it shaped the order of work: the
manuscript had come to describe **three development generations at once** — the former ordered
component-summary design, the current scoped-vector design, and the desired claim-selected design —
as if all three were current behaviour.

---

## Verification of the review's load-bearing claims

| Review claim | Result |
|---|---|
| `component_evidence_vector()` copies every record into every claim (P0-1) | **CONFIRMED** — PV-02 inherited 5 records including three negative-outcome findings about observables it does not assert |
| `PublicClaim` requires an authored badge; no `derive_badge()` exists (P0-2) | **CONFIRMED** — `validate()` checked vocabulary membership only |
| §5.1 and §5.2 give mutually exclusive accounts of ordering (P0-3) | **CONFIRMED** — and **the test suite pinned both**: one test required the "release heuristic"/"launder" wording, another asserted the ordering was gone |
| Dangling "DESCENDING strength order" source comment | **CONFIRMED** — immediately above a comment saying there is deliberately no ordering |
| Ownership table says the scorecard has no producer (P0-4) | **CONFIRMED** — and a test required the string "hand-maintained" |
| §4.1 says schema 0.6, Table 7 says 0.7, code says 0.7 (P0-5) | **CONFIRMED** |
| Table 2a omits the fines-provenance fields that motivated the bump | **CONFIRMED** |
| "pressure-node identity is not a field any contract carries" (P0-8) | **CONFIRMED FALSE PREMISE** — `MachineState` has carried `p_p`, `p_h`, `P_basket`, `dP_bed` since schema 0.4; D18 inspected field *names* for the substring "node" |
| D04 is a control counted in the defect denominator (P0-7) | **CONFIRMED** |

---

## P0 — publication blockers

| ID | Item | Status |
|---|---|---|
| **P0-1** | Claim-scoped evidence selection | ✅ **IMPLEMENTED.** `ClaimEvidenceSelection` (dependency ref, exact evidence-link ids, the claim's own observable and domain, the component's role, and a **rationale recording the deliberate exclusions**). Evidence links gained stable `link_id`-derived ids. `evidence_inventory()` keeps the full set for drill-down; `evidence_profile()` returns only the selection. All five public claims are scoped. `validate()` rejects a non-existent link, a link belonging to another dependency, and a load-bearing component with no selection. Tests cover wrong-dependency selection and the review's key criterion: **an unrelated strong record added to a component does not change any claim's badge**. |
| **P0-2** | Derive badges instead of authoring them | ✅ **IMPLEMENTED.** `derive_badge()` computes `(badge, rationale, limiting_dependency)` from the selected records, their evaluation designs and the component's role, and **fails closed** on ambiguity. An authored badge that disagrees is a validation error. All five seeded claims now derive exactly the badge they had asserted — which is the useful outcome: the labels were right, but nothing had been enforcing them. |
| **P0-3** | Remove the ordering contradiction | ✅ **DONE.** Obsolete §5.1 paragraph replaced by a historical note; dangling source comment deleted; **the test that pinned the old wording is replaced by one asserting it is gone**; Figure 2's "anywhere in the implementation" narrowed. |
| **P0-4** | Claim-ownership / scorecard producer | ✅ **DONE.** `P3-SCORECARD` now names `paper3.named_shot_scorecard.scorecard`. The correction is **disclosed, not applied silently** — the manuscript records that the row was true when written and is no longer — and the declared-configuration vs generated-claims distinction is drawn. The stale test is replaced. ⏭ Generating both the repository document and the manuscript table from one structured source (P1-7) is **not** done. |
| **P0-5** | Contract schema version and fields | ✅ **DONE.** Manuscript is now consistent with the live `SCHEMA_VERSION`, bound by a test that reads it from `contracts.py`. Table 2a gains the three fines-provenance fields, described as **declarations, not conversion formulas**. (The version is now **0.8**, because P0-8 added a contract — see below.) |
| **P0-6** | Mean-trace labelling + shot-level integration | ✅ **DONE.** Every occurrence of 0.573/0.648/0.116/0.096 is labelled a score on the preprocessed mean of five shots over 15–95 s, in the abstract too. New **Table 5a** gives both bases. The two conclusions are stated separately: the temporal-vs-constant ordering survives all five shots; the mean-trace RMSE is **not** shot-level accuracy. The "nearly reaches the flexible floor" claim is **withdrawn**. The blocked-holdout reason (TDS never shot-matched) is stated. |
| **P0-7** | Recast the defect benchmark | ✅ **DONE.** Cases gained `is_control`, `independence_group`, `execution_type` and `severity`. Reporting is now **18 defects / 13 caught / 5 missed / 9 independent groups / 2 controls, both passing / 0 false positives**, with **no coverage percentage emitted at all** — and the manuscript explains why recomputing 67 % as 64.7 % would have preserved the error. `detection_rate` is gone from the result object and a test forbids its return. |
| **P0-8** | Correct the pressure-node diagnosis | ✅ **DONE.** The false premise is corrected in the manuscript, the scorecard row and Figure 3's caption, with the *real* gap named: legacy traces carried no node identity and same-typed fields can be swapped. Added `PressureNode`, `PressureTrace` and `require_node` (schema **0.8**); D18 is replaced by an **end-to-end adapter mutation** that now passes, plus **D19** (valid control — a correct trace must be accepted) and **D20** (untyped legacy trace fails closed). |
| **P0-9** | Narrow Appendix B | ✅ **DONE.** The universal-coverage claim is withdrawn and the other generated claim classes are enumerated; a single cross-class coverage registry is stated as future work. The `badge` and new `evidence_selections` field notes describe the implemented behaviour. |
| **P0-10** | Reconcile readiness statements | ✅ **DONE.** Figure status corrected; the environment lock described **precisely** — `requirements-paper-release.lock` is a *direct-version* lock, deliberately not a transitive lock or container digest, so neither "no pinned environment" nor "transitive lock landed" was accurate. The blocker list gains claim-selection coverage and states explicitly that **a DOI is not the only remaining gap**. ⏭ Metadata, ethics determination, archival release and clean-room reproduction remain open. |

## P1 items actioned

- **P1-5** Outcome derivation was `context_only + claim_not_supported → negative`, everything else
  `supported` — which silently turned blocked, unresolved and not-run records into supporting ones.
  Now an **exhaustive** mapping that **raises** on an unhandled status.
- **P1-6** The fit/evaluation axis is carried as its own field (`fit_evaluation`), distinct from the
  comparison relation, and is what badge derivation reads.
- **P1-12** Table 2's claim about named typed fields is narrowed to what they actually achieve.
- **P1-16** Figure 2's absolute "anywhere" claim narrowed.
- **P1-17** The abstract's manifest-record phrasing corrected: "supported by 107 dataset-manifest
  records" read as 107 validation datasets → "described by 107 provenance-manifest records".

## Not actioned

- **P1-1** — *partly closed on a re-check.* The **manuscript sentence** is fixed: §9.2 said "the
  result is negative validation of that configuration", contradicting §5's own rule that a negative
  result is an outcome on a relation and not a relation of its own. It now reads "a negative outcome
  on an exploratory-synthesis check", and says which sentence it is correcting. What remains is only
  the **vocabulary migration** — removing the legacy `negative validation` entry from
  `EVIDENCE_STRENGTHS` — which needs an artifact-migration decision because published artifacts
  carry it. New validation already rejects it.
- **P1-2** deriving scorecard **stage** statuses from stage-selected links — the selection machinery
  now exists, but the scorecard has not been migrated onto it.
- **P1-4** the many-to-one public evidence mapping still collapses held-out/independent and
  reproduction/reconstruction.
- **P1-8** references 7–9; **P1-11** timescale model-selection diagnostics; **P1-13** the legacy
  bar-gauge/Pa callback; **P1-20** freezing test/gate reports as release artefacts.
- **P1-19** — *closed on a re-check.* Four bare parenthetical review IDs in production source
  ("Paper 3 review P0-4 option 1", "(Paper 3 review P0-3/P0-4)") are replaced with the design
  rationale they stood for. Comments added during this work that carry substantive rationale — what
  changed, why the previous behaviour was wrong — are **kept**, with the review ID as dated
  provenance rather than as the content; that is the "stable design rationale" the review asked
  for, not the thing it objected to.
- **§15 structural rewrite** and the related-work feature matrix.

## Repo-convention follow-up

`CLAUDE.md` requires a `docs/ROADMAP.md` §7.1 changelog entry for a contract change. **Added**
(2026-07-27, schema 0.7 → 0.8). A `docs/SPRINTS.md` tick is **not** added: these are review
responses rather than a planned sprint item, and choosing where they sit in the sprint breakdown is
an author decision.
