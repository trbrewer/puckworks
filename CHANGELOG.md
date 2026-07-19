# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

- **Single-source native reference producers + result contract v2 (#70):** each native reference runner now consumes ONE shared full-precision summary producer (`puckworks.product.lab_reference_producers`) instead of re-deriving the fitted quantity / collapse statistic / first-drip bracket inline; the gate remains the pass/tolerance authority and a test binds the two (they compute the same values). The Foster first-drip threshold is a single named model constant `foster2025.infiltration.FIRST_DRIP_THRESHOLD_G` consumed by **both** the gate and the runner (the gate's own `argmax` first-drip is replaced by the explicit `observed_first_drip_s` crossing — no numerics change; the `0.5`/`0.7`/`1.2` literals no longer appear as executable constants in the runner). Producer precision is preserved (outputs carry the exact `value` plus a separate rounded `display_value`; rounding never happens before canonical hashing). Failure results satisfy the full schema with a finite `execution_state` vocabulary and a **sanitized, path-free** error message (no stack traces or filesystem paths leak into a published artifact). Runner results consume the centralized code/data/output rights and flag outputs not cleared for public redistribution. No model numerics or gate verdicts changed (gates PASS=50 unchanged).

- **Explicit Guided Pull Laboratory component catalog (#70):** the component matrix no longer infers common-scenario compatibility from a broad `stage`/`kind`/`role` substring heuristic. A committed `puckworks.product.lab_catalog` states one authoritative record per registered component — the **disposition** and **adapter capability** are explicit; registry-derived fields (module, card path, stage, role, evidence, provenance, **gate ids**, validity range) are declared and validated against `puckworks.components()`; runner/adapter capability, rights (code/data/output + public-use eligibility), and quantity basis are consumed from their authoritative sources. `validate_catalog()` is a CI gate: a missing entry, an unknown gate id, an unresolved runner/adapter id, a rights mismatch, or a rights-blocked component not dispositioned `RIGHTS_BLOCKED` fails. `lab._lab_spec` consumes the catalog (an AST test proves it no longer compares against stage/kind literals); the redundant `_COMMON_SCENARIO_LENSES` dict is removed in favour of the `ADAPTERS` registry. No component count is hard-coded; the env-dependent optional-dependency skip remains a runtime overlay, not a committed capability. No model numerics changed.

- **Adapter-driven common-scenario lens execution (Lab schema v5, #70):** the Laboratory no longer "runs Cameron, then reports a selection" — it prepares a model-independent scenario, resolves the selected lenses, evaluates each lens's OWN domain, and executes **only** the selected, ready, in-domain lenses. `prepare_scenario()` calls no producer; a `LensAdapterSpec` protocol wraps each model (the first adapter wraps Cameron and calls the existing `simulate_pull` — no equation re-implemented); a finite `lens_selection_policy` (`primary` / `all_ready` / `selected` / `none`) replaces the future-expanding empty-tuple default (`requested_lens_ids` requires `selected`; duplicates are canonicalized; adding a future adapter never changes `primary`). The producer is now invoked **only** for a selected+ready+in-domain lens: selecting `none`, a registered-but-non-ready component, a rights-blocked lens, or a domain-blocked Cameron runs **no** producer; the executed-lens count equals the producer-invocation count; a fake adapter executes independently of Cameron; and one adapter failing never erases another. Each `LensResult` records requested/readiness/rights-use/domain/producer-invoked/status/mapping/outputs/decline-reason. Reference selection now resolves **components** (a registered component with no runner is `RUNNER_NOT_IMPLEMENTED`, a rights-blocked one is `RIGHTS_BLOCKED` and never executed; only a non-registered id is "unknown"). No model numerics changed; Cameron remains the only executable lens.

- **Affirmative rights clearance + release safety (#73):** rights are now **use-specific** — one state is never universally sufficient. New policy functions (`may_execute_locally`, `may_execute_in_public_batch`, `may_publish_outputs`, `may_include_code_in_release`, `may_include_data_in_release`) each consult the relevant code/data/output field with the strictness that use demands: a `RIGHTS_BLOCKED` component is refused everywhere; `NOT_REVIEWED` stays inspectable **locally** but is a visible **gap** for public execution, output redistribution, and release (never reported as "clear"); only affirmative clearances (`CLEAR`/`PERMISSION_DOCUMENTED`/`INDEPENDENT_REIMPLEMENTATION`) permit an outward or release use. The **generic release bypass is removed** — there is no `--allow-rights-blocked` flag; the guard hard-blocks only on code not cleared for release inclusion and passes once the blocked module is absent (an authorized removal makes it pass, not a "build anyway" flag), while `NOT_REVIEWED` gaps are reported, not silently passed. `RightsRecord` gains validation (ISO review date; reviewed determinations require source + date; `RIGHTS_BLOCKED` requires a decision issue + reason; `PERMISSION_DOCUMENTED` requires permission metadata; `NOT_APPLICABLE` requires a reason; unknown/lowercase vocabulary and duplicate/unregistered records are rejected, with a `tombstone` exemption for removed components). Product-local `"clear"` claims are gone: `RunnerSpec` no longer defaults to `"clear"` (runner results consume the centralized record's code/data/output states + a public-output decision), the adapter audit derives rights from the registry, and reference-basis admissibility consumes the use-specific policy. A structured `review_backlog()` surfaces the reviews still owed (Cameron code+outputs first). No model numerics changed; Grudeva 2025 stays rights-blocked pending #73.

- **Deterministic research-impact source scope (#46):** `tools/research_impact.py` now has an explicit source-scope contract. The default **committed** scope examines only git-tracked cards/intake (via `git ls-files`), so the canonical report is reproducible from a commit and never silently incorporates a maintainer's untracked local files; **working_tree** scope opts in to untracked files for local authoring, and a non-git directory degrades to a recorded `working_tree_fallback` rather than a false `committed`. The report gains a `source_scope` block (`scope`, `requested_scope`, tracked/untracked counts, `excluded_untracked_paths`) and `schema_version` 2. CI and the standing-issue workflow pass `--source-scope committed` explicitly. Verified: run 29693508558 (head `3d9e254`) reproduces byte-for-byte from a clean detached worktree at the same SHA; the previous local divergence was exactly the 17 untracked cards, now excluded by committed scope.

- **Research-radar 51-candidate adjudication fixture + precision metrics (#42 / #46):** the FIRST real research-radar scan (workflow run 29666830887, source commit `5f300c00`, artifact SHA-256 `21a53ad1…`) is committed verbatim as a regression fixture with its recorded human adjudication (all 51 retained candidates are off-domain false positives from the broad generic query families; **0 relevant**). A deterministic `research_radar.adjudication_metrics()` computes precision@retained (0.00) and per-query-family precision (every generic family 0.00; coffee-anchored families quiet) over the human labels — it derives no relevance itself, only tallies the adjudication, rejects a non-vocabulary label, and surfaces any unlabelled candidate rather than hiding it. This guards against a classifier change silently turning off-domain noise into apparent relevance. The scheduled/dispatchable `research-impact` workflow was exercised from `main` (run 29691062085): intake validated, the deterministic registry-impact report computed + uploaded, and the idempotent monthly note appended to #46.

- **Guided Pull Laboratory reference-basis ontology + fail-closed inventory adapters (#70):** groundwork for a *possible* second common-scenario lens — delivered as the ontology + validators + audit, **not** a second lens (none is ready). A finite quantity-basis vocabulary (`bed_volume` / `grain_volume` / `per_bed_cell` / `per_species` / `liquid_phase_profile` / `flow_trend` / …) makes each component's reference basis a typed value instead of prose; inventory-conversion primitives are **fail-closed** — the only registered rule is the identity (same basis), so every cross-basis request raises `UnsupportedConversion` (the framework never invents a scale factor), and a conservation primitive rejects any transform that does not conserve total solute inventory. Second-lens admissibility is therefore mechanical: `mo2023_2.coupled_bed` (per-bed-cell) and `pannusch2024.solver` (per-species) have no validated conversion to Cameron's bed-volume basis, `romancorrochano2017.extraction` is a flow trend (not an absolute EY/TDS), and `grudeva2025.reduced` is rights-blocked (#73) — **no candidate is admissible, so no second lens is added.** The existing prose adapter audit is now bound to the typed basis (they cannot disagree). No model numerics changed.

- **Guided Pull Laboratory native-runner authority + validation + selection (#70):** every pass/band verdict a native reference runner reports is now the **authoritative gate verdict** — the runner *calls its component's quick gate* (`gate_waszkiewicz_static_refit`, `gate_wadsworth_collapse`, `gate_infiltration_triangle`) and surfaces it verbatim, so a magic number (the wadsworth `0.7 < ratio < 1.2` collapse band, the foster `> 0.5 g` first-drip threshold, the waszkiewicz refit tolerances) can never drift between a runner and its authority. The foster first-drip crossing is now **explicit** — when the weight never crosses the threshold there is no first drip (reported `unavailable`), never a spurious `argmax`-of-all-False sample at t[0]. `RunnerSpec` and the runner registry are validated (runtime-class vocabulary, key/component-id match, registration, rights consistency), results are schema-sanitized + finite (a NaN or a unit/role-less output becomes `FAILED`, never a malformed result), and selection is explicit (`run_selected` raises on an unknown id by default — never a silent drop; `available_runners()` / `runtime_class()` expose the selectable set). No model numerics or gate thresholds changed.

- **Guided Pull Laboratory unit-safe scientific figures (#43 / #70):** the shared plotting layer (`lab.render_data`) is now **unit-safe by construction** — every source trace is split into one panel per unit, so a single ordinary y-axis never overlays incompatible units (bar / g/s / g / % / kg/m³). An explicit `lab.assert_unit_safe()` validator rejects a mixed-unit panel, and both the Streamlit UI and the Actions batch render through it (they *cannot* draw a mixed-unit axis). The batch now emits one figure **and** a CSV text-alternative per panel, records a `panel_inventory` in the manifest, and keeps the required-figure gate (no plottable panel fails the job). The Streamlit UI adds a per-unit panel selector, per-panel data table + CSV download, an axis unit label, and a `domain_policy` (warn/strict) control that surfaces the operational block path. No science recomputed in the view layer.

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
