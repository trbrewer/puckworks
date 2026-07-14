# Paper 4 (future) — Spatial concentration & control mode

*Fork scaffold created 2026-07-14 per `PUBLICATION_STRATEGY_REVIEW.md` §5. This `future/`
folder is the deferred publication home for the N-tube work. The N-tube **code and
results are preserved** in `puckworks/harness.py` (`ntube_*`) and the broad
`PAPER_B_DRAFT.md` Result 3 — this note only re-homes the **publication** of that
material out of the near-term portfolio. Claim ownership: `../CLAIM_OWNERSHIP.md`.*

**Status:** DEFERRED. Not a near-term paper. The N-tube result stays an **exploratory
simulation** in the registry; it is removed from the narrow Paper B (B2) as a central
narrative and is not published on its own until the requirements below are met.

**Future question (§5.1):** *How do machine control mode and lateral hydraulic coupling
govern the amplification or suppression of flow heterogeneity in a dynamically evolving,
near-choke porous bed?*

## What must mature before this is a paper (§5.2)

- **Physical model:** a defensible lateral-exchange operator (currently **CARD-BLOCKED**,
  gap G-lat / PV-14 — no card exists for the physical operator); explicit local + global
  conservation laws; permeability–porosity–extraction coupling; matched pressure- and
  flow-control BCs; a clear tube↔physical-region mapping.
- **Mathematical analysis:** defined base state; linear-stability / transient-growth /
  finite-time-amplification analysis; distinction between instability, localization, and
  thresholded first passage; sensitivity to the initial perturbation spectrum.
- **Numerical analysis:** full-trajectory convergence; event-time interpolation;
  independent integrator comparison; timestep + spatial refinement; per-step balance
  diagnostics; sensitivity to N, seed, closure, control mode, lateral strength.
- **Experimental evidence:** spatially resolved flow/wetting; depth-resolved
  porosity/extraction; imaging or tracer data; repeated shots; controlled pressure/flow
  modes; a definition of "channeling" tied to measurable physical structure.

## Material re-homed here (publication only; code unchanged)

- N-tube finite-time flow concentration; conductance-floor test; switching-convergence
  study; control-mode (flow vs pressure) contrast; lateral-coupling **proxy** behaviour
  (broad Paper B Result 3 / `ntube_*` harness).
- The fine-grind-dip anomaly as a central narrative (demoted from B2).

Until matured, the N-tube result is used only as an **exploratory registry component** and
as motivation for the discriminating spatial/control-mode experiments proposed in Paper B2
and Paper 3 — never as a standalone instability claim.
