"""maille2024 — early-time (<30 s) two-regime batch extraction kinetics + a PSD->fast-fraction
closure (card `docs/cards/maille2024.md`).

Registered as TWO calibration components, matching the two distinct roles the card's Interface
mapping names — a component is per-stage, and these sit on different stages:

  * `maille2024.phi_closure`  (grind)      — Eqs 6.7-6.9: phi = theta_v,fines + theta_v,coarse,
    predicted a priori from a measured binned PSD. This is the piece with runtime-adjacent value:
    a parameter-free prior on cameron2020.extraction_bdf's *fitted* two-population split.
  * `maille2024.two_regime`   (extraction) — Eqs 6.1/6.2: the two-exponential kinetics and the
    per-material/per-species lambda_fast, lambda_slow tables (timescale priors + gate provider).

BOTH are `calibration`, never runtime (card "Kind justification"): the model has no bed, no
pressure and no flow variable to couple through, and its dilute/K=1 assumption is violated in
espresso. It produces normalized per-species curves and NOTHING in ShotResultState — no EY, no TDS.
"""
from puckworks.models.maille2024 import phi_closure, two_regime  # noqa: F401
