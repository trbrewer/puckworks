"""Small synthetic set-valued inverse query; no real-data scoring.

RESEARCH_ONLY / PHYSICAL_VALIDATION=NOT_ESTABLISHED. Engineering allowances,
not rigorous interval arithmetic, statistical confidence or physical bounds.
Source-derived output CC-BY-NC-3.0, Pannusch/Schmieder 10.17632/y2tz67f6ry.1;
first-party code licensing is separate.

Run: python -m examples.pannusch_prefix_conditioned
"""
import numpy as np

from puckworks.models.pannusch2024 import prefix_conditioned as pc, state_envelope as se, stateful_fv as sf


def main():
    n = 4
    plan = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7., 7.13, 7.3), (80, 95, 87)),
        sf.FlowHistory((7., 7.09, 7.3), (1.2e-6, 2.7e-6, 1.8e-6), 'linear'),
        (7., 7.3), sf.FVSettings(cells=n, h_max_s=.02))
    def state(value):
        return sf.FVChemicalState.from_cell_averages(solute='caffeine', grind=1.7, time_s=7.,
            edges_m=np.linspace(0., .015, n+1), liquid_kg_m3=np.full(n, value),
            fine_kg_m3=np.full(n, 3*value), coarse_kg_m3=np.full(n, 2*value))
    u = se.FVChemicalStateSet(state(1.), state(2.), (0., 2e-4), 'EXPLICIT_SYNTHETIC_BOX')
    early = se.build_delivery_response(plan, solute='caffeine', window_s=(7., 7.1))
    target = se.build_delivery_response(plan, solute='caffeine', window_s=(7.1, 7.3))
    # Already specified kg band, intentionally broad. This illustrates that
    # qualified yet uninformative conditioning is a legitimate outcome.
    obs = pc.FVFractionObservation('early', early, (0., u.inventory_scale_kg),
                                  'SYNTHETIC_BROAD_MASS_BAND_NOT_ASSAY_PRECISION')
    joint = pc.condition_on_fractions(u, plan, (obs,))
    bounds = pc.bound_future_delivery(joint, target, epsilon_kg=1e-9)
    checked = pc.replay_conditioned_extrema(bounds)
    print(checked.to_json())


if __name__ == '__main__':
    main()
