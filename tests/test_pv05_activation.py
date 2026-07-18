"""PV-05 activation guards (Section 11): the live-link references and the generated-data-hash binding.

Offline. These fail if the public surfaces stop pointing at the deployed model-composition story, if
the deployed site data drifts from the packaged snapshot, or if the recorded acceptance hash no longer
matches the artifact it certifies.
"""
import hashlib
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_URL = "https://trbrewer.github.io/puckworks/model-composition/"
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv05_model_composition.json"
SITE_DATA = _ROOT / "docs" / "public" / "site" / "model-composition" / "data.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_public_surfaces_link_the_live_model_composition_story():
    readme = (_ROOT / "README.md").read_text(encoding="utf-8")
    assert _URL in readme, "README must link the live model-composition interactive"
    assert "do not simply add up" in readme.lower()
    pub = (_ROOT / "docs" / "public" / "README.md").read_text(encoding="utf-8")
    assert _URL in pub and "PV-05" in pub
    land = (_ROOT / "docs" / "public" / "site" / "index.html").read_text(encoding="utf-8")
    assert 'href="model-composition/"' in land


def test_site_data_matches_packaged_snapshot_hash():
    # the deployed data.json is byte-identical to the packaged, producer-bound snapshot
    assert SITE_DATA.read_bytes() == SNAPSHOT.read_bytes()
    assert _sha(SITE_DATA) == _sha(SNAPSHOT)


def test_status_records_pv05_live_with_the_artifact_hash():
    items = {it["id"]: it
             for it in json.loads((_ROOT / "docs" / "status" / "current.json").read_text())["items"]}
    pv05 = items["pv05-model-composition"]
    assert pv05["state"] == "complete"
    assert pv05["verified_commit"] and pv05["verified_date"]
    # the recorded acceptance hash must match the artifact it certifies (drift-proof)
    assert _sha(SNAPSHOT) in pv05["acceptance_evidence"], "acceptance hash != live snapshot hash"
    # PV-04 is now the active public-value lane
    assert items["pv04-analysis-autopsy"]["state"] == "active"
