# CURRENT — the one current document per topic (R3)

Start here. Each row names the single authoritative document for a topic; everything else is
supporting detail or archived provenance (`docs/archive/`). If two documents disagree, the one
listed here wins.

| topic | current document |
|---|---|
| **Project status / active queue** | [`docs/planning/STATE_OF_TRUTH.md`](planning/STATE_OF_TRUTH.md) — GENERATED from [`docs/status/current.json`](status/current.json) (`python -m puckworks.statusdoc`); curate the JSON, not the Markdown |
| **Onboarding** | [`docs/ONBOARDING.md`](ONBOARDING.md) |
| **Roadmap** | [`docs/ROADMAP.md`](ROADMAP.md) — §3 sequence, §7.1 changelog |
| **Sprint status log** | [`docs/SPRINTS.md`](SPRINTS.md) |
| **CI lanes** | [`docs/CI_LANES.md`](CI_LANES.md) |
| **Strategic plans (historical)** | [`docs/planning/archive/`](planning/archive/) — superseded snapshots (product-first reprioritization, next-step plan); NOT authoritative |
| **Data-use policy** | [`docs/visualizerCoffee_DATA_USE.md`](visualizerCoffee_DATA_USE.md) + memory `visualizer-data-permission` |
| **Sanctioned corpus export contract** | [`docs/analysis/SANCTIONED_EXPORT_SPEC.md`](analysis/SANCTIONED_EXPORT_SPEC.md) |
| **Pressure-atlas pre-analysis spec** | [`docs/analysis/PRESSURE_ATLAS_SPEC.md`](analysis/PRESSURE_ATLAS_SPEC.md) |
| **Paper A manuscript** | [`docs/PAPER_A_DRAFT.md`](PAPER_A_DRAFT.md) — claims verified by `python -m puckworks.paper_a.build verify` |
| **Model/source cards** | [`docs/cards/`](cards/) — one card per model; source of truth for the physics |
| **Release / reproducibility** | `python -m puckworks.paper_a.build` / `.paper3.build`; `docs/reproducibility/` |
| **Superseded reviews / history** | [`docs/archive/`](archive/) — provenance only, NOT current |

## Vocabulary (no bare "DONE")

`proposed` · `implemented` · `CI-verified` · `validated` · `release-ready` · `submitted`.
"Implemented locally" is not "CI-verified". Every completion claim points to evidence at an
exact commit (CI run, generated artifact, validation result, release artifact, or a recorded
human/scientific decision). See `STATE_OF_TRUTH.md`.
