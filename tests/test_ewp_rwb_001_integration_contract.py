from puckworks.data.visualizer.integration_contract import recover_integration


def test_explicit_paths_and_consistency():
    for payload in ({"integration_source": "Parsers::Gaggiuino"},
                    {"integration": "Parsers::Gaggiuino"},
                    {"parser": "Parsers::Gaggiuino"},
                    {"brewdata": {"parser": "Parsers::Gaggiuino"}}):
        assert recover_integration(payload)[0] == "VISUALIZER_GAGGIUINO"
    assert recover_integration({"parser": "Parsers::Gaggiuino", "brewdata": {
        "parser": "Parsers::Gaggiuino"}})[2] == "CONSISTENT_MULTIPLE_EXPLICIT_FIELDS"


def test_conflict_unknown_and_structural():
    assert recover_integration({"parser": "Parsers::Gaggiuino", "brewdata": {
        "parser": "Parsers::Gaggimate"}})[0] == "CONFLICTED"
    assert recover_integration({"parser": "unknown"})[0] == "UNRESOLVED"
    assert recover_integration({"brewdata": {"datapoints": []}})[0] == "VISUALIZER_GAGGIUINO"
    assert recover_integration({"brewdata": {"samples": [], "datapoints": []}})[0] == "AMBIGUOUS"
    assert recover_integration({"brewdata": {"anything": 1}})[0] == "UNRESOLVED"
