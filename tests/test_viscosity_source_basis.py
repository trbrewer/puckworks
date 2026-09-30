"""F15: convert measured kinematic viscosity using the water-fraction density basis."""
from puckworks import data
from puckworks.validation import gates


def test_four_source_gate_uses_water_fraction_for_density(monkeypatch):
    density = data.telisromero_density_kgm3
    calls = []

    def checked_density(temperature_c, water_fraction):
        # The measured Khomyakov overlap is 10–24% dry solids, hence 76–90%
        # water. A dry fraction on the density API inflates every conversion.
        assert 0.76 <= water_fraction <= 0.90
        calls.append((temperature_c, water_fraction))
        return density(temperature_c, water_fraction)

    monkeypatch.setattr(data, 'telisromero_density_kgm3', checked_density)
    result = gates.gate_g10_foursource_spread()
    assert calls
    assert result['khomyakov_above_tr']
