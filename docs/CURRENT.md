# CURRENT — the one current document per topic (R3)

Start here. Each row names the single authoritative document for a topic; everything else is
supporting detail or archived provenance (`docs/archive/`). If two documents disagree, the one
listed here wins.

| topic | current document |
|---|---|
| **Project status / active queue** | [`docs/planning/STATE_OF_TRUTH.md`](planning/STATE_OF_TRUTH.md) — GENERATED from [`docs/status/current.json`](status/current.json) (`python -m puckworks.statusdoc`); curate the JSON, not the Markdown |
| **Supported public API + stability policy** | [`docs/API.md`](API.md) — `puckworks.__all__`; what semver covers; internal vs public |
| **Public-experience / homepage policy** | [`docs/PUBLIC_EXPERIENCE.md`](PUBLIC_EXPERIENCE.md) — the design + review authority behind `README.md` (issue #41) |
| **Accessibility / platform-support policy** | [`docs/ACCESSIBILITY.md`](ACCESSIBILITY.md) — one-click paths + one-wheel platform matrix (issue #43) |
| **Public-release display metadata** | [`docs/status/public_release.json`](status/public_release.json) — compact machine-readable projection of release facts for README/Colab/public-access tooling, validated by `tools/release_record.py`. **NOT** a project-status authority (that stays `current.json` → STATE_OF_TRUTH.md) and **NOT** the historical release record (that stays `docs/reproducibility/RELEASE_VERIFICATION_v0.2.0.md`) |
| **Onboarding** | [`docs/ONBOARDING.md`](ONBOARDING.md) |
| **Roadmap** | [`docs/ROADMAP.md`](ROADMAP.md) — §3 sequence, §7.1 changelog |
| **Current product implementation plan** | [`docs/planning/EXPLANATION_BUNDLE_VERTICAL_SLICE.md`](planning/EXPLANATION_BUNDLE_VERTICAL_SLICE.md) — the scoped evidence-aware explanation-bundle slice; the archived `PRODUCT_FIRST_REPRIORITIZATION.md` is historical design input, NOT authoritative |
| **Sprint status log** | [`docs/SPRINTS.md`](SPRINTS.md) |
| **CI lanes** | [`docs/CI_LANES.md`](CI_LANES.md) |
| **Strategic plans (historical)** | [`docs/planning/archive/`](planning/archive/) — superseded snapshots (product-first reprioritization, next-step plan); NOT authoritative |
| **Literature / venue / collaboration discovery** | [`docs/RESEARCH_RADAR.md`](RESEARCH_RADAR.md) — governs discovery + triage (issue #42). Radar output is **candidate metadata, not evidence**; monthly radar issues are **disposable triage records**, not authorities. The venue/deadline ledger stays [`docs/SUBMISSION_TARGETS.md`](SUBMISSION_TARGETS.md) |
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
