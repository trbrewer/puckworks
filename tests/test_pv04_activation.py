"""PV-04 activation guards (Section 11): the live-link references and the generated-data-hash binding.

Offline. These fail if the public surfaces stop pointing at the deployed analysis-autopsy story, if the
deployed site data drifts from the packaged snapshot, if the recorded acceptance hash no longer matches
the artifact it certifies, or if stale "active / next / queued" wording survives in the authoritative
current-state sections. Mirrors tests/test_pv05_activation.py.
"""
import hashlib
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_URL = "https://trbrewer.github.io/puckworks/analysis-autopsy/"
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv04_analysis_autopsy.json"
SITE_DATA = _ROOT / "docs" / "public" / "site" / "analysis-autopsy" / "data.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_public_surfaces_link_the_live_analysis_autopsy_story():
    readme = (_ROOT / "README.md").read_text(encoding="utf-8")
    assert _URL in readme, "README must link the live analysis-autopsy interactive"
    assert "falsified our own espresso headline" in readme.lower()
    pub = (_ROOT / "docs" / "public" / "README.md").read_text(encoding="utf-8")
    assert _URL in pub and "PV-04" in pub
    assert "public.analysis_autopsy.pv04_values" in pub          # the producer is listed
    land = (_ROOT / "docs" / "public" / "site" / "index.html").read_text(encoding="utf-8")
    assert 'href="analysis-autopsy/"' in land                    # landing page retains the relative link


def test_readme_does_not_imply_universal_grinder_behaviour():
    readme = (_ROOT / "README.md").read_text(encoding="utf-8").lower()
    # the live description must keep the dial-scope / non-portability caveat and avoid a universal claim
    assert "dial is not a particle size" in readme or "not a particle size" in readme
    assert "universal too-fine" not in readme and "universal optimum" not in readme


def test_site_data_matches_packaged_snapshot_hash():
    # the deployed data.json is byte-identical to the packaged, producer-bound snapshot
    assert SITE_DATA.read_bytes() == SNAPSHOT.read_bytes()
    assert _sha(SITE_DATA) == _sha(SNAPSHOT)


def test_status_records_pv04_live_with_the_artifact_hash():
    items = {it["id"]: it
             for it in json.loads((_ROOT / "docs" / "status" / "current.json").read_text())["items"]}
    pv04 = items["pv04-analysis-autopsy"]
    assert pv04["state"] == "complete"
    assert pv04["verified_commit"] and pv04["verified_date"]
    assert pv04["next_gate"] is None
    ev = pv04["acceptance_evidence"]
    # the recorded acceptance hash must match the artifact it certifies (drift-proof)
    assert _sha(SNAPSHOT) in ev, "acceptance hash != live snapshot hash"
    # the deployment provenance is recorded
    assert _URL in ev and "29663302756" in ev and "238714b" in ev
    # PV-05 stays complete/live; no new lane silently activated
    assert items["pv05-model-composition"]["state"] == "complete"


def test_no_stale_active_or_next_wording_in_authoritative_state():
    # authoritative current-state surfaces must not still call PV-04 active/next or queued behind PV-05
    for rel in ("docs/status/current.json", "docs/planning/STATE_OF_TRUTH.md",
                "docs/public/README.md"):
        low = (_ROOT / rel).read_text(encoding="utf-8").lower()
        assert "queued behind pv-05" not in low, f"stale 'queued behind PV-05' in {rel}"
    # the pv04 item itself must not describe PV-04 as the active/next lane any more
    pv04 = next(it for it in json.loads((_ROOT / "docs" / "status" / "current.json").read_text())["items"]
                if it["id"] == "pv04-analysis-autopsy")
    blob = json.dumps(pv04).lower()
    assert "queued behind pv-05" not in blob
    assert pv04["state"] != "active"
