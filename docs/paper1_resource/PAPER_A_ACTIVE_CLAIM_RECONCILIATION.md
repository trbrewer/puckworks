# Paper A — active claim reconciliation

**Gate:** P0-G1a. Performed **before** the protocol freeze and before any new scientific run.
**Trigger:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1_REVIEW_20260801.md` §3.4, which found that the
plan's prose had been corrected while several *active repository artefacts* still asserted the
withdrawn claims. Verified — every item below was confirmed in the repository before it was changed.

Numerical evidence is untouched. Only interpretive fields, labels and docstrings changed, and no
history was rewritten.

---

## 1. What was wrong

| surface | asserted | why it was withdrawn |
|---|---|---|
| `PAPER_A_SATURATION_VERIFICATION.json` | `"verdict": "PHYSICAL"`; question asked whether saturation is "physical" | both integrators share the equations, spatial operator, parameterisation and omitted physics — the path is independent **in time only** |
| `tools/paper_a_saturation_verification.py` | docstring framed the check as physical | same |
| `PAPER_A_ABLATION_REFIT_STABILITY.json` | question read *"freezing the rate transfers better"* | the pooled sign is not stable, coarse and fine oppose, and "transfer" is reserved for cross-grind evaluation |
| `PAPER_A_INFORMATION_PARITY.json` | `M0_to_M2` = "RATE RECALIBRATION ALONE" | M0−M2 is an **estimation-policy** contrast; the inventory level is re-profiled under each policy |
| `tools/paper_a_information_parity.py` | module heading said "mechanistic attribution" | M1−M2 is an **input substitution**; particle geometry was frozen and never varied |
| `puckworks/paper_a/separability.py` | "all local rate information after profiling the level" | true only in the declared **weighted-L2 surrogate**; the production objective is MAPE, piecewise linear in the level |
| `PAPER_A_CLAIM_LEDGER.md` | S4 "coexists with weak localisation"; S5 pooled wording; S10 "all local rate information" | localisation classification requires `J_inf`; pooled wording hides the grind reversal; S10 as above |

---

## 2. What changed

**Rescoped, artefacts regenerated from their producers:**

- saturation verdict `PHYSICAL` → **`MODEL-STRUCTURAL`**, with new explicit fields
  `evidence_type`, `temporal_artifact_status: not_BDF_artifact`, `physical_validity: untested`, and
  `current_interpretation`;
- ablation question rewritten as an estimation-policy contrast, naming that **both** arms receive the
  target-grind map and **both** re-profile the level;
- `M0_to_M2` relabelled **estimation-policy contrast**; `M0_to_M1` already declared confounded;
- information-parity heading changed to *input ablation*, with an explicit note that a substitution
  effect is not a causal mechanism because geometry was held fixed;
- `separability.py` docstring now states the Schur complement and determinant separately and says
  plainly that neither is MAPE curvature.

**Superseded, not rewritten:**

- `PAPER_A_CLAIM_LEDGER.md` → superseded by `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json`, and classified
  `historical` in the manifest;
- plan revisions v1, v2, v2.1 → superseded banners, classified `historical`;
- `docs/ROADMAP.md` and `docs/SPRINTS.md` → **deliberately unchanged**. They are a dated audit trail
  and rewriting them would destroy the record of what was believed when. They are classified
  `historical` in the manifest so a repository search cannot mistake them for the current position.

---

## 3. How this is now enforced

`PAPER_A_PLAN_MANIFEST_V1.yaml` lists `active_claim_surfaces` and `historical_exclusions`
explicitly, and `banned_assertions` with a reason attached to each. `tests/test_paper1_plan_integrity.py`
scans every active surface and fails on a match outside a quoted or code span.

Exemption is **by explicit classification**, never by filename convention — so adding a new artefact
without classifying it fails, rather than passing silently.

---

## 4. Verification

- every listed defect confirmed present before change;
- producers edited and archives regenerated, so no artefact was hand-edited away from its producer;
- `--check` modes reproduce the regenerated archives;
- a repository scan of active surfaces finds no remaining unqualified assertion that the plateau is
  physically verified, that M0−M2 is a pure rate intervention, that the weighted-variance identity is
  all local information, or that the map result establishes causal attribution.
