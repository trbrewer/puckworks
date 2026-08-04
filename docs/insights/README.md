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
  closure_portability_index.csv  calibration components + declared validity
  public_claim_inventory.md   what the repo has already published
  snapshot_manifest.json      commit + input/output hashes
  chatgpt_project/            the numbered upload pack
candidates/                   cards for SHORTLISTED candidates only (created on demand)
screens/                      one directory per candidate that reaches a cheap screen
chatgpt_project/              Project instructions + chat prompts (hand-written)
```

## Status

Foundation only. The portfolio has been **generated, not triaged** — every candidate is `SEED`,
nothing is scored, and no component has been executed.

The next step is human triage (blueprint §12 Stage B): read the portfolio, select 10–15, run three
cheap screens. **Do not extend this layer before that has happened.** Building machinery ahead of
the decisive screen is the Paper 1 failure mode this whole design exists to avoid.
