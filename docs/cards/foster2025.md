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

## Competing-hypothesis note
Their unsaturated-flow explanation of the fine-grind dip (incomplete wetting =
tubes at k -> 0, an atom the lognormal lacks) must be cited alongside our
channeling closure; time-resolved CT / first-drip timing per grind discriminates.
