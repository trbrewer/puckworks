"""Synthetic, offline small-mesh demonstration; not full-bed qualification.

Run: python examples/pannusch_temperature_history.py
Requires only the installed package's NumPy/SciPy dependencies and parameter
summaries. Output is kg/m^3, kg and m^3; not yield, TDS percent or taste.
Pannusch et al., Mendeley 10.17632/y2tz67f6ry.1; source-derived outputs CC-BY-NC-3.0.
"""
from puckworks.models.pannusch2024.temperature_history import (
    TemperatureHistory, TemperatureHistorySettings, simulate_temperature_history,
)


def main():
    history = TemperatureHistory.constant_celsius([0, 1, 2, 3], [88, 93, 86])
    result = simulate_temperature_history(
        history, flow_m3_s=2e-6, t_span_s=(0, 3), solute="caffeine", grind=1.7,
        observation_times_s=(0, 1, 2, 3), fraction_bounds_s=(1, 2, 3),
        settings=TemperatureHistorySettings(nz=12),
    )
    print(result.to_json(include_trajectories=False))
    assert result.integration_complete


if __name__ == "__main__":
    main()
