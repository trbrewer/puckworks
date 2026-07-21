"""Repository-truth checks tied to the audited relay reference result (§15.8).

Keeps the README / relay-doc public counts and taxonomy honest: they must match the reference run, and the
public-path list count must match the number of listed paths.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def readme():
    return (REPO / "README.md").read_text(encoding="utf-8")


def test_public_path_number_matches_the_list(readme):
    m = re.search(r"(Four|Five|Six|Seven) public paths \(no local setup required\):", readme)
    assert m, "public-paths intro not found"
    words = {"Four": 4, "Five": 5, "Six": 6, "Seven": 7}
    claimed = words[m.group(1)]
    # count the bullet items in THIS list only — stop at the first non-blank, non-bullet paragraph line
    tail = readme.split(m.group(0), 1)[1]
    listed = 0
    for ln in tail.splitlines():
        if ln.startswith("- **"):
            listed += 1
        elif ln.strip() == "":
            continue
        else:
            break
    assert claimed == listed, f"README claims {claimed} public paths but lists {listed}"


@pytest.mark.slow
def test_readme_relay_counts_match_the_reference_result(readme):
    from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull
    r = execute_illustrative_linked_pull(RelayRequest(mode="fast"))
    c = r["counts"]
    assert f"{c['components_executed']} components" in readme
    assert f"{c['cross_component_handoffs']} explicit" in readme


def test_readme_keeps_the_relay_distinct_from_a_validated_coupled_model(readme):
    low = readme.lower()
    assert "not a validated coupled simulation" in low
    assert "no registered component is currently validated as a universal whole-process coupled" in low
    # the four distinct experiences remain named
    for name in ("Full Laboratory Tour", "Espresso Model Relay", "quickstart", "Guided Espresso Pull"):
        assert name in readme
