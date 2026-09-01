from puckworks.analysis.ewp_rwb_001_pressure_interface_reconciliation import (
    aggregate_gate, valid_channel,
)


def _pair(parser="Parsers::Gaggiuino", command=None, achieved=None, user="u"):
    hydraulic = {"time__s": [0.0, 1.0]}
    if command is not None: hydraulic["pressure_goal__Pa"] = command
    if achieved is not None: hydraulic["pressure__Pa"] = achieved
    return ({"hashed_user": user, "payload": {"brewdata": {"parser": parser}}},
            {"hydraulic": hydraulic})


def test_validity_uses_normalized_time_and_channel():
    assert valid_channel(_pair(command=[1.0, 2.0])[1], "pressure_goal__Pa")
    assert not valid_channel(_pair(command=[1.0])[1], "pressure_goal__Pa")


def test_pressure_free_family_does_not_pass():
    result = aggregate_gate([_pair(user=str(i % 10)) for i in range(20)])
    assert not result["families"]["VISUALIZER_GAGGIUINO"]["pressure_bearing_gate"]


def test_disclosure_qualified_command_and_achieved_pass_independently():
    command = aggregate_gate([_pair(command=[1.0, 2.0], user=str(i % 10)) for i in range(20)])
    achieved = aggregate_gate([_pair(achieved=[1.0, 2.0], user=str(i % 10)) for i in range(20)])
    assert command["families"]["VISUALIZER_GAGGIUINO"]["pressure_bearing_gate"]
    assert achieved["families"]["VISUALIZER_GAGGIUINO"]["pressure_bearing_gate"]


def test_below_disclosure_and_ambiguous_do_not_pass():
    low = aggregate_gate([_pair(command=[1.0, 2.0], user="one") for _ in range(20)])
    assert not low["families"]["VISUALIZER_GAGGIUINO"]["pressure_bearing_gate"]
    ambiguous = ({"hashed_user": "u", "payload": {"brewdata": {
        "samples": [], "datapoints": []}}}, {"hydraulic": {"time__s": [0.0]}})
    assert aggregate_gate([ambiguous])["ambiguous"] == 1
