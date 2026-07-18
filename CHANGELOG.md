# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

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
