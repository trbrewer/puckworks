"""Synthetic checks only: no original chemistry, model fits, or scoring."""

from decimal import Decimal

import pytest

from tools import pw_cup_time_increment_001_phase0 as phase0


def synthetic_source():
    # All non-selected payloads are deliberately invalid, including chemistry,
    # the excluded shots, the extra block, and terminal columns.
    for shot in range(1, 15):
        selected = shot in phase0.PRIMARY_SHOTS
        for label in phase0.ROW_LABELS:
            if selected and label == "Vial No.":
                fields = [str(i) for i in range(1, 17)]
            elif selected and label == "Weight":
                fields = ["0", "0"] + ["1.003"] * 14
            else:
                fields = ["FORBIDDEN_FIELD"] * 16
            yield label + "," + ",".join(fields + ["FORBIDDEN_TERMINAL"]) + "\n"
        yield ",,,,\n"


def test_mass_only_never_parses_tds_fields(monkeypatch):
    original_reader = phase0.csv.reader
    seen = []

    def guarded_reader(lines, *args, **kwargs):
        lines = list(lines)
        for line in lines:
            label = line.partition(",")[0]
            assert label in ("Vial No.", "Weight"), "non-mass fields accessed"
            seen.append(label)
        return original_reader(lines, *args, **kwargs)

    monkeypatch.setattr(phase0.csv, "reader", guarded_reader)
    windows = phase0.mass_windows(synthetic_source())
    result = phase0.endpoint_summary(windows)
    assert tuple(windows) == phase0.PRIMARY_SHOTS
    assert len(seen) == 22
    assert [Decimal(r["mass_g"]) for r in result] == [
        Decimal("14.0"), Decimal("7.0"), Decimal("10.50")
    ]
    assert result[0]["duration_min_s"] == pytest.approx(4 + 2 * 14 / 1.003)


def test_activation_delay_zero_mass_and_exact_crossing_boundary():
    masses = tuple(map(Decimal, ("0", "0", "2", "0", "3")))
    assert phase0.duration_at_mass(masses, Decimal("1")) == 5
    assert phase0.duration_at_mass(masses, Decimal("2")) == 6
    assert phase0.duration_at_mass(masses, Decimal("3.5")) == 9
    with pytest.raises(ValueError, match="exceeds"):
        phase0.duration_at_mass(masses, Decimal("5.1"))


def test_minimum_total_not_mean_sets_endpoint():
    windows = {shot: (Decimal("0"),) * 15 + (Decimal("12.37"),)
               for shot in phase0.PRIMARY_SHOTS}
    windows[1] = (Decimal("0"),) * 15 + (Decimal("10.19"),)
    result = phase0.endpoint_summary(windows)
    assert [Decimal(r["mass_g"]) for r in result] == [
        Decimal("10.1"), Decimal("5.05"), Decimal("7.575")
    ]
    assert result[0]["duration_max_s"] == pytest.approx(30 + 2 * 10.1 / 10.19)


def test_source_hash_checked_before_mass_access(tmp_path, monkeypatch):
    bad = tmp_path / "exp13.csv"
    bad.write_text("NOT_THE_PINNED_SOURCE")
    monkeypatch.setattr("sys.argv", ["phase0", "--source", str(bad)])

    def forbidden(*args):
        pytest.fail("mass reader reached before source authentication")

    monkeypatch.setattr(phase0, "mass_windows", forbidden)
    with pytest.raises(SystemExit, match="SHA-256 mismatch"):
        phase0.main()
