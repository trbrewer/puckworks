# IF-5 — human triage decision

**Status: `IF_5_HUMAN_TRIAGE_COMPLETE`.** This document is the persistent record of the human
selection step the Insight Foundry was built to stop short of. It is a **decision record**, not a
generated artifact: nothing here was produced by `puckworks.insights`, and nothing here may be
regenerated from it.

The generated portfolio remains the commit-pinned seed record. **This decision did not exist at
snapshot generation time** and the portfolio must not be rewritten to imply that it did — every
candidate in `docs/insights/generated/candidate_portfolio.json` is still `SEED`, still unscored,
and still carries `source_commit` `c1b7d79e…`. Selection is recorded here and on the twelve
materialised cards; it is not a score, and no generator produced it.

## 1. Identity of the corpus this decision was taken over

| what | value |
|---|---|
| Foundation merge | `56060e5b589132c496c432fa09e61efea305d5cf` (PR #225) |
| Corpus-source snapshot (`source_commit` on every candidate) | `c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b` |
| Portfolio read | `docs/insights/generated/candidate_portfolio.json`, 91 candidates, all `SEED` |
| Tension atlas read | `docs/insights/generated/tension_atlas.csv`, 170 rows, all `UNREVIEWED` |
| Build warnings at decision time | 32 (see §7) |
| `python -m puckworks.insights verify` at decision time | `OK` — no drift, no hand-edit |

**Card materialisation stamp.** The twelve cards under `docs/insights/candidates/` were written by
`python -m puckworks.insights card I-XXX` while the working tree was at the foundation merge, so
their generated header reads `commit 56060e5b58`. The **content** derives from the `c1b7d79e…`
corpus snapshot; `verify` returns `OK` at both commits, i.e. the snapshot did not drift across the
merge. Both identities are recorded on each card so neither is inferred later.

## 2. The shortlist

Ten active candidates and two reserves — inside the blueprint §12 Stage B band of 10–15.

### Active

| ID | lane | title (generated, verbatim) |
|---|---|---|
| **I-040** | Wave 1 | Which strength is load-bearing where the manifest says 'independent + post_fit + same_campaign'? |
| **I-010** | Wave 1 | Does anything consume pannusch2024.closures, and does it survive outside its declared range? |
| **I-024** | Wave 1 | Can one transport state explain every measured species at once? |
| **I-045** | Wave 2 | Which strength is load-bearing where the manifest says 'independent + verification'? |
| **I-076** | Wave 2 | Do pannusch2024.solver and cameron2020.extraction_bdf actually disagree, or only claim to? |
| **I-013** | candidate-readiness | Does anything consume sourcing2026.g3_pump_characteristic, and does it survive outside its declared range? |
| **I-014** | candidate-readiness | Does anything consume wadsworth2026.grindmap, and does it survive outside its declared range? |
| **I-015** | candidate-readiness | Does anything consume wadsworth2026.permeability, and does it survive outside its declared range? |
| **I-072** | high-risk | Do mo2023_2.swelling and brewer2026.streamtube actually disagree, or only claim to? |
| **I-090** | high-risk | Can first_drip_time discriminate between the models that predict it? |

### Reserves

| ID | title (generated, verbatim) |
|---|---|
| **I-079** | Does the negative result in ANALYSIS_transfer generalise beyond its configuration? |
| **I-077** | Do romancorrochano2017.extraction and cameron2020.extraction_bdf actually disagree, or only claim to? |

## 3. Reason for each lane assignment

### Wave 1 — runs now

Wave 1 is chosen for **decisiveness per unit cost**, not for interest. Each of the three either
needs no model execution at all, or reaches a real held-out prediction with an evidence unit that
is already ingested and already labelled independent.

- **I-040 — Wave 1.** The cheapest decisive screen in the portfolio: a pure source audit with no
  execution. The dataset (`waszkiewicz2025/traces_time_dependent`) is the single most re-used
  time-resolved trace in the repository, and its manifest cell names two strengths at once. If any
  consumer leans on the wrong half, the error propagates into every downstream claim citing it —
  including two published public claims. High blast radius, near-zero cost, and the decision rule
  is answerable from source alone.
- **I-010 — Wave 1.** The one calibration-portability candidate whose producer→consumer path can be
  settled by reading a single import statement, so the screen cannot stall on step 1 the way
  I-013/I-014/I-015 can. It also has a genuinely non-circular scoring unit already in the manifest
  (`angeloni2023`, labelled independent, never in the pannusch fit), which is exactly the resource
  the other portability candidates lack.
- **I-024 — Wave 1.** The portfolio's only `cross_species_inconsistency` candidate — no second
  attempt exists if it is skipped. It is also the one Wave-1 screen that can return
  `NEEDS_NEW_DATA` on a well-understood axis (solute-specific replicate uncertainty), which is a
  useful answer rather than a stall, and it reuses the frozen observation operator that Paper A
  already fixed, so no new analysis convention has to be invented.

### Wave 2 — runs only after Wave 1 reports

- **I-045 — Wave 2.** Method-identical to I-040 (mixed-strength cell, source audit, no execution)
  on a second dataset, `foster2025_2/fig12_14_curves`. Deliberately sequenced *after* I-040 so it
  reuses I-040's audit template rather than inventing a second one — and so that if I-040 retires,
  the same retirement logic is applied to I-045 rather than rediscovered.
- **I-076 — Wave 2.** The most executable of the eighteen `model_disagreement` candidates: both
  `pannusch2024.solver` and `cameron2020.extraction_bdf` are registered runtimes that already run
  against the same angeloni total-solids target, so a matched scenario is reachable without
  inventing a card parameter. Held back from Wave 1 because a matched-scenario comparison is
  **RP-A's** scope (ROADMAP §9), and Wave 1 must not smuggle response-sweep machinery into the
  Foundry.

### Candidate-readiness — blocked on a card/interface prerequisite, not on science

These three are the same lens as I-010 and were shortlisted for the same reason, but their step 1
(establish the producer-output→consumer-input path) cannot be answered from the current cards. The
lane records that the missing edge **is** the finding, and that the prerequisite is a card repair,
not an experiment.

- **I-013 — candidate-readiness.** `sourcing2026.g3_pump_characteristic` carries
  `UNRESOLVED_CARD` (no `docs/cards/sourcing2026*.md`), and `docs/cards/g3_pump_characteristic.md`
  is missing *Governing equations*. The named same-stage neighbour is `foster2025.machine_mode`,
  whose own card is missing every template section. Prerequisite: a resolvable card with an
  Interface mapping on at least one side.
- **I-014 — candidate-readiness.** `docs/cards/wadsworth2026.md` is missing *Interface mapping*
  (among others), so `wadsworth2026.grindmap`'s consumed-input edge cannot be traced from the card.
  Prerequisite: the Interface mapping section.
- **I-015 — candidate-readiness.** The sharpest case, and the reason the lane exists: the Foundry
  build itself emits `NO_INTERFACE_MAPPING: docs/cards/wadsworth2026.md (component
  wadsworth2026.permeability) — no observable edges inferred`. The corpus map has already recorded
  that this artifact has no traceable consumer edge. Prerequisite: same card repair as I-014.

### High-risk — high value, high chance of a null or a data block

- **I-072 — high-risk.** `mo2023_2.swelling` and `brewer2026.streamtube` are a card-declared
  competitor pair, but the generated row records only that they are **comparable**, and the
  candidate's own strongest alternative — "the observable is named the same but defined
  differently" — is the likely outcome, since one produces a porosity/deformation response and the
  other a flow-distribution response. `brewer2026.streamtube` also carries `UNRESOLVED_CARD`.
  Kept active because a confirmed convention mismatch between two registered components is itself
  a reportable result; flagged high-risk because it will probably retire on
  "answer different questions", and settling it properly is RP-A execution.
- **I-090 — high-risk.** The cheapest *decisive* screen the corpus could offer if it works —
  discrimination on an already-measured observable with no new experiment. But its own
  INCONCLUSIVE clause is the likely one: `de1_fixtureA` is a single fixture (its manifest row also
  names an unresolvable `source_card`, `(registry [RS])`), and without replicate spread no
  within-model uncertainty band can be drawn. Expect `NEEDS_NEW_DATA` naming a specific
  measurement; that is a useful output, but it is not a result.

## 4. I-079 → reserve, I-045 promoted

**I-079 was moved to reserve.** Two reasons, both about scope rather than merit:

1. **It is not a cheap screen.** Its cheap test is "re-run the recorded analysis under a second
   configuration". For `ANALYSIS_transfer` that work has largely already been done and archived —
   `angeloni_bracket.geometry_sensitivity_transfer`, `flow_map_sensitivity_transfer`,
   `endpoint_mass_sensitivity`, `loco_cv_refit` and `numerical_convergence` are exactly
   second-configuration runs, and they are slow-lane, not CI. A cheap screen here would mostly
   re-read an existing result, which is a literature review of our own repository, not a screen.
2. **It lands on a governed claim surface.** `ANALYSIS_transfer` is the source of `PAPER_A_DRAFT`,
   and the Paper 1 assurance layer is FROZEN (CLAUDE.md). A candidate whose SURVIVE condition is
   "the verdict reverses or weakens materially" cannot be run as a one-day screen without touching
   a reader-facing claim surface. It needs the deep-screen lane and a human who is prepared to
   open the claim ledger.

Reserve status is not retirement: I-079 is **not** recorded in `RETIRED_CANDIDATES.md`, keeps its
stable ID, and is reopened by the deep-screen lane (IF-7) or by any Wave-1/Wave-2 result that
bears on the transfer verdict.

**I-045 was promoted into the freed active slot** because it is the strict opposite on both counts:
it needs no execution at all, and a manifest-cell attribution cannot reach a reader-facing surface
without a separate human step. It also raises the value of I-040 by turning a single audit into a
two-point method check.

**I-077 is the second reserve** because it is dominated by I-076. Same lens, same method, weaker
pairing: `romancorrochano2017.extraction` carries `sign_or_compatibility` and
`cameron2020.extraction_bdf` carries `code_verification`, so neither side's evidence is strong
enough for an observed difference to be attributable to physics rather than to either
component's own unvalidated region. If I-076 produces a usable matched-scenario protocol, I-077
becomes cheap and can be promoted; on its own it is not worth an active slot.

## 5. Groupings, at a glance

```
Wave 1 (executing now)      I-040   I-010   I-024
Wave 2 (after Wave 1)       I-045   I-076
Candidate-readiness         I-013   I-014   I-015     (blocked on card/interface repair)
High-risk                   I-072   I-090             (expect RETIRE / NEEDS_NEW_DATA)
Reserve                     I-079   I-077             (not retired; no reopen condition needed)
```

## 6. Standing rules this decision fixes

**Rule 1 — only cheap-screen survivors receive deep screening or external novelty research.**
A candidate that has not been through its cheap screen and returned `SURVIVE` gets no deep screen
(IF-7), no external novelty search, no literature sweep, and no manuscript work. This is the
blueprint §13.4 sequencing and it is the Paper 1 lesson: novelty research is expensive, it is
motivating, and it is the single easiest way to spend a month on a candidate that a one-day screen
would have retired. The novelty search terms already written on each card are **inert** until that
`SURVIVE` exists.

**Rule 2 — no additional Foundry infrastructure precedes the Wave-1 results.**
`puckworks/insights/` and `docs/insights/generated/` are closed for extension until all three
Wave-1 screens have reported. No new lens, no new generator, no scoring of the 91-candidate
portfolio, no new candidates, no schema growth, and no materialisation of the other 79 cards. A
screen may add its own analysis script and its own result bundle under
`docs/insights/screens/I-XXX/`; that is screen output, not layer infrastructure. The three
`DEFERRED_LENSES` stay deferred and are unblocked by RP-A, not here. Machinery built ahead of the
decisive screen is the failure mode the whole design exists to avoid.

## 7. Corpus warnings — triaged, not repaired

The build emits **32 warnings**. They were checked one by one against the three Wave-1 candidates.
**None is load-bearing for I-040, I-010 or I-024**, so none is repaired in this work:

- I-040 consumes `waszkiewicz2025/traces_time_dependent`; `docs/cards/waszkiewicz2025.md` resolves,
  has no template deviation, and the manifest row's `source_card` resolves. No warning touches it.
- I-010 consumes `pannusch2024.closures` / `.solver`; `docs/cards/pannusch2024.md` resolves with no
  template deviation. The alternative closures it substitutes are taken from the **registered
  component** `romancorrochano2017.extraction` (card `romancorrochano2017_extraction.md`, which
  resolves), *not* from the `romancorrochano2017/*` manifest rows that carry warnings 2–11 — so
  those warnings are outside the screen's evidence path by construction.
- I-024 consumes `angeloni2023/*`; `docs/cards/angeloni2023.md` resolves with no template
  deviation. No warning touches it.

All 32 are therefore **deferred**, and recorded as deferred in each screen's `README.md`. Ten of
them are, however, the *readiness prerequisite* for the candidate-readiness lane (§3): warnings
12, 18, 25, 29, 32 and manifest row 27's unresolved `source_card` are precisely what blocks I-013,
I-014, I-015 and I-090. Those are repaired when that lane is worked, by a human, in a commit whose
subject is the card repair — not silently inside a screen.

Deferred warning classes, for the record:

| class | count | rows / components |
|---|---|---|
| `MANIFEST_SOURCE_CARD_UNRESOLVED` | 11 | row 27 (`de1_fixtureA`); rows 33–41, 48 (`romancorrochano2017/*` → the paper stem splits into `_extraction` / `_permeability` cards) |
| `NO_INTERFACE_MAPPING` | 1 | `wadsworth2026.permeability` |
| `TEMPLATE_DEVIATION` | 13 | cameron2020, foster2025, g10_liquor_rheology, g1_glassbead_analog, g1_retention_search_target, g3_pump_characteristic, khomyakov2020, lateral_coupling_feasibility, liang2021_AUDIT, moroney2019_AUDIT, schmieder2023_AUDIT, visualizer_coffee, wadsworth2026 |
| `UNRESOLVED_CARD` | 7 | `brewer2026.{lb_reference,lb_taichi,pack_generator,streamtube}`; `sourcing2026.{g10_liquor_rheology,g1_glassbead_analog,g3_pump_characteristic}` |

## 8. What this decision does *not* do

- It does not score anything. No candidate has a score; `scores` stays `{}` on all 91.
- It does not promote any candidate above `SEED` in the generated portfolio. The twelve cards
  record `SHORTLISTED` in their own human block; the generated record is untouched.
- It does not change, promote or restate any evidence label, public-claim badge, validation rung or
  model verdict. The Foundry is not an authority and neither is this file.
- It does not retire anything. `RETIRED_CANDIDATES.md` is unchanged; a retirement is recorded there
  only by a screen that ran.
- It does not touch `ID_REGISTRY.json`. The registry is append-only and no new identity was minted.

## 9. Pointers

- Cards for the twelve: `docs/insights/candidates/I-0*.md`
- Wave-1 screen bundles: `docs/insights/screens/{I-040,I-010,I-024}/`
- Bundle shape and the six required contents: `docs/insights/screens/README.md`
- Design and departures: `docs/insights/INSIGHT_FOUNDRY_DESIGN.md`
- Standing constraint and the RP-A boundary: `docs/ROADMAP.md` §9
- Sprint status: `docs/SPRINTS.md` "Insight Foundry (IF)"
