# Search-target card: G1 coffee water-retention & relative-permeability curves

**This is a SEARCH TARGET, not a model card.** There is no source yet — the card
project's job is to FIND the source that satisfies the acceptance criteria below,
then replace this file with a normal model/data card for that source. It exists so
the search is aimed at the right measurement instead of drifting into wetting-front
papers that do not close the gap.
**Stage(s):** infiltration (unsaturated flow) · **Kind:** calibration (data source)
**Status:** OPEN SEARCH — no source identified.
**Serves:** gap **G1** (unsaturated flow at fine grinds; ROADMAP §4) and fine-grind-dip
hypothesis #2 (incomplete wetting).

## What is needed (and why this specific thing)
G1 — a continuous-saturation (Richards-type) espresso wetting model — is blocked on
CONSTITUTIVE DATA, not on solver choice (a Richards solver already exists,
egidi2018, but for soil). The missing input is the pair of constitutive functions
that close Richards' equation for a coffee bed:

1. **Water-retention curve** θ(ψ) — volumetric water content (or effective
   saturation S_e = (θ−θ_r)/(θ_s−θ_r)) as a function of capillary suction / matric
   potential ψ. This is the partial-saturation relationship the sharp-front models
   (foster) collapse to a single interface and therefore cannot provide.
2. **Relative permeability / hydraulic conductivity** K_r(θ) or K_r(ψ) — how the
   effective permeability falls as the bed de-saturates.

Together these turn the abstract "incomplete wetting" hypothesis into a runnable
model: with θ(ψ) and K_r, a coffee puck's partial-saturation profile behind the
wetting front becomes computable, which is exactly what distinguishes hypothesis #2
from the sharp-front picture.

## Acceptance criteria (what a satisfying source must have)
A source qualifies if it provides, for a **coffee bed** (ideally tamped, espresso-
relevant grind; roasted & ground, not green):
- a **measured** retention curve θ(ψ) with **saturation resolution** — multiple
  (ψ, θ) points spanning wet→dry, ideally a full imbibition and/or drainage curve,
  NOT a single wetting-front position h(t); AND/OR
- a relative-permeability curve K_r(θ) or K_r(ψ); OR
- **fitted closure parameters** directly ingestible into a Richards solver:
  van-Genuchten (α, n, θ_r, θ_s, and m=1−1/n) or Brooks–Corey (ψ_b, λ, θ_r, θ_s),
  with the fit dataset or R² stated.
- Real units (Pa or m of head for ψ; volumetric or gravimetric θ with a stated bulk
  density). A pixel-unit or arbitrary-scale trace does NOT qualify.
- Enough metadata to place the measurement: grind/PSD, dose or bulk density, roast,
  temperature. Missing metadata caps the value even if the curve shape is right.

Grade the find with the standard vocabulary (ROADMAP §0): a measured curve on
espresso-grind coffee = **independent**; a curve on an analog powder (or green
beans, or a very different grind) = **reference/qualitative** prior only, flagged.

## What does NOT satisfy this (already checked — do not re-propose)
- **foster2025 / foster2025_2 (infiltration):** SHARP-FRONT; models the interface
  position s(t), silent on saturation behind it. This is what G1 must go beyond.
- **egidi2018:** a Richards *solver* (van Genuchten–Mualem) but for SOIL — supplies
  the numerics, not coffee's θ(ψ)/K_r. It is the consumer, not the source.
- **mckeonaloe2021:** n=1 pixel-unit √t wetting-front trace, zero pressure, loose
  bed, no scale/metadata; silent on partial saturation. Superseded by foster.
- Any "pre-wetting vs pre-infusion" observational post that asserts incomplete
  wetting without measuring a saturation profile.
General filter: a paper reporting only a FRONT (position vs time) does not qualify;
it must report SATURATION (θ or S) vs suction or depth.

## Where to look (search strategy for the intake project)
The measurement itself is standard **soil physics / porous-media** — the novelty
would only be applying it to coffee. Scan, in rough order of likelihood:
- **Adapted soil-physics methods on ground coffee:** pressure-plate / centrifuge
  retention; tensiometry; dew-point / chilled-mirror water-potential (WP4C);
  mercury-intrusion porosimetry converted to a retention curve via Young–Laplace.
- **Moisture-profile imaging of a wetting/brewing puck:** NMR / MRI relaxometry
  and profiling; neutron radiography; X-ray µCT segmented for **saturation** (grey-
  level → local water fraction), not just front tracking.
- **Groups / venues:** the Foster/Vynnycky/Moroney applied-math lineage (they name
  the continuous-saturation need); food-engineering porous-media drying/rewetting
  literature (coffee, soil, ceramics, paper); J. Food Eng., Drying Technology,
  Transport in Porous Media, Water Resources Research (for method transfer).
- **Search terms:** "coffee water retention curve", "coffee capillary pressure
  saturation", "ground coffee unsaturated hydraulic conductivity", "espresso puck
  moisture profile MRI/NMR", "van Genuchten coffee bed".
- **Analog fallback (flag as reference-strength):** retention/K_r for a
  particle-size-matched inert powder or fine granular medium, used as a shape prior
  until a coffee-specific measurement appears.

## What to do when found
Replace this file with a normal card for the source, land the θ(ψ)/K_r data (or the
VG/BC parameters) under `puckworks/data/`, and it becomes the constitutive input to
a Richards G1 component (egidi2018's solver form, or a minimal 1-D Richards) that
finally instruments hypothesis #2 with partial-saturation physics. Until then, the
wetting-atom probe (`validation/slow/hyp2_wetting_atom.py`) remains the qualitative
interim; do NOT promote it to a model.

VERDICT: OPEN SEARCH — the single measurement that unblocks G1 is a coffee-bed
water-retention curve θ(ψ) (+ relative permeability) with saturation resolution and
real units; it does not yet exist on file. Find that, and the Richards wetting model
becomes implementable — effort (to intake the data) S; (to build the model
afterward) M.
