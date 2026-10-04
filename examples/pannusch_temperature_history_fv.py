"""Synthetic offline FV example; small grid, NOT a qualification campaign."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from puckworks.models.pannusch2024.temperature_history_fv import (  # noqa: E402
    TemperatureHistory, FVSettings, simulate_temperature_history_fv,
)

if __name__ == "__main__":
    result = simulate_temperature_history_fv(
        TemperatureHistory.constant_celsius((0, .04, .1), (88, 93)),
        flow_m3_s=2e-6, t_span_s=(0, .1), solute="caffeine", grind=1.7,
        observation_times_s=(0, .04, .07, .1), fraction_bounds_s=(0, .04, .1),
        settings=FVSettings(cells=8))
    print(result.to_json(include_trajectories=False))
