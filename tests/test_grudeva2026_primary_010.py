"""Primary-data survival and exact derived checks; solver-free controls."""
import json

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_full_reference_010_io as io
from test_grudeva2026_full_reference_010 import _synthetic_archive


@pytest.mark.parametrize('secondary_failure', [False, True])
def test_derived_failure_preserves_primary(tmp_path, monkeypatch, secondary_failure):
    construct = io.concentration_blocks
    observed = {}
    def wrong(t, y):
        path = tmp_path/'archive'
        # All primary coefficients must already be verifiable when derivation begins.
        receipt = io.verify_primary_archive(path)
        observed['receipt'] = receipt
        observed['identities'] = {p.name: io.sha256(p) for p in path.glob('*.npy')}
        assert not (path/'manifest.json').exists()
        result = construct(t, y)
        result[1, 3] += 1.
        return result
    monkeypatch.setattr(io, 'concentration_blocks', wrong)
    with pytest.raises(io.CaptureMismatch) as caught:
        _synthetic_archive(tmp_path)
    if secondary_failure:
        def broken(*args):
            raise RuntimeError('injected witness failure')
        monkeypatch.setattr(io, 'byte_difference', broken)
    saved = io.persist_capture_failure(tmp_path/'failure', caught.value)
    record = json.loads((tmp_path/'failure/FAILURE.json').read_text())
    assert record['component'] == 'concentrations'
    assert record['archive_group'] == 'segment-0'
    assert record['block'] == [0, 3] and record['time_range'] == [1., 1.2]
    assert record['expected']['shape'] == record['observed']['shape'] == [3, 21]
    assert record['expected']['dtype'] == record['observed']['dtype'] == '<f8'
    assert record['expected']['sha256'] != record['observed']['sha256']
    assert record['identity_matches'] is False and record['sources_stable'] is True
    if not secondary_failure:
        witness = json.loads((tmp_path/'failure/witness-0.json').read_text())
        assert witness['first_index'] == [1, 3]
        assert witness['differing_entries'] == 1
        assert np.load(tmp_path/'failure/witness-0-source.npy')[24] != np.load(tmp_path/'failure/witness-0-target.npy')[24]
    else:
        assert saved['errors'] and 'witness failure' in saved['errors'][0]
    path = tmp_path/'archive'
    assert io.verify_primary_archive(path) == observed['receipt']
    assert {p.name: io.sha256(p) for p in path.glob('*.npy')} == observed['identities']
    assert not (path/'manifest.json').exists()
    if not secondary_failure:
        from tools.run_grudeva2026_full_reference_010 import fresh_read
        fresh_read(path, 'primary')
        receipt = json.loads((path/'primary-fresh-read.json').read_text())
        assert receipt['status'] == 'PASS'
        assert receipt['primary_receipt_sha256'] == io.sha256(path/'PRIMARY_INCOMPLETE.json')
        assert not (path/'manifest.json').exists()
    with pytest.raises(FileNotFoundError):
        io.load_archive(path)


def test_primary_reader_rejects_changed_payload(tmp_path):
    path, _, _ = _synthetic_archive(tmp_path)
    io.verify_primary_archive(path)
    member = path/'segment-0-D.npy'
    with member.open('r+b') as stream:
        stream.seek(-1, 2)
        byte = stream.read(1)
        stream.seek(-1, 2)
        stream.write(bytes([byte[0] ^ 1]))
    with pytest.raises(ValueError, match='Primary saved payload'):
        io.verify_primary_archive(path)
