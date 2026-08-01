# CLAUDE.md — puckworks

Component registry for espresso process models. NOT a monolith: stages with
typed contracts; each published model is a component with provenance,
assumptions, validity range, and validation gates. A simulation is a
configuration.

## Read first, always
- `docs/ONBOARDING.md` — session entry point (read order, state-verification,
  standing caveats).
- `docs/ROADMAP.md` — the plan. §3 is the development sequence; work items by
  their numbers (0.x data intake, 1.x components, 2.x harnesses, 3.x later).
- `docs/SPRINTS.md` — the current sprint breakdown and status checklist.
- `docs/cards/` — cards are the source of truth for each model's physics.
  Never implement from memory of a paper; implement from its card, and if the
  card is ambiguous, STOP and flag it (do not guess).

## Commands
```
pip install -e ".[dev]"
pytest -v                                  # quick gates (~30 s) — must pass before any commit
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
```

## Architecture rules (non-negotiable)
1. Every new component: model card exists first → module under
   `puckworks/models/<key>/` → registered in `puckworks/models/__init__.py`
   with assumptions + validity range → at least one gate wired to real data
   in `puckworks/data/`.
2. `kind`: runtime vs calibration per REGISTRY_STATE. Prefer calibration;
   forced runtime coupling is the mega-model failure mode.
3. Gates: quick gates (<~30 s total) go in `puckworks/validation/gates.py`
   and CI. Slow/GPU work goes in `validation/slow/` or the Colab notebook —
   NEVER in CI.
4. Validation-strength vocabulary (ROADMAP §0): independent · post-fit
   reconstruction · verification · qualitative. Never promote a rung when
   labelling a gate or writing a docstring. Status promotions require a
   ROADMAP §7.1 changelog entry.
5. Data intake (Phase 0): every dataset lands with a manifest row per the
   ROADMAP §3 manifest rule (source, extraction method, units as published
   and in registry, uncertainty, license, gate use, validation strength).
   Manifests live in `puckworks/data/MANIFEST.csv`.
6. No silent merges of conflicting constants (c_sat 212.4/224/170; ceiling
   values; ROADMAP §5.4–5.5): these are config fields surfaced in reports.
7. Units: strict SI at contract boundaries. The Forchheimer k_I correlation
   fails silently off-SI (ledger A7) — assert units, don't trust them.
8. Naming: `Fo_F` = Forchheimer number, `Fo_diff` = Fourier number. Bare
   "Fo" is banned in code and docs (ROADMAP P6).
9. Dial spaces are grinder-specific and non-portable (ledger A9/G5). Never
   map one grinder's dial to another's without an explicit refit adapter.
10. cameron2020 `paper_mode` stays quarantined (import-order sensitive) —
    do not add it to this package.

## Conventions
- Commit style: `<item#>: <what>` e.g. `0.2: waszkiewicz Zenodo intake + manifest`.
  One roadmap item (or one sprint) per commit where practical.
- After a component lands or a gate status changes: update `docs/ROADMAP.md`
  (§7.1 changelog) and tick `docs/SPRINTS.md` in the same commit.
- New contract fields: additive only; bump `contracts.SCHEMA_VERSION`;
  implement ledger items (A1–A10) only when the consuming sprint needs them,
  not speculatively.
- Python ≥3.10, numpy/scipy core; taichi is optional (`[lb]` extra) — code
  must import without it.

## Paper 1 assurance layer: FROZEN (2026-07-31)

The claim/evidence machinery is closed. Rounds 10-12 each found defects in the previous round's
gates, and the layer is now ~4,800 lines guarding, in part, a registry with **zero** entries. Do not
harden it further on speculation.

- **Do not** extend `inferential_evidence.py`, the procedure registry, evidence records or the
  chronology proof while `PROCEDURE_REGISTRY` and `PRODUCTION_EVIDENCE` are empty. Paper A performs
  no inferential procedure and requests no unlock; build the machinery against a real case, when
  there is one.
- **Do not** add prohibited-phrase rules in response to a hypothetical paraphrase. The taxonomy is
  defence-in-depth and is documented as incomplete by construction. The load-bearing defences are
  generated central text, pre-insertion scanning, and proposition coverage.
- **Do** keep the existing gates green, and do fix a gate that lets a defect reach a reader-facing
  surface.

**What reopens it:** an analysis that actually earns a decision (a calibrated procedure with a
predeclared margin), or a defect demonstrated in *shipped* reader-facing text — not in a gate.

**The P0 acceptance criterion is now falsifiable** and replaces "no reviewer objects to the
wording": every load-bearing claim surface must carry `symmetric_non_establishment` — the analysis
establishes neither that the advantage is reproducible/useful **nor** that it is absent. All nine
surfaces are checked by `claim_policy.SURFACE_ASSERTIONS`. Wording disputes that do not violate that
criterion are editorial preference, not findings.

## What NOT to do
- No implementation without a card. No parameters invented where a card says
  "not provided". No upgrading authors' validation claims.
- Don't refactor existing gated components while landing new ones — separate
  commits, gates green in between.
- Don't touch `notebooks/espresso_lb_colab.ipynb` numerics without rerunning
  its validation gate cells.
