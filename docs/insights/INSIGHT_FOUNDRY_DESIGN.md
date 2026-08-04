# Insight Foundry — design (Phase 0 acceptance)

Blueprint: [`docs/PUCKWORKS_INSIGHT_FOUNDRY_CONCEPT_DESIGN_AND_IMPLEMENTATION.md`](../PUCKWORKS_INSIGHT_FOUNDRY_CONCEPT_DESIGN_AND_IMPLEMENTATION.md).
This file records what the **foundation** actually implements, what it deliberately does not, and
where it departs from the blueprint and why. It is the Phase 0 deliverable named in blueprint §16.

The Foundry is a bounded research-discovery overlay. Its job is to make the corpus's internal
disagreements findable and falsifiable, cheaply, **before** anything expensive starts.

---

## 1. What was built

| Blueprint phase | Status | Where |
|---|---|---|
| Phase 0 — design acceptance | done | this file |
| Phase 1 — corpus map | done | `puckworks/insights/{extract,corpus_map}.py` |
| Phase 2 — tension atlas | done (10 of 13 lenses) | `puckworks/insights/tension_atlas.py` |
| Phase 3 — candidate generation | done (seeds only, no triage) | `puckworks/insights/candidates.py` |
| Phase 4 — ChatGPT Project | pack generated; **project creation is a human step** | `docs/insights/chatgpt_project/` |
| Phase 5+ — cheap screens, deep screens, outputs | **not started, by design** | — |

Counts are generated, never hand-maintained here (blueprint §4.3). For the live numbers read
[`generated/INSIGHT_SNAPSHOT.md`](generated/INSIGHT_SNAPSHOT.md), or run:

```
python -m puckworks.insights build
```

## 1a. Stable identity — `T-0042` means one thing forever

`T-` and `I-` numbers get quoted in decision records, screen bundles, retirement rows and chat
threads. The first implementation derived them from **sort position**, so adding one early-sorting
row would silently renumber everything after it and every persistent reference would start
pointing at the wrong record. That is fixed.

Identity is now a **fingerprint** over the few fields that say what a record *is*
(`puckworks/insights/ids.py`), recorded in the tracked, append-only
[`ID_REGISTRY.json`](ID_REGISTRY.json):

| | fingerprint |
|---|---|
| tension | schema version · lens · difference type · sorted entity ids · canonical discriminator |
| candidate | schema version · lens · difference type · canonical grouping key |

Three consequences, each test-bound:

- **Wording is free.** Rewriting a row's summary, evidence basis or prose discriminator does not
  mint a new ID. Row prose *should* improve as the corpus is understood better, and improving it
  must not cost a renumber. This is why `Tension.canonical_discriminator` (a slug) exists
  separately from `candidate_discriminator` (prose).
- **Numbers are never reused.** A record that leaves the corpus keeps its registry entry. If it
  returns it gets its original number back; its number is never handed to a different record. A
  stale reference therefore resolves to what it always meant, or to nothing — never to something
  else. IDs are consequently **not dense**, and gaps are correct.
- **Identity tracks substance.** A row whose entity set changes is a different row: it gets a new
  ID and the old one retires. That is deliberate — silently re-pointing an existing ID at a
  materially different record is the failure the registry exists to prevent.

The registry was **seeded from the assignments at head `e8054b3`**, mapping each pre-existing ID
onto its post-rename fingerprint, so the two family renames below cost no renumbering: all 170
tension IDs and all 89 candidate IDs survived with zero minted.

## 2. The source-of-truth rule

The Foundry is **never** an authority. Every entity carries the path of the authority it was read
from, and every evidence label is copied byte-identical (`schema.assert_verbatim`). Derived tags
live in separate fields beside the original wording, never in place of it.

This is the mechanical form of CLAUDE.md rule 4. It matters most in one place: the manifest's
`validation_strength` column is free prose, and several cells name **more than one** strength —
`"independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)"` is both. The derived
tags are therefore additive and carry `mixed_strength` when a cell mixes; a consumer that keeps
only the stronger half has promoted the dataset, and the atlas raises a row about exactly that.

## 3. Deliberate departures from the blueprint

**No wall-clock timestamp in tracked artifacts.** The blueprint's snapshot manifest carries
`generated_at` (§8.6). A timestamp makes every regeneration a diff, which makes hand-editing
undetectable — defeating the staleness control §19.7 wanted it for. Commit sha plus a sha256 per
input identifies a snapshot strictly better: it changes when and only when the inputs change.
`--stamp-time` is available for untracked human-facing exports.

**`verify` distinguishes STALE from DRIFT.** A naive regenerate-and-diff check would fail on every
commit, because the artifacts record the commit they were generated from and HEAD moves the
moment they are committed. So `verify` first compares input hashes against the manifest (STALE →
regenerate), and only then regenerates *at the manifest's stored commit* to compare bytes (DRIFT →
someone hand-edited a generated file).

**One relation type added: `CARD_NAMES_IN_OVERLAPS`.** The blueprint offers only `COMPETES_WITH`
and `COMPLEMENTS` for a card's `Overlaps and conflicts` section. But cards routinely name a
neighbour without ruling on it, and picking one of those two would be the extractor inventing a
scientific verdict. The colourless edge records the fact; the typed edges are emitted only when
the card's own sentence says so.

**Two families were renamed because their wording outran the metadata.** Both renames assert less
than the originals did, and both are guarded by tests:

- `closure_portability` / `closure_producer` → **`calibration_artifact_portability` /
  `calibration_artifact_producer`**. `execution_role == "calibration"` means a component supplies
  parameters offline. That covers closures, but also lookup tables, geometry generators, reference
  datasets and verification twins — calling them all closures asserts a functional form the
  registry never stated. Relatedly, a same-stage runtime component is a **possible downstream**
  component, not an established consumer: nothing traced an output to an input. So
  `cheap_test_possible` is `UNKNOWN` rather than `YES` wherever a same-stage neighbour exists, and
  **step 1 of the screen is to establish the path**; the swap experiment is step 2 and only runs
  if step 1 succeeds. The index column is `possible_downstream_same_stage`, beside a
  `consuming_path_established` column that reads `no` on every row by construction.
  The word *closure* survives only where an authority wrote it — a component name
  (`maille2024.phi_closure`, `pannusch2024.closures`) or a verbatim `valid_range` — because
  rewriting those would be the label-tampering this layer forbids.
- `same_source_variant_pair` → **`same_source_pair_requires_composition_audit`**. Sharing a source
  prefix does not make two components a base/superset pair: `maille2024.phi_closure` and
  `maille2024.two_regime` are two calibration roles on different stages, and `mo2023_2.swelling`
  and `mo2023_2.coupled_bed` are a reduced and a depth-resolved model the repository keeps side by
  side on purpose. A base-versus-base-plus-mechanism comparison is meaningless for those. The row
  now asks the **classification** question first — base/superset, alternative reductions, or
  independent — and only a confirmed base/superset pair proceeds to the held-out comparison. The
  separately evidence-backed PV-05 generalisation candidate is untouched and stays its own row.

**Candidate cards are materialised on demand, not in bulk.** The blueprint's `candidates/`
directory implies a file per candidate. Writing all of them as tracked files would be the
governance re-expansion §19.6 warns against, for candidates nobody has read yet. The portfolio
(JSON + Markdown) holds every seed; `python -m puckworks.insights card I-007` writes a card when a
person decides to work one.

**Portfolio size is above the blueprint's band.** §3.3 targets 50–80 generated seeds; the
generator produces more than that (see the snapshot for the live count). Grouping was already
coarsened once — mixed-strength lineage rows are grouped by *which strengths a cell mixes* rather
than by paper, which collapsed 22 near-identical candidates into a handful of sharper ones.
Coarsening further would merge distinct evidence units into vaguer questions, which is the
opposite of the §19.1 control ("one falsifiable sentence, one cheap test, one stop condition").
The count is reported rather than trimmed to fit; human triage (§12 Stage B) is the intended
filter, and it has not run.

## 4. Lenses not implemented, and why

Three of the blueprint's thirteen lenses are absent **by decision**, and the generated atlas says
so rather than emitting weak rows to look complete. All three need matched-scenario EXECUTION of
the components:

- **B observational equivalence** — a card read cannot establish that two models agree
  numerically.
- **F regime transition** — cards declare validity in prose, not comparable dimensionless
  thresholds.
- **G hidden discriminator, ranking half** — `between-model separation / within-model uncertainty`
  is an execution quantity. The *availability* half (which observable several models predict, and
  whether data exists) is implemented.

That execution programme already exists and is specified: **RP-A** in ROADMAP §9, with
`docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md`. The Foundry defers to it rather than growing a
second, weaker copy of it. The atlas's `model_disagreement` rows record **comparability** — the
precondition RP-A needs — and say in the row itself that agreement is not established.

## 5. Relationship to existing systems

The Foundry consumes; it does not replace.

| Existing authority | How the Foundry uses it |
|---|---|
| `puckworks/registry.py` | live component identity, typed axes, gates, validity ranges |
| `docs/cards/` | mechanisms, interfaces, and the `Overlaps and conflicts` section |
| `puckworks/data/MANIFEST.csv` | dataset lineage, verbatim strength wording, caveats |
| `docs/public/generated/claims.json` | the duplicate-proposal guard (§19.3) |
| allowlisted `docs/ANALYSIS_*.md`, `docs/P3_hypotheses.md` | standing verdicts, negative-result pointers |
| ROADMAP §9 RP-A | the execution layer the disagreement lenses defer to |
| `tools/research_radar.py` | external novelty search, **after** internal survival only |

Note on the word *corpus*: in `puckworks/data/corpus_export.py` it means the visualizer.coffee
**shot** corpus. In the Foundry it means the **knowledge** corpus — models, cards, datasets,
claims, analyses. The two never touch.

## 6. What is forbidden here

Carried from the blueprint's §2.3 non-goals and CLAUDE.md:

- No evidence label, badge, or validation rung may be changed, promoted, or restated.
- No lens may write a scientific verdict; `human_status` starts `UNREVIEWED`.
- No candidate may be generated above `SEED`, and no generator may score its own output.
- `llm_suggested` relations may never drive automated scoring (`schema.scoring_admissible`).
  Nothing in the foundation is LLM-suggested; the guard exists so the first scorer cannot quietly
  consume a suggestion as evidence.
- No manuscript work before a candidate survives a cheap screen. **Scientific viability before
  publication assurance** (blueprint §1.3) — this is the Paper 1 lesson, and the reason the
  Paper 1 assurance layer is frozen (CLAUDE.md).
- No protocol freeze, claim ledger, or merge ceremony at seed stage (§18.3).

## 7. What the foundation found on its first run

The build warnings are corpus findings, not build failures — surfacing them is the point. The live
list is in the snapshot; the recurring classes are:

- **Registered components with no model card of their own** — four `brewer2026.*` project models
  and three `sourcing2026.*` aggregators (the latter legitimately span several source cards).
  CLAUDE.md rule 1 says the card comes first.
- **Manifest `source_card` cells that resolve to no single card** — including a family of rows
  naming `romancorrochano2017`, which has two cards (`_extraction`, `_permeability`). The
  extractor refuses to guess between them; that lineage cannot currently be followed mechanically.
- **Cards missing template sections.** This one bit the Foundry itself, and has since been
  **repaired**. `first_drip_time` originally showed **zero** predicting models — not because
  nothing models first drip, but because `foster2025.md`, the sharp-front infiltration card whose
  headline result *is* a predicted first-drip time, had no `Interface mapping` section for the
  extractor to read. The blueprint's flagship candidate was therefore invisible to the matrix.
  A narrowly scoped `Interface mapping` was added to that card (only inputs and outputs the
  source, card and implementation already support, and only ones common to both components the
  card serves). The result, and the reason this is worth recording rather than quietly fixing:

  | | before | after |
  |---|---|---|
  | `first_drip_time` predicting models | 0 | 2 (`foster2025.infiltration`, `foster2025.machine_mode`) |
  | `first_drip_time` | `measured_but_unmodelled` | **`discriminator_with_data`** — a screen runnable on data already in the manifest |
  | `wetting_front` | invisible | `predicted_but_unmeasured` — the first Lens L row the corpus has produced |

  Four rows retired (`T-0048`, `T-0049` — the two blind-spot rows; `T-0055` — the
  measured-but-unmodelled row; `T-0170` — the scale-mismatch row, whose entity set changed) and
  four minted (`T-0171`–`T-0174`). **No surviving ID was renumbered**, which is the stable-ID
  registry doing the job it was added for. Other cards' template deviations are still reported and
  were deliberately left alone — this was a targeted repair, not a card cleanup.

## 8. Next step

**Human triage** (blueprint §12 Stage B): read the portfolio, select 10–15, then run three cheap
screens. Nothing in this layer should be extended before that has happened — the blueprint's own
§1.3 lesson is that machinery built ahead of the decisive screen is the failure mode.
