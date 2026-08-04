# Model card: Foster 2025 infiltration

**Paper:** Foster et al., Phys. Fluids 37, 013383 (2025). DOI 10.1063/5.0245167
**Stages:** infiltration, machine (pump/headspace) · **Kind:** runtime
**Status:** gated (parameter-free triangle: predicted first-drip 6.4-7.8 s brackets
observed 7.0 s on DE1 fixture A; bed capacity 7.5-14.0 g brackets fitted W_dead 8.8 g)

## Scope
Sharp-front unsaturated infiltration into a dry bed with pump characteristic,
pipe resistance, and trapped-air headspace; validated by time-resolved micro-CT
(1 s resolution) on a 59 mm basket.

## Implemented here
Recorded-pressure closed form s(t) = sqrt(2k Int P dt / (mu phi_T)) with capillary
p_c option. Full pump/headspace model (their Eqs. 2-7) = PUCK LAB "machine mode"
backlog. Coupling extraction start to front passage per depth cell = solver backlog.

## Interface mapping
Inputs consumed: `MachineState.P_of_t` — the recorded or prescribed basket pressure history
[bar], time-integrated; `BedState.k` — bed permeability k [m^2] (or `BedState.kappa` via
`k_from_kappa`, which routes through the Cameron flux table); `BedState.porosity` — the
water-accessible porosity phi_T; `BedState.depth_m` — bed depth L [m]; `BedState.area_m2` —
basket area A [m^2], needed only for the bed-water-uptake outputs. An optional capillary
suction p_c [bar] adds to the driving pressure.

Outputs produced: the sharp wetting-front position s(t) [m], capped at the bed depth L; and the
front-arrival time at the bed base — `t_saturate` / `t_s` — which IS this card's predicted
**first-drip** time. That prediction is the card's headline gated result (Status, above): a
predicted first drip of 6.4-7.8 s brackets the observed 7.0 s on DE1 fixture A.

Couplings: runtime. Front position comes from `infiltration.front_from_pressure` and
`machine_mode.front_headspace_mm`; `infiltration.observed_first_drip_s` is the measurement-side
comparator (first crossing of a 0.5 g scale threshold), NOT a model output. **This section is
deliberately narrow.** It names only inputs and outputs the source, this card and the
implementation already support, and only ones common to BOTH registered components — one card
serves `foster2025.infiltration` and `foster2025.machine_mode`, so anything listed above is
attributed to both. Left out for that reason: `machine_mode` also solves the pump/headspace system
and reports a bed-throughput minimum and a headspace pressure; `infiltration` also reports bed
water uptake and bed capacity in g. Neither belongs to the other.

## Competing-hypothesis note
Their unsaturated-flow explanation of the fine-grind dip (incomplete wetting =
tubes at k -> 0, an atom the lognormal lacks) must be cited alongside our
channeling closure; time-resolved CT / first-drip timing per grind discriminates.
