import json
import re
from pathlib import Path
from tools import build_espresso_data_guide as guide
from tools import build_local_corpus_family_index as index

ROOT=Path(__file__).resolve().parents[1]


def test_reproducible_projection_and_curated_notes_preserved():
    text=guide.GUIDE.read_text()
    assert guide.render()==text
    changed=text.replace('## Publication and storage','A curated note.\n\n## Publication and storage')
    assert 'A curated note.' in guide.render(changed)
    assert guide.render(guide.render(changed))==guide.render(changed)
    assert len(index.DISCOVERY_NOTES)==39
    assert json.loads(index.OUTPUT.read_text())==index.build()


def test_local_links_and_every_family_discoverable():
    text=guide.GUIDE.read_text()
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if not link.startswith(('http:','https:','#')):
            assert (guide.GUIDE.parent/link.split('#')[0]).exists(),link
    for fid in index.FAMILIES:
        assert f'### {fid}\n' in text
    for path in ['README.md','CLAUDE.md','AGENTS.md','docs/ONBOARDING.md']:
        assert 'ESPRESSO_DATA_GUIDE.md' in (ROOT/path).read_text()


def test_mo_task_note_is_curated_and_survives_rendering():
    text = guide.GUIDE.read_text()
    link = '[SCI-MD-MO-TRANSFER-001](../analysis/sci_md_mo_transfer_001/RESULT.md)'
    note = (
        f'{link} implemented an analysis-only conservative S0/S2/D2 reference '
        'and audited all 51 supplied rows. Both absolute transfer axes remain '
        '`BLOCKED_SOURCE_CONTRACT`; numerical application is separately '
        '`NUMERICALLY_UNRESOLVED`. Original institutional manuscript inspected; '
        'no real fit/score or production integration. Historical reconstruction '
        'remains unchanged.'
    )
    assert text.count(link) == 1
    assert text.count(note) == 1
    for block in re.finditer(r'<!-- (\w+):start -->.*?<!-- \1:end -->', text, re.S):
        assert link not in block.group()
    rendered = guide.render(text)
    assert rendered.count(note) == 1
    assert rendered == text
    assert guide.render(rendered) == rendered


def test_no_private_payload_in_committed_projection():
    snapshot=json.loads((ROOT/'puckworks/data/LOCAL_CORPUS_SNAPSHOT.json').read_text())
    text=json.dumps(snapshot)
    for forbidden in ['/home/','/Users/','relative_path','permission_email','raw_shot','local_path','link_target','header_preview']:
        assert forbidden not in text
    assert set(f['family_id'] for f in snapshot['families'])==set(index.FAMILIES)
    assert snapshot['hashed']<=snapshot['files']
