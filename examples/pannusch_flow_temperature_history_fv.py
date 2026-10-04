"""Offline N=8 illustration only; no empirical or campaign accuracy claim."""
from puckworks.models.pannusch2024.flow_temperature_history_fv import (
    FlowHistory, TemperatureHistory, FVSettings, simulate_flow_temperature_history_fv,
)

if __name__ == '__main__':
    result = simulate_flow_temperature_history_fv(
        TemperatureHistory.linear_celsius((0, .04, .1), (80, 90, 98)),
        flow_history=FlowHistory((0, .03, .1), (1e-6, 3e-6), 'constant'),
        t_span_s=(0, .1), solute='caffeine', observation_times_s=(0, .015, .03, .06, .1),
        fraction_bounds_s=(0, .03, .07, .1), settings=FVSettings(cells=8),
    )
    print(result.to_json(include_trajectories=False))
