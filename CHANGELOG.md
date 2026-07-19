# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

- **Guided Pull Laboratory request semantics + layered integrity (schema v4, #70):** the Lab request is now honest and operational. `domain_policy` (`warn`/`strict`) is enforced through the authoritative product domain BEFORE the producer runs — a `REJECTED` input blocks under any policy and a `WARNING` blocks under `strict`; when blocked the scientific producer is **not** invoked and the lens is surfaced as `REQUESTED_BUT_NOT_EXECUTABLE` (never produced as zero). `requested_lens_ids` actually selects the common-scenario lenses (unknown id raises; non-executable id surfaced, not dropped; `executed_common_scenario_lenses` is derived). `reference_selection_policy` (`none`/`interactive_fast`/`selected`) is unambiguous (unknown selected id raises). Static native-runner/adapter **capability** is separated from per-request **execution** state (a validated `ComponentLabSpec`, with a `METADATA_INCOMPLETE` fallback rather than an invented capability). Integrity is now **three recomputed layers** — `scientific_payload_sha256` (invariant to build identity, Python version, and optional-dependency installation), `capability_snapshot_sha256` (env-dependent), `artifact_sha256` (full) — with `verify_integrity()` tamper detection and finite canonical JSON (`NaN`/`Infinity` rejected). No model numerics changed; the executed common-scenario lens is still Cameron only; no multi-model validation claim.

- **Centralized component rights + Grudeva legacy containment (#73):** a single authoritative rights registry (`puckworks.rights`) with distinct code/data/output states and a finite vocabulary (CLEAR / PERMISSION_DOCUMENTED / INDEPENDENT_REIMPLEMENTATION / RIGHTS_REVIEW_REQUIRED / RIGHTS_BLOCKED / NOT_REVIEWED / NOT_APPLICABLE; an unreviewed component is NOT_REVIEWED, not CLEAR). `grudeva2025.reduced` is code RIGHTS_BLOCKED pending #73; the Guided Pull Laboratory, native runners, and adapters consume the registry (the product-local rights dictionary is removed) and refuse it; a release-readiness guard fails if a rights-blocked component would enter a new artifact; README governance rejects an 'Executable model' label for it. README/card/module/registry wording corrected to 'Legacy - rights-blocked pending #73' (retained in history; not for new execution/integration). No model numerics changed; v0.3.0 history/assets untouched. #73 stays open pending the maintainer decision.

- **Guided Pull Laboratory second-lens adapter-readiness audit (#70):** a deterministic audit (`puckworks.product.lab_adapter_audit`) of the extraction candidates against the common scenario. Finite decisions: `pannusch2024.solver` and `mo2023_2.coupled_bed` -> ADAPTER_REQUIRES_TESTED_CONVERSION, `romancorrochano2017.extraction` -> OUTPUTS_NOT_COMPARABLE, `grudeva2025.reduced` -> RIGHTS_BLOCKED (#73). No candidate is ready without an invented conversion, so **no second common-scenario lens is added** — the honest dispositions + report are the deliverable.

- **Scheduled research-intake/registry-impact automation (#46):** a `research-impact` workflow (PR read-only; scheduled/dispatch posts a monthly note to #46 from trusted main, `issues:write` gated; SHA-pinned) that validates the intake records and computes the deterministic `tools/research_impact.py` report. Added radar precision-regression fixtures (relevant espresso extraction / porous-bed infiltration / espresso telemetry vs irrelevant medical / petroleum / IoT classes); the first scan's precision is recorded on #42 (51 retained, 0 relevant — generic families noisy; porous-media physics families deliberately kept broad, not coffee-gated).

- **Guided Pull Laboratory native reference runners (development):** three genuinely-executed native reference cases (`waszkiewicz2025.poroelastic` static refit, `wadsworth2026.permeability` Table-1 percolation collapse, `foster2025.infiltration` first-drip bracket), each reusing the validation-gate callables (no equation duplication), with per-runner failure isolation. The Lab now separates executed native references from not-yet-implemented coverage; `grudeva2025.reduced` stays RIGHTS_BLOCKED (#73).

- **Guided Pull Laboratory contract hardening (schema v3, development `0.4.0.dev0`):** exact scenario
  identity + override provenance (`guided_v1` runs are no longer mislabelled `pv19_named`); typed
  `ScenarioRequest`/`ScenarioExecution` records; separated **scientific-payload** vs **full-artifact**
  integrity hashes (the downloadable artifact now carries `source_commit`/`package_version`/
  `workflow_run_id`/`wheel_sha256`, supplied explicitly — no git subprocess in the producer); correct
  observable roles (prescribed/derived/simulated/unsupported/diagnostic); an explicit component
  capability/rights matrix (with `grudeva2025.reduced` marked **RIGHTS_BLOCKED** pending issue #73);
  honest reference-suite coverage (executed results vs not-yet-implemented placeholders); real
  scientific trace plots in the Streamlit UI and the Actions batch (required figure — the batch fails if
  it cannot render); and an artifact hash manifest. Still one executed common-scenario lens (Cameron);
  no multi-model validation claim.

- **Guided Pull Laboratory** (development `0.4.0.dev0`, not released): `puckworks.product.lab` exposes
  the full component registry as a coverage matrix and runs the compatible subset as independent model
  lenses (one executed extraction lens today) — never a validated digital twin. Added a Codespaces
  devcontainer + Streamlit UI (`apps/lab_app.py`, `webapp` extra; not a core dependency) and a
  reproducible `guided-pull-batch` Actions runner. Browser/Pyodide hosting is a documented feasibility
  note only (`docs/PAGES_FEASIBILITY.md`); nothing is deployed to a third-party host.

## 0.4.0.dev0

Development line opened after the v0.3.0 release. Source/development builds identify themselves as
`0.4.0.dev0`; the latest **public release remains v0.3.0** (GitHub Release; not on PyPI) and its
install/notebook guidance is unchanged. Unreleased work is tracked above and in `docs/ROADMAP.md`
§7.1. Three static, generated public interactives are now **live** (no new model coupling): PV-03
"The Cup Hides the Clock", PV-05 "More Physics Made It Worse", and **PV-04** "How We Falsified Our Own
Espresso Headline" (<https://trbrewer.github.io/puckworks/analysis-autopsy/>) — the analysis autopsy
exposing replicate-level extraction-yield points, per-panel evidence partitions, and the corrected
middle-minus-coarse (dial 1.7 − dial 2.0) result. No next public-value product lane has been
authoritatively selected — selection is pending. This is development-line work only — not a release
candidate; the latest public release remains v0.3.0.

## 0.3.0

First functional minor after v0.2.0. Adds the caller-owned input boundary and the **Guided Espresso
Pull** — a rights-independent, runnable *guided mechanism explorer* — under the supported
`puckworks.product` API. Rights-independent throughout: no upstream fixture data is shipped or loaded.
puckworks remains **GitHub-only** (not on PyPI).

### Added

- `puckworks.product.normalize_shot_input` — a rights-independent normalization boundary mapping
  caller-owned / synthetic channels to a versioned `ShotInput`.
- Guided Espresso Pull core: `PullRecipe` / `PullConfig` / `PullRun` / `StageResult` /
  `DomainFinding` / `ComponentCoverage`, `simulate_pull`, `evaluate_domain`, the `pv19_named`
  (fixed reference) and `guided_v1` (range-limited) presets, deterministic JSON/Markdown export, a
  full 25-component coverage ledger, and the `puckworks-pull` CLI. The one executed chain is the
  coherent `cameron2020.extraction_bdf` shot model; every other component gets an explicit
  disposition rather than being silently coupled.
- Authoritative `PullRun.traces` (`PullSeries` / `PullTrace`) copied from the solver at full
  precision, each labelled by value role (prescribed input · simulated output · derived quantity).
- Stage-by-stage visual report: `render_pull_report` → `PullReportArtifacts` (evidence-badged
  figures + captions + JSON/Markdown), matplotlib kept lazy so the core stays matplotlib-free;
  `puckworks-pull run … --report-dir/--figures`.
- Guided Colab notebook (`notebooks/guided_espresso_pull_colab.ipynb`) with native `#@param`
  controls, a `PUCKWORKS_WHEEL` override for hermetic testing, and SHA-256 hash-verified install.

### Changed

- README hero updated to the maintainer-supplied logo; the development-source line now reads
  `0.3.0`. The latest **public release remains v0.2.0** until v0.3.0 is published.

### Scientific / evidence

- The guided pull is an `EXPLORATORY_SIMULATION`, code-verified against the source paper, **not**
  independently validated against a measured cup. It does **not** model puck wetting, physical first
  drip (reported `unavailable`; the old number survives only as a diagnostic), a dynamic pressure
  profile (pressure is a prescribed constant input), or a thermal transient (temperature is
  recorded-only). It reports chemical **composition**, never sensory flavor, and never averages
  alternative components into a consensus.

## 0.2.0

First verifiable post-0.1 release: canonical status, complete gate evaluation, a deterministic
Paper 3 archive, a hardened CI supply chain, and a fully-adjudicated per-claim evidence graph.

### Added
- **Canonical status source of truth**: `docs/status/current.json` → generated
  `STATE_OF_TRUTH.md` (`python -m puckworks.statusdoc`); a CI verifier rejects stale/contradictory
  state; `--audit-ruleset` reads the actual GitHub required-checks setting.
- **Typed gate evaluation** (`puckworks.gate_runner`): `GateStatus`/`GateResult`/`GateSuiteResult`;
  every gate runs (no short-circuit); exceptions become `ERROR`; zero-gate components are explicit
  (`SKIP`/`ACKNOWLEDGED_EXCEPTION`), never a vacuous pass. `run_all_gates` kept as a compat wrapper.
- **Deterministic Paper 3 archive** (`puckworks.paper3.archive`): `create/verify/inspect-archive`
  build a byte-reproducible `.tar.gz` with a per-member sha256 + role + provenance manifest,
  verifiable without the source checkout; privacy/redistributability fail-closed scan.
- **Paper 3 per-claim evidence graph** (schema v2): 51/51 gate wirings adjudicated; scope-aware
  strict modes (`--scope paper3` release gate, `--scope all`); component→gate roll-up and
  zero-gate policies enforced.
- **Lateral-coupling discrimination harness**: exact Ξ equalization group, continuous-α proxy
  matching; representational/mathematical distinguishability only (Paper 4 NOT authorized).
- **Publication-freeze lifecycle**, **sanctioned-export** contract + synthetic pipeline, and
  **pressure-atlas v2** (from the convergence lane).
- Supply-chain: `security.yml` (dependency-review + pip-audit); SHA-pinned Actions; a `min-deps`
  lane proving the dependency floors.

### Changed
- Supported Python stated explicitly (3.10–3.13; 3.12 primary); dependency floors `numpy>=2.0`
  (uses `np.trapezoid`), `scipy>=1.13`.
- `foster2025.infiltration` evidence tier demoted `controlled_independent → sign_or_compatibility`
  under the roll-up policy (ROADMAP §7.1); the registry declares no `controlled_independent`
  component.
- Registry metadata validation raises explicit exceptions (survives `python -O`); state
  vocabulary formalized.
- `paper3.build bundle` renamed to `list-bundle` (it lists paths; use `archive create-archive`).

### Fixed
- **Red CI repaired** (R0/R1): matplotlib-dependent figure tests ran in the `.[dev]`-only quick
  lane; now `importorskip("matplotlib")` + `.[figures]` in slow-science. Invalid job-level
  `secrets` in `if:` replaced with a `vars`-gated pattern.
- `all(...)` short-circuit in the gate runner (later failures were hidden) — see gate_runner.
- **Private corpus could leak into the distribution**: the broad `puckworks.data` `**/*.csv`
  package-data glob swept `visualizer/{raw,normalized_v3,crawl_*}` + `aggregate_stats.csv` into the
  wheel/sdist. Added `exclude-package-data` + a `packaging` CI job that inventories the built
  distributions (no private paths; required data present) and clean-room-installs the wheel.

### Scientific / evidence
- Every asserted Paper-3 claim carries an honest per-gate tier, relationship, caveat, and
  claim-not-supported statement; no tier is promoted by inference. G10 viscosity tensions and the
  c_sat 212.4/224/170 constant are surfaced (not merged).

### Data / provenance
- New MANIFEST dataset `cameron2020/fig5_grind_deviation` (rule-5 intake) backing the streamtube
  held-out gate.

### Compatibility / migration
- `run_gates`/`run_all_gates` remain Boolean wrappers over the typed runner.
- `bundle` still works but warns; prefer `list-bundle` / `create-archive`.
- No public numerical behaviour change; existing examples reproduce.

## 0.1.0
- Initial registry scaffold: 7 founding components, 3 gated.
