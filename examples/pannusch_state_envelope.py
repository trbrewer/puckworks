"""Small public-API-only synthetic example; no empirical state inference.

Run: python examples/pannusch_state_envelope.py
Concentration: kg/m^3, delivery: kg. RESEARCH_ONLY.
Source-derived outputs: Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0, separately from first-party code. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
"""
import json

import numpy as np

from puckworks.models.pannusch2024.stateful_fv import (
    FVChemicalState, FVPlan, FVSettings, FlowHistory, TemperatureHistory,
)
from puckworks.models.pannusch2024.state_envelope import (
    FVChemicalStateSet, build_delivery_response, bound_delivery,
    contrast_deliveries, replay_extrema,
)


def main():
    settings = FVSettings(cells=4)
    t, duration = 7., .11
    a = FVPlan(TemperatureHistory.linear_celsius(
        (t, t+.4*duration, t+duration), (80, 96, 87)),
        FlowHistory((t, t+.3*duration, t+duration), (1.2e-6, 2.7e-6, 1.8e-6), 'linear'),
        (t, t+duration), settings)
    b = FVPlan(TemperatureHistory.linear_celsius(
        (t, t+.25*duration, t+duration), (96, 84, 92)),
        FlowHistory((t, t+duration), (2.16e-6,), 'constant'), (t, t+duration), settings)
    edges = np.linspace(0., .015, 5)  # explicit source geometry, metres
    x = (edges[:-1]+edges[1:])/(2*.015)
    lower = np.array([.2+.5*x, .2+.4*x, .5+.3*x])
    upper = np.array([3+3*x, 8-3*x, 8+2*x])
    bounds = [FVChemicalState.from_cell_averages(solute='caffeine', grind=1.7,
        time_s=t, edges_m=edges, liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
        for c in (lower, upper)]
    states = FVChemicalStateSet(bounds[0], bounds[1], (8e-5, 1.2e-4),
        'SYNTHETIC_EXAMPLE; explicit assumed bounds, not a measured coffee state',
        ((8e-6, 3e-5), (1e-5, 5e-5), (2e-5, 8e-5)))
    responses = [build_delivery_response(p, solute='caffeine', window_s=(t, t+duration))
                 for p in (a, b)]
    envelopes = [replay_extrema(bound_delivery(states, r, epsilon_kg=1e-9)) for r in responses]
    contrast = replay_extrema(contrast_deliveries(states, *responses, epsilon_kg=1e-9,
        delta_kg=1e-6, comparison_basis='MATCHED_COLLECTED_VOLUME'))
    print(json.dumps(dict(envelopes=[json.loads(r.to_json()) for r in envelopes],
        contrast=json.loads(contrast.to_json())), sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
