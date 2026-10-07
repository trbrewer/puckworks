"""Small standalone synthetic B_MINUS_A example; no private data or fitted state.

Run: python examples/pannusch_common_past_contrast.py
"""
from __future__ import annotations

import json
import numpy as np

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf


def main():
    n = 4
    times = (7., 7.1, 7.2)
    plans = tuple(sf.FVPlan(sf.TemperatureHistory.linear_celsius(times, t),
        sf.FlowHistory(times, q, 'constant'), (7., 7.2), sf.FVSettings(cells=n, h_max_s=.02))
        for t, q in (((90, 90, 86), (2e-6, 1.5e-6)), ((90, 90, 94), (2e-6, 2.5e-6))))
    def state(scale):
        return sf.FVChemicalState.from_cell_averages(solute='caffeine', time_s=7.,
            edges_m=np.linspace(0., .015, n+1), liquid_kg_m3=np.full(n, scale),
            fine_kg_m3=np.full(n, 2*scale), coarse_kg_m3=np.full(n, 3*scale))
    u = se.FVChemicalStateSet(state(.5), state(1.), (0., 1e-3), 'EXPLICIT_SYNTHETIC_NOT_COFFEE_PRIOR')
    early = se.build_delivery_response(plans[0], solute='caffeine', window_s=(7., 7.1))
    obs = pc.FVFractionObservation('early', early, (0., 1e-6), 'SUPPLIED_SYNTHETIC_BAND_NOT_ASSAY_PRECISION')
    a, b = (se.build_delivery_response(p, solute='caffeine', window_s=(7.1, 7.2)) for p in plans)
    result = cc.replay_common_past_extrema(cc.bound_common_past_contrast(
        pc.condition_on_fractions(u, plans[0], (obs,)), a, b, branch_time_s=7.1,
        epsilon_kg=1e-9, delta_kg=1e-6, comparison_basis='EXPLICIT_UNEQUAL_VOLUME'))
    print(json.dumps(dict(orientation=result.orientation, interval_kg=result.outer_interval_kg,
        compatibility=result.compatibility, bounds=result.bounds, decision=result.decision,
        common_past_receipt=result.receipt.identity_sha256, PHYSICAL_VALIDATION='NOT_ESTABLISHED'),
        indent=2, allow_nan=False))
    return 0 if result.bounds == 'QUALIFIED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
