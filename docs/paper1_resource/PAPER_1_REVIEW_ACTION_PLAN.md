# Paper 1 / Paper A — review action tracker

**Source review:** [`PAPER_1_DETAILED_REVIEW-20260724.md`](PAPER_1_DETAILED_REVIEW-20260724.md) (external desk review, 24 Jul 2026; verdict **major revision**).
**Reviewed manuscript:** `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` @ `85af247` (still current on `main`).
**Authoritative working draft:** `docs/PAPER_A_DRAFT.md`.

This tracker triages every review recommendation by **priority** (review §9) and **owner-type**, with a
**verification** column recording what was checked against the *current* repo (not the pinned commit). It
does **not** itself change the manuscript — per the review's own top recommendation (MC1), manuscript edits
must flow from a single chosen canonical source, which is an author decision (see "Gating decision" below).

Owner-types:
- **[mech]** repo-mechanical — unambiguous, no scientific judgment; safe to execute once the canonical source is chosen.
- **[author]** author decision — scientific/editorial voice or claim framing.
- **[analysis]** needs new computation (a rerun, a derivation, a solver-backed audit).
- **[external]** needs an external artifact (indexed literature search, new measurement, DOI/release).

## Verification of the review's load-bearing claims (all CONFIRMED on current `main`)

| Claim (review) | Check | Result |
|---|---|---|
| Version drift: JFE conversion carries stale wording the working draft already corrected (MC1) | grep both files for the 5 stale + 4 corrected phrases | **CONFIRMED** — JFE has all 5 (`identifiability ratio`, `nested reduced-model ladder`, `matched 40 g`, `essentially nothing`, `frozen-parameter transfer`); DRAFT has all 4 corrections |
| Methods subsections mis-numbered `2.x` under Section 3 (MC3, §4.4) | grep JFE headings | **CONFIRMED** — `### 2.1 Model` … `### 2.6 Evidence vocabulary` |
| Table 7 inventory uses an undefended `1 kg = 1 L` mass→volume basis (MC5) | read `docs/cards/angeloni2023.md` | **CONFIRMED** — card L53: `mg/L (=mg/kg, 1 kg=1 L assumed)` |
| Editorial conversion note visible in the manuscript (MC13, L9) | read JFE L9 | **CONFIRMED** — present (and self-describes as "remove before submission") |
| Repository scaffolding in prose (`Strength:` labels, code-object names) (MC11/MC13) | grep JFE | **CONFIRMED** — `Strength:` ×4; `c_s0` ×14, `rate_scale` ×4, `pannusch2024` ×7 |
| Declaration/reference placeholders remain (MC13, §4.12) | read JFE tail | **CONFIRMED** — `[Insert … statement.]` for CRediT/funding/COI/AI; References stub |
| No manuscript-consistency / drift gate exists | search tools+tests | **CONFIRMED** — only `readme_governance`; nothing guards the two Paper-A files |

## Status — 2026-07-24 mechanical batch (canonical = `PAPER_A_DRAFT.md`)

Author decisions taken: **canonical source = `docs/PAPER_A_DRAFT.md`**; execute the **[mech]** batch.
Landed on the conversion `docs/submission/PAPER_A_JFE_MANUSCRIPT.md` (no scientific rewording — every
change is either a verbatim port of the canonical draft's already-corrected wording or a numbering/
scaffolding cleanup):

- **P0-1 direction set** — `PAPER_A_DRAFT.md` is canonical; the JFE file is a synced view. ✅
- **P0-2 drift guard built** — `tools/paper_a_consistency.py` (5 banned + 5 required phrase pairs, with a
  config-sanity check against the canonical draft) + `tests/test_paper_a_consistency.py` (5 tests). It runs
  in the **quick-pr pytest lane**, so regression is caught at PR time without a workflow change. ✅
- **P0-3 language sync** — all 5 retired phrases replaced with the canonical draft's wording: `identifiability
  ratio`→`profile range ratio`; the Table 7 `collapses…narrow band`/`interior, unique`→`conditional
  one-dimensional intersection band` (+ "not a confidence interval", "illustrative ±10 % perturbation");
  `frozen-parameter transfer` heading→`cross-grind endpoint prediction versus a level-only baseline`;
  `matched 40 g cups`→`40 mL matched-volume proxies…`; `nested reduced-model ladder`/`explains essentially
  nothing`→`in-sample comparator ladder` (non-nested, descriptive). ✅
- **P0-8 scaffolding (partial)** — removed the L9 editorial conversion note, converted the 4 inline `Strength:`
  result labels to plain prose (content preserved, per MC11's "integrate into prose"), and removed the
  Data/code-availability `Strength tags`/`not in CI`/change-log scaffolding. ✅ (partial — see deferred)
- **P0-9 numbering (partial)** — Methods subsections `2.1`–`2.6`→`3.1`–`3.6`. ✅ (partial — see deferred)

### P0-4 Table 7 dimensional audit — DONE (2026-07-24, demoted to qualitative)

`docs/paper1_resource/PAPER_A_TABLE7_UNITS_AUDIT.md`: the intersection equates two `mg mL⁻¹` values
whose physical volume bases are not shown to match — pannusch2024's `c_s0` (10.80) is **fitted** with
an unanchored basis; Angeloni Table 7 (12.54) is a dry `mg kg⁻¹` assay reinterpreted via an undefended
`1 kg = 1 L`. The assay alone spans **~4.8–16.3 mg mL⁻¹ (~3.4×)** across defensible bases — ≫ the ±10 %
propagated — so `rate ≈ 0.95 [0.60–1.76]` is not secure. **Demoted to qualitative** in the canonical
draft + synced JFE; the guard gained a required anti-regression phrase (`qualitative, not a quantitative
rate constraint`); a unit-basis caveat added to `table7_rate_constraint`'s docstring (no computation
change). The valid qualitative claim (an orthogonal inventory of the same order *could* break the
compensation) is preserved. To re-quantify later: derive pannusch's `c_s0` basis + map the assay to it
with a measured coffee density + propagated uncertainty (owed, out of scope). ✅

### Deliberately deferred (needs author judgment or new analysis — NOT mechanical)

- **In-text §-cross-reference remap** (part of P0-9): the `(§4)/(§5)/(§6)/(§3–§5)` in-text refs are still on
  the working-draft numbering. Remapping them is entangled with the fact that the canonical draft and the
  conversion have **different top-level section structures**, so it needs the author's intended target
  mapping — left for the author pass, not guessed.
- **Evidence-vocabulary → study-design table** (MC11 / P1-7): the inline labels were de-tagged, but relocating
  the §3.6 evidence taxonomy and the Result-1 table's `strength` column into one study-design table is [author].
- **Declaration/reference/author placeholders** (`[insert]`, `[Insert … statement.]`, References stub): left in
  place — these are needed fields to be **filled** (P0-7 [external], P2-4 [author]), not deleted.
- **[analysis]** P0-5 uncertainty reruns (P0-4 Table 7 units audit is now done, above) and all **[author]/[external]** items below.

## Gating decision (author) — RESOLVED: canonical = `PAPER_A_DRAFT.md` (mechanical stream above)

*(retained for provenance)*

MC1 requires choosing **one canonical Paper-A source** and regenerating the venue conversion from it, then
adding a check that fails on divergence. Until that is chosen, patching `PAPER_A_JFE_MANUSCRIPT.md` directly
would perpetuate the two-files-drift the review flags. Options: (a) **`PAPER_A_DRAFT.md` canonical**, JFE is a
generated view; (b) **JFE canonical**, retire the working draft; (c) merge into one file. Recommended: (a).

## P0 — submission-blocking (review §9)

| # | Item | Owner | Notes |
|---|---|---|---|
| P0-1 | Choose canonical source; regenerate JFE from it; **stop editing both** | **[author]** → then [mech] | The gating decision above. Everything below assumes it is made. |
| P0-2 | Add an automated **drift guard** — fail when the canonical draft and the venue conversion disagree on designated load-bearing phrases / result numbers / evidence labels | **[mech]** | Repo-idiomatic (cf. `readme_governance`). Design ready to build once P0-1 picks a direction; proposed as a `tools/paper_a_consistency.py` + test. |
| P0-3 | Port all corrected evidence language DRAFT→JFE (profile range ratio; conditional 1-D intersection band; in-sample comparator ladder; 40 mL proxy; drop "essentially nothing"/"identifiability ratio"/"frozen-parameter transfer") | **[mech]** | Corrected wording already exists in DRAFT — a sync, not new science. Do as one complete pass under P0-1, not piecemeal. |
| P0-4 | Resolve the **Table 7 dimensional conversion** (units table + first-principles conversion eq + uncertainty), or demote Table 7 to qualitative and remove the numeric rate intersection (~0.95) | **[analysis]** | Needs the model's `c_s0` volume basis + bed geometry/porosity; solver-backed. The `1 kg = 1 L` assumption is in the Angeloni card and must be defended or dropped. |
| P0-5 | **Uncertainty analysis**: uncertainty-weighted + relative/log + robust reruns of the principal profile; paired **clustered** bootstrap for the model-vs-null difference; refit-inside-resampling for LOCO | **[analysis]** | Review calls this a submission gate, not a limitation. Angeloni RSDs 0.3–19.7% already noted; weighted reruns are "outstanding". |
| P0-6 | Add **standalone** model + observation-operator equations (PDE/reduced balances, BCs, cup & fraction operators, precise `c_s0`/`rate_scale` definitions, fitting groups, objectives) | **[author]**+[analysis] | MC3 — Methods currently not reconstructable without repo object names. |
| P0-7 | Complete the **indexed novelty search** (Scopus/WoS: databases, queries, dates, screening) + final reference list | **[external]** | Review: don't rest novelty on "we did not find". References section is a stub. |
| P0-8 | Remove review IDs, prior-draft history, bug notes, `delivered/owed` language, `Strength:` tags, code names, L9 editorial note, placeholders | **[mech]** | Verified present. Do under P0-1 on the canonical file. |
| P0-9 | Repair Section numbering (`2.x`→`3.x`) and every stale cross-reference (§3–§6) | **[mech]** | Verified: `### 2.1`–`### 2.6` under Methods. |

## P1 — scientific presentation (review §9) — mostly [author]

| # | Item | Owner |
|---|---|---|
| P1-1 | Adopt a descriptive espresso title (review's rec: "Separating Extractable Content from Extraction Rate in Espresso Models…") | **[author]** |
| P1-2 | Rewrite the abstract around amount-vs-rate (draft provided, review §8); use the **0.4 pp** null result as primary | **[author]** |
| P1-3 | Reorganize around the **observation operator**; add the local rate-sensitivity (Gram/determinant) design diagnostic (MC2) | **[author]**+[analysis] |
| P1-4 | Reframe Angeloni C/F as a **within-campaign cross-grind holdout under target-derived hydraulics** (MC6) | **[author]** |
| P1-5 | Rework the Waszkiewicz external analysis (12-vs-14 fractions; replicate handling; near-zero-TDS MAPE; time alignment; 27% min; algebraic one-cup) (MC9) | **[author]**+[analysis] |
| P1-6 | Reduce main figures to 4–5; move Figs 5/7/8 to supplement; fix legibility (MC14, §6) | **[author]** |
| P1-7 | Add dataset-role, adapter/assumption, and principal-results tables (MC11/MC14) | **[author]** |

## P2 — editorial polish & reproducibility (review §9)

| # | Item | Owner |
|---|---|---|
| P2-1 | Standardize terminology (extractable content/inventory; rate multiplier; extraction rate); define O/C/F, macro/pooled-MAPE, "percentage points" at first use | **[author]** |
| P2-2 | Single spelling convention | **[mech]** |
| P2-3 | Permanent **tagged release + DOI + pinned environment**; journal-style data/code availability statement; reproducibility supplement | **[external]** (ties to the Paper 3 §11a release prerequisite) |
| P2-4 | Complete title-page & declaration material (CRediT/funding/COI/AI) | **[author]** |

## Strengths to preserve (review §10) — do not "fix"

Level-only baseline; the four-properties distinction (localization / endpoint accuracy / prediction stability /
incremental skill); matched-observation-window lesson; right-censoring disclosure; named-solute vs TDS/total-solids
separation; candour on the shallow external minimum; provenance discipline (→ supplement); **the negative result**.

## Recommended execution order

1. **[author]** P0-1 canonical-source decision (unblocks the mechanical stream).
2. **[mech]** batch: P0-9 numbering, P0-8 scaffolding removal, P0-3 language sync, P0-2 drift guard — one clean pass on the canonical file, gates green in between.
3. **[analysis]** P0-4 Table 7 audit, P0-5 uncertainty reruns (each a separate scientific PR; no evidence-label upgrade without a ROADMAP §7.1 entry).
4. **[author/external]** P0-6 standalone Methods, P0-7 novelty search + references, then the P1/P2 presentation pass.

Nothing here upgrades an evidence claim; the review's whole thrust is to *down*-scope overclaims to what the design supports, which matches repository discipline.
