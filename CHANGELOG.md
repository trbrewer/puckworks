# Changelog

Notable changes. Format loosely follows Keep a Changelog; scientific/component changes are
tracked in detail in `docs/ROADMAP.md` §7.1.

## Unreleased

### Fixed
- **Red CI repaired** (R0/R1): figure tests were matplotlib-dependent but ran in the
  `.[dev]`-only quick lane, failing on CI's 3.10/3.12 since ~PR7. Figure tests now
  `importorskip("matplotlib")`; slow-science installs `.[figures]`. `fail-fast: false` +
  CI diagnostics + JUnit-on-failure. The invalid job-level `secrets` in `if:` on the live
  canary was replaced with a `vars`-gated pattern (was failing at parse).

### Added
- Verified **publication-freeze lifecycle** (`corpus_freeze`): rehearse / materialize / verify
  with a `PublicationReceipt`; the moving corpus is rejected; a label can't mint a freeze.
- **Sanctioned-export** contract + deterministic importer + synthetic end-to-end pipeline.
- **Pressure-atlas v2**: committed hashed pre-analysis spec; time-weighted, gap-aware,
  active-phase metrics; user-clustered bootstrap CIs; seeded one-shot-per-user; exclusion flow.
- **Lateral-coupling feasibility** card + minimal conservative model (unregistered).
- **CI-lane rigor** (R2): network-block fixture, lane-partition policy test, `docs/CI_LANES.md`.
- **Doc-truth** (R3): `docs/CURRENT.md` index; superseded Paper A reviews archived; link check.
- **Real release pipeline** (R4): `puckworks.release` builds wheel+sdist, twine-checks, writes a
  checksummed manifest; `release.yml` installs the wheel clean-room. `[release]` extra + `readme`.
- **Governance** (R5): CODEOWNERS, PR template, CONTRIBUTING, SECURITY, this changelog.

### Changed
- Registry metadata validation raises explicit exceptions (survives `python -O`), not `assert`.
- State vocabulary formalized (no bare "DONE"); `STATE_OF_TRUTH.md` + `CURRENT.md` are canonical.

## 0.1.0
- Initial registry scaffold: 7 founding components, 3 gated.
