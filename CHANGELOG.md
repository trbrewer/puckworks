# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

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
