# docs/insights — the Insight Foundry

A bounded research-discovery overlay: it maps what the repository knows, surfaces the tensions
between its parts, and turns them into falsifiable candidate questions — **before** any expensive
publication work starts.

It is not an authority for anything. Every record points back at the registry, a model card, the
manifest, or a generated public claim, and no Foundry output changes an evidence label.

## Read in this order

1. [`INSIGHT_FOUNDRY_DESIGN.md`](INSIGHT_FOUNDRY_DESIGN.md) — what is built, what is deliberately
   not, and every departure from the blueprint with its reason.
2. [`generated/INSIGHT_SNAPSHOT.md`](generated/INSIGHT_SNAPSHOT.md) — the current state in one
   page: counts, lenses, portfolio, existing public claims, build warnings, limitations.
3. [`generated/candidate_portfolio.md`](generated/candidate_portfolio.md) — every candidate, each
   with a question, a cheap screen, a decision rule, and a stop condition.
4. [`generated/tension_atlas.md`](generated/tension_atlas.md) — the rows the candidates came from.
5. [`IF5_HUMAN_TRIAGE_DECISION.md`](IF5_HUMAN_TRIAGE_DECISION.md) — the **human** selection step
   (IF-5): which ten candidates are active, which two are reserves, why each is in the lane it is
   in, and the two rules the decision fixes. Hand-written; not generated, not regenerable.

The blueprint this implements is
[`../PUCKWORKS_INSIGHT_FOUNDRY_CONCEPT_DESIGN_AND_IMPLEMENTATION.md`](../PUCKWORKS_INSIGHT_FOUNDRY_CONCEPT_DESIGN_AND_IMPLEMENTATION.md).

## Commands

```
python -m puckworks.insights build       # build in memory, print the counts
python -m puckworks.insights write       # regenerate every tracked artifact + the ChatGPT pack
python -m puckworks.insights verify      # staleness + hand-edit check (the tests run this)
python -m puckworks.insights card I-007  # materialise a card for a shortlisted candidate
```

`generated/` is **generated**. Do not hand-edit anything in it — `verify` fails on drift and so do
the tests. Curate the authorities (registry, cards, manifest, claims) and regenerate.

`ID_REGISTRY.json` is tracked and **append-only**. `T-0042` and `I-007` are stable identities, not
sort positions: they survive rewording and reordering, and a retired number is never reused, so
IDs are deliberately **not dense**. Never delete or renumber an entry — see
[`INSIGHT_FOUNDRY_DESIGN.md` §1a](INSIGHT_FOUNDRY_DESIGN.md).

## Layout

```
INSIGHT_FOUNDRY_DESIGN.md     design + departures + first-run findings
generated/                    every artifact below is machine-written
  INSIGHT_SNAPSHOT.md         the one-page state
  corpus_map.json             entities + typed, provenance-carrying relations
  tension_atlas.{csv,md}      the tension rows, per lens
  candidate_portfolio.{json,md}  the seeds
  observable_index.csv        model/observable matrix
  evidence_lineage_index.csv  per-dataset lineage, manifest wording verbatim
  calibration_artifact_portability_index.csv
                              calibration components + declared validity + possible
                              downstream components (co-location, NOT established consumers)
  public_claim_inventory.md   what the repo has already published
  snapshot_manifest.json      commit + input/output hashes
  chatgpt_project/            the twelve-file upload pack (gitignored; rebuilt by `write`)
ID_REGISTRY.json              tracked, append-only fingerprint -> stable ID map
candidates/                   cards for SHORTLISTED candidates only (created on demand)
screens/                      one directory per candidate that reaches a cheap screen
chatgpt_project/              Project instructions + chat prompts (hand-written)
```

## Status

The portfolio is still **generated, not scored** — every candidate is `SEED`, nothing has a score,
and no generator ranked anything.

**IF-5 human triage is complete** (2026-08-04): ten active candidates + two reserves, recorded in
[`IF5_HUMAN_TRIAGE_DECISION.md`](IF5_HUMAN_TRIAGE_DECISION.md) and on the twelve cards under
[`candidates/`](candidates/). Selection lives there and only there; the generated portfolio was not
rewritten and does not imply the decision existed at snapshot time.

Wave-1 cheap screens (IF-6) run on **I-040, I-010, I-024** — see [`screens/`](screens/).

**Do not extend this layer before the Wave-1 screens have reported** — no new lens, no new
generator, no scoring of the 91 candidates, no further card materialisation. Building machinery
ahead of the decisive screen is the Paper 1 failure mode this whole design exists to avoid.
