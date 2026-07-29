# Paper 1 — Round 7 action tracker

**Review:** `PAPER_1_ROUND_7_DETAILED_REVIEW.md` (target `5db834b`)
**Actioned on:** `paper1-round7`
**Verdict accepted:** not ready for submission at the reviewed commit. All three P0s reproduce
exactly as described, and one of them was being actively enforced in the wrong direction by CI.

Two decisions in this round were the author's, not the reviewer's, and both were taken with the
numbers in hand rather than in advance: the corpus contract (P0-3, Option A) and whether to narrow
or actually run the loss-robustness claim (P1-2, run it).

---

## Disposition

| ID | Finding | Action | Rerun? | Outcome |
|---|---|---|---|---|
| **P0-1** | Manuscript `Re` differs from code by `α_l⁻² ≈ 34.6` | Documentation corrected to the source's superficial-velocity convention in manuscript, draft and card; contract test recovers `Re` numerically from `Sh` | **No** | The code was right; the frozen `A_x,i`/`B_x,i` were fitted under the superficial convention, so changing it would have invalidated them |
| **P0-2** | 38/40/42 g endpoints labelled mL throughout | `_V_TARGET_ML` → `_M_TARGET_G`; relabelled across abstract, Tables 2/4a, §§2.3–2.4, §§3–4, limitations, SI Methods S2, Table S3, all captions, and the text baked into `fig4_transfer.png` | **No** | The values were already mass-endpoint values. The sweep is now the source's own declared ±2 g tolerance rather than an invented bracket |
| **P0-3** | 8 off-grid C/F records excluded while Table 1 claimed the whole corpus | Both contracts computed; **complete 44-record corpus adopted** (132 obs). Producers emit included/excluded sample IDs | **Yes** | Conclusion unchanged in every slice — see below |
| **P1-1** | Resampling broke cross-solute condition dependence | Primary cluster is now `(variety, T, p)`; old units demoted to secondary; `ci95_pp` → `percentile_range_pp` | **Yes** | The correct unit is **wider**; the previous precision was manufactured by dropping a real dependence |
| **P1-2** | Loss robustness tested the model's own error, not the paired estimand | New `comparator_loss_robustness`: both predictors refit and rescored under the alternative loss | **Yes** | −0.394 → −0.393 pp; sign and reading unchanged. The claim is now about the quantity it names |
| **P1-3** | SI S1 claimed one least-squares level fit for three objectives | Replaced with the objective-specific statement plus formulas; generated, not hand-authored | No | OLS / weighted LS (1/y²) / IRLS |
| **P1-4** | One-panel convergence read as global assurance | Reading narrowed to the Arabica-caffeine panel, its listed outputs and the tested node × tolerance domain; `reading_scope` surfaced in Table S5 | No | — |
| **P1-5** | **Confirmed stale**: audit reported 65/436 and 60/77 from `fc61c46` | Audit is now generated (`tools/claim_binding_audit.py`) with input fingerprints; CI fails when its inputs move | No | The only confirmed stale numbers in the round were in the document that measures staleness |
| **P1-6** | Audit asserted uniform precision the SI contradicted | One canonical archive, one rendering policy (three decimals); main table, SI table, readings and captions all generated from it; superseded "two runs" paragraph removed | No | `excludes_zero` is now decided on the **rounded** bounds the paper quotes, so flag and interval cannot disagree |
| **P2-1** | SI inadvertently asserted structural identifiability | Replaced with an explicit non-assessment | No | — |
| **P2-2** | Trained comparator called a statistical "null" | "level-only comparator" throughout manuscript, SI, captions, figures and producer verdicts | No | One deliberate use survives, in the sentence that says it is *not* a statistical null |
| **P2-3** | §5 renewed an absence claim; unmatched parenthesis | Both fixed; the same-model exact-cup calculation is now named as an interim control | No | — |
| **P2-4** | Figure 3 title/legend/annotation collisions | Short title, endpoint read from typed `m_target_g`, shared legend outside the data area, count moved to the axis label | No | — |

---

## What the corpus change did to the headline

| | matched on-grid (108 obs) | **complete corpus (132 obs)** | off-grid only (24 obs) |
|---|---|---|---|
| model / comparator MAPE | 8.23 / 8.59 | **8.44 / 8.83** | 9.39 / 9.93 |
| paired difference | −0.361 pp | **−0.394 pp** | −0.545 pp |
| model worse on | 50 of 108 | **62 of 132** | 12 of 24 |
| primary range, (variety,T,p) | [−0.826, +0.037] | **[−0.825, +0.000]** | — |

Both predictors degrade away from the training grid and the conclusion is the same in every slice.
The complete corpus was adopted because it makes Table 1's existing claim true rather than
qualifying it, and because the excluded records are precisely the campaign's own designated
validation points — the wrong eight records to drop from a claim about transfer.

The same-(T,p) lookup comparator is demoted to a **matched-grid secondary**: none of the eight
off-grid conditions has an optimal-grind counterpart, so it is undefined on 24 of 132 points. It is
reported on its own support rather than pooled across two different corpora.

**A boundary that is not a result.** At 40 g and 42 g the primary range's upper bound rounds to
+0.000; at 38 g it clears zero by 0.046 pp. Reporting one of those as "excludes zero" and another
as "includes zero" would be a claim about the third decimal place of a resampling percentile. The
manuscript declines to make it, and `paired_clustered_bootstrap` now decides `excludes_zero` on the
rounded bounds and reports `nearest_bound_to_zero_pp` alongside, so the artifact cannot disagree
with the prose about which side of zero it is on.

---

## The reviewer's central point, in one table

Every P0 in this round passed the existing value-level bindings. That is the finding, not an aside.

| defect | why the numeral audit saw nothing |
|---|---|
| Reynolds off by `α_l⁻²` | both equations contain the same constants; only the *use* of porosity differs |
| 40 g labelled 40 mL | the token "40" is byte-identical in either unit |
| 108 records called the whole corpus | 108 is arithmetically correct — for the subset nobody declared |
| resampling omitted cross-solute dependence | the reported values match the producer exactly |
| SI described one optimizer for three objectives | every reported minimum still resolves against its archive |
| the audit itself was stale | the audit sat outside its own binding chain |

`tests/test_paper_a_model_contract.py` binds meaning instead of tokens: the displayed equation
against the evaluated one, the endpoint's unit against its stopping rule, the declared corpus
against the emitted sample-ID manifest, the resampling cluster key, the SI optimizer description
against `_profile_objectives`, the audit against its inputs, and interval precision across the
manuscript and the supplement.

---

## Not actioned, and why

* **`tests/test_manuscript_structure.py::test_paper_3_generated_blocks_are_current` and
  `tests/test_paper3_corpus.py::test_generated_artifacts_and_the_manuscript_block_are_fresh`**
  fail on this branch and failed before any round-7 change (verified by stashing). They are Paper 3
  generated-block staleness, out of scope for a single-paper round.
* **Author list, ORCIDs, CRediT, funding, competing interests, AI declaration, licensed novelty
  search, release DOI** — declared out of scope by the round-7 brief and unchanged.
