# Model card: brewer2026 coupled κ(t) — porosity-evolution synthesis

**Source:** This project (puckworks). **This is a SYNTHESIS card, not a published
model** — it composes four separately-carded mechanisms into one coupled
porosity ODE. There is no external paper; do not search for one.
**Stage(s):** bed_dynamics · **Kind:** synthesis (runtime)
**Status:** proposed (card-first; implementation to follow against this card)

## Scope and mechanism
A single time-dependent bed permeability κ(t) driven by one shared porosity
state ε(t), which every registered bed-evolution mechanism reads and writes.
Replaces the earlier harness approximation κ = f₁·f₂·f₃·f₄ (a product of four
factors each computed independently from ε₀), which double-counts pore volume:
in the multiplicative form, extraction opens porosity that swelling has already
closed, because the factors do not see each other. Porosity is a single,
shared, conserved, bounded quantity; the correct bookkeeping is one ODE in ε
with permeability a function of where ε actually lands.

The four contributing mechanisms, each already a registered component:
- **extraction** (raises ε): soluble mass leaves the grains → pore space opens.
  Donor: cameron2020 / pannusch2024 extraction (whichever runtime is active).
- **swelling** (lowers ε): grains imbibe water and expand. Donor: mo2023_2.swelling.
- **compaction** (lowers ε): pressure/strain consolidates the bed. Donor:
  fasano2000_partII porosity law (Eq. 8.69) as the named compaction closure.
- **fines clogging** (lowers ε): mobilized fines pack downstream pore throats.
  Donor: fasano2000_partI.fines_migration.

The poroelastic waszkiewicz2025 component is the DEGENERATE special case:
extraction-only porosity growth, Φ(t)=m_d(t)/m₀. This synthesis generalizes it
by adding the three loss branches on the same ε.

## Governing equations
Single coupled porosity ODE (this card's defining equation):

1. dε/dt = R_ext(EY, t) − R_swell(t) − R_comp(P, t) − R_fines(t)·ε

with permeability from the shared porosity via Kozeny–Carman (consistent with
the streamtube/wadsworth lineage):

2. κ(t) = f_CK(ε(t)) = κ_ref · [ε(t)³ / (1−ε(t))²] / [ε₀³ / (1−ε₀)²]

normalized so κ(t=0) = κ₀ (the bed's initial permeability from BedState).

**Branch definitions** — each term inherits its donor component's law; this card
fixes only their signs, units, and coupling into ε:

- **R_ext (extraction → +dε/dt).** Soluble mass removed opens pore volume. The
  coupling MUST use the same soluble-inventory convention as the active
  extraction runtime (CLAUDE.md rule 6 — no silent constant merge). For
  cameron2020's per-bed-volume convention c_s0 = 118/φ_s:
  R_ext = (1/ρ_c,eff) · d[m_soluble_removed / V_bed]/dt,
  i.e. Δε over a step = (soluble mass leaving grains in that step) / (grain
  solid density × bed volume). This is the extraction↔porosity relation the
  multiplicative form omitted.
- **R_swell (swelling → −dε/dt).** From mo2023_2.swelling grain-radius growth;
  the pore-volume loss is the grain-volume gain per bed volume. Note mo2023_2's
  headline swelling claims are fixed-Δp and UNVALIDATED (its card) — this branch
  inherits that weakness.
- **R_comp (compaction → −dε/dt).** From fasano2000_partII Eq. 8.69 porosity
  law under the bed pressure P(t) from MachineState. Parameters unidentified in
  source (its card) — this branch is structural, not calibrated.
- **R_fines (fines → −dε/dt, proportional to ε).** From fasano2000_partI
  mobile-fines transport; clogging rate scales with available pore space, hence
  the ·ε factor. Source parameters unidentified (its card).

**Clamp (required).** ε(t) is held in [ε_min, ε_max] with ε_min > 0 and
ε_max < 1. Hitting either bound is a DOCUMENTED regime edge (bed fully clogged
or fully depleted), surfaced in output, never a silent save. κ at ε_min defines
the choke floor.

**Sign / unit audit table** (CLAUDE.md rule 7 — assemble at implementation,
verify before first gate):

| term | sign into dε/dt | units (SI) | donor component | convention note |
|---|---|---|---|---|
| R_ext | + | 1/s | active extraction runtime | must match its inventory convention |
| R_swell | − | 1/s | mo2023_2.swelling | fixed-Δp claims unvalidated |
| R_comp | − | 1/s | fasano2000_partII (8.69) | params structural/unidentified |
| R_fines | − (×ε) | 1/s | fasano2000_partI | params unidentified |

## Parameters
| symbol | value | units | source |
|---|---|---|---|
| ε₀ | from BedState.porosity | — | measured/config per run |
| κ₀ | from BedState.k_m2 | m² | measured/config per run |
| ε_min, ε_max | to specify at implementation (e.g. 0.02, 0.95) | — | assumed (regime clamp) |
| extraction inventory constant | inherited from active extraction runtime | mixed | NOT re-specified here (rule 6) |
| swelling / compaction / fines params | inherited from donor components | mixed | mostly unidentified in sources |

No NEW free parameters are introduced by this synthesis beyond the clamp bounds.
That is deliberate and is what makes the validation below meaningful.

## Calibration and validation offered by the source
None yet — this card proposes the component and its gate; the gate is run at
implementation. **The validation must be parameter-free to earn any strength:**

- **Primary gate (independent, if it passes):** fix every branch's parameters
  from its own donor card, compose with ZERO free parameters, and test whether
  the coupled ε(t) reproduces the Waszkiewicz 9-bar Q(t) trace. The poroelastic
  branch ALONE already fits this (rung 4, RMSE 0.113); re-fitting the full
  composition to the same trace would be post-fit reconstruction and is
  FORBIDDEN as a strength claim. A parameter-free composition that reproduces
  the trace is independent; one that does not, yields a residual that diagnoses
  which branch is mis-scaled — report the residual, do not tune it away.
- **Stronger gate (cross-pressure, if params allow):** fix at 9 bar, predict a
  different pressure's Q(t) from Waszkiewicz's other traces. This is the
  Phase-2 cross-pressure discriminator; passing it is genuinely out-of-sample.
- **Degeneracy check:** with swelling/compaction/fines branches disabled, the
  ODE must reproduce waszkiewicz2025.poroelastic exactly (extraction-only
  Φ(t)). This is a verification gate on the reduction.

## Assumptions and validity range
- One well-mixed porosity per bed (or per depth cell if run on the A8 per-cell
  BedState); no lateral structure (that is the streamtube component's job).
- κ(ε) is Kozeny–Carman; shares that lineage's limits.
- **Framework-level validity only.** This synthesis is exactly as sound as its
  shakiest branch, and three of the four donors carry documented weaknesses:
  mo2023_2 swelling (fixed-Δp, unvalidated), fasano I and II (parameters
  unidentified, source validation qualitative). The honest label is "coupled
  κ(t) FRAMEWORK; branch fidelity inherited," NOT "validated κ(t) law." No
  future session should over-trust the composite beyond its weakest input.
- Clamp bounds are regime edges, not physics; results at a clamp are flagged.
- Silent on: temperature dependence of any branch, hysteresis, air-phase
  effects (that is the G1 unsaturated-flow gap, out of scope here).

## Interface mapping
Inputs consumed: BedState (ε₀→porosity, κ₀→k_m2, dose/geometry), MachineState
(P(t) for compaction and the flow solve), and the active extraction runtime's
EY(t)/soluble-removal signal (for R_ext — this is the extraction↔bed_dynamics
coupling). Outputs: κ(t) and ε(t) traces into BedState over the shot; feeds the
flow solve each step.
Coupling: runtime bed_dynamics component. It closes the loop
extraction→ε→κ→flow→extraction, so it must be stepped consistently with the
flow and extraction solvers (shared ε per step), not computed once from ε₀.

## Extractable data
None — synthesis card. Validation data is Waszkiewicz 9-bar (and other-pressure)
Q(t), already held (data/waszkiewicz2025/).

## Overlaps and conflicts
- **waszkiewicz2025.poroelastic (generalizes):** that component is this one's
  extraction-only special case; the degeneracy gate enforces exact reduction.
  Do NOT retire it — it remains the validated minimal model and the reduction
  target.
- **brewer2026.streamtube (complements, orthogonal):** streamtube is LATERAL
  static heterogeneity (many tubes, fixed σ); this is a SINGLE bed's temporal ε
  evolution. The natural future union is per-tube κ(t) (an N-tube coupled ODE),
  which is the lee2023-suggested and streamtube-card-noted extension — a
  separate, later work item, not this card.
- **The four donor components (consumes):** this synthesis does not replace
  them; it composes their laws on a shared ε. Each remains independently
  registered and gated.
- **Backlog "bed_dynamics: κ(t)=κ₀·f(P,ε,E)":** this card IS that item, in its
  physically-coupled (ODE) form rather than the multiplicative approximation.

## Implementation estimate
Small (CC): one coupled ODE (scipy), four branch calls, a clamp, Kozeny–Carman
κ(ε), stepped with the flow solve. The work is mostly the sign/unit audit table
and the parameter-free composition — NOT new physics. Gates: (1) degeneracy →
poroelastic exact; (2) parameter-free 9-bar Q(t) reproduction, report residual;
(3) optional cross-pressure out-of-sample. Register as `kind: synthesis` so no
future reader hunts for a paper.

VERDICT: implement-now (as a synthesis component) — the coupled porosity ODE is the physically-correct form of the κ(t) backlog item, fixes a real double-counting error in the multiplicative harness closure, and introduces no new free parameters so its parameter-free gate against Waszkiewicz Q(t) can earn genuine independent strength; but it must be labelled framework-level with inherited branch fidelity, since three of its four donors carry unidentified or unvalidated parameters — effort S
