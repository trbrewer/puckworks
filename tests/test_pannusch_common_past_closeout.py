"""Small native archive checks; no representative campaign fixtures or runs."""
from dataclasses import replace
import hashlib
import json
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_common_past_closeout as closeout
from tools import pannusch_common_past_contrast_verification as runner
from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from test_pannusch_common_past_contrast import inputs, query


@pytest.fixture
def archived_pair(tmp_path):
    c, a, b = inputs(n=3, observations=False)
    result = query(c, a, b)
    values, calls = [], []
    forward = sf.simulate_stateful_fv
    def capture(**kwargs):
        value = forward(**kwargs)
        calls.append(kwargs); values.append(value)
        return value
    with patch.object(sf, 'simulate_stateful_fv', capture):
        receipt = cc._paired_replay(result, result.minimum.witness)
    assert receipt.status == 'CHECKED'
    for label, request, value in zip(('A', 'B'), calls, values):
        directory = tmp_path / label
        directory.mkdir()
        runner._archive_value(directory, 'inputs', request)
        for stage in ('before-transport', 'after-transport', 'after-freeze'):
            runner._archive_value(directory, stage, value)
    def provider():
        index = {str(p.relative_to(tmp_path)): dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in tmp_path.rglob('*') if p.is_file()}
        sources = json.loads((tmp_path / 'A/inputs.json').read_text())['source_sha256']
        return closeout.ArchivePair(closeout.IndexedArchive(tmp_path, index), ('A', 'B'), sources)
    return result, receipt, values, calls, provider


def test_complete_archives_reexecute_checks_and_same_minimum_gap(archived_pair):
    result, original, _, _, make = archived_pair
    provider = make()
    with patch.object(sf, 'simulate_stateful_fv', provider), patch.object(sf.fv, '_evolve', closeout.forbidden), \
            patch.object(pc, 'linprog', closeout.forbidden), patch.object(se, 'linprog', closeout.forbidden):
        replay = cc._paired_replay(result, result.minimum.witness)
        checked = cc._qualify_extremum(result, result.minimum, replay)
    provider.finish()
    expected = cc._qualify_extremum(result, result.minimum, original)
    assert checked.status == expected.status == 'QUALIFIED'
    assert checked.interval_kg == expected.interval_kg and checked.gap_kg == expected.gap_kg
    assert len(provider.used) == 2
    assert all(r['full_report_recomputed'] for r in provider.used)


@pytest.mark.parametrize('change', ['state', 'plan', 'window', 'observation', 'extra'])
def test_request_must_match_exact_archived_execution(archived_pair, change):
    _, _, _, calls, make = archived_pair
    request = dict(calls[0])
    if change == 'state':
        state = request['initial_state']
        request['initial_state'] = replace(state, liquid_cell_average_kg_m3=state.liquid_cell_average_kg_m3 * 1.000001)
    elif change == 'plan':
        request['plan'] = calls[1]['plan']
    elif change == 'window':
        request['fraction_windows_s'] = ((7., 7.1),)
    elif change == 'observation':
        request['observation_times_s'] = (7., 7.1, 7.2)
    else:
        request['stop_time_s'] = 7.2
    provider = make()
    with pytest.raises(ValueError, match='MISMATCH|FIELDS'):
        provider(**request)
    assert not provider.used


def test_pair_rejects_missing_or_extra_requests(archived_pair):
    _, _, _, calls, make = archived_pair
    provider = make()
    provider(**calls[0])
    with pytest.raises(ValueError, match='INCOMPLETE'):
        provider.finish()
    provider(**calls[1]); provider.finish()
    with pytest.raises(ValueError, match='EXTRA'):
        provider(**calls[0])


def test_indexed_bytes_are_checked_before_unpickling(archived_pair, tmp_path):
    _, _, _, calls, make = archived_pair
    provider = make()
    path = tmp_path / 'A/before-transport.pickle'
    path.write_bytes(path.read_bytes() + b'corruption')
    with pytest.raises(ValueError, match='HASH_MISMATCH'):
        provider(**calls[0])


@pytest.mark.parametrize('change', ['future_concentration', 'fraction', 'diagnostics', 'dtype'])
def test_full_report_consistency_not_just_prefix_or_stored_status(archived_pair, change):
    _, _, values, calls, _ = archived_pair
    value = values[0]
    if change in ('future_concentration', 'dtype'):
        c = value.primary.liquid_cell_average_kg_m3.copy()
        c[-1, -1] = np.nextafter(c[-1, -1], np.inf)
        if change == 'dtype':
            c = c.astype(np.float32)
        value = replace(value, primary=replace(value.primary, liquid_cell_average_kg_m3=c))
    elif change == 'fraction':
        f = value.fractions[0]
        value = replace(value, fractions=(replace(f, solute_kg=f.solute_kg * 1.01),))
    else:
        value = replace(value, diagnostics=tuple((k, 'FAIL' if k == 'sampled_admissibility' else v) for k, v in value.diagnostics))
    with pytest.raises(ValueError, match='INCONSISTENCY|DTYPE'):
        closeout.check_complete_report(value, calls[0])


def test_replay_failure_or_excess_gap_is_not_promoted(archived_pair):
    result, receipt, _, _, _ = archived_pair
    bad = cc._qualify_extremum(result, result.minimum, replace(receipt, status='UNRESOLVED'))
    assert bad.status == 'NUMERICALLY_UNRESOLVED' and bad.gap_kg is None
    wide = replace(receipt, combined_interval_kg=(receipt.combined_interval_kg[0], 1.))
    assert cc._qualify_extremum(result, result.minimum, wide).status == 'NUMERICALLY_UNRESOLVED'


def test_source_metadata_and_transport_changes_fail_closed(archived_pair, tmp_path):
    _, _, values, calls, make = archived_pair
    provider = make()
    provider.sources = dict(provider.sources, stateful_fv_py='not-the-executed-source')
    with pytest.raises(ValueError, match='SOURCE_OR_METADATA'):
        provider(**calls[0])
    # Independently indexed, internally hashed outputs can still disagree across
    # the transport boundary. No choice of the favorable stage is permitted.
    changed = replace(values[0], elapsed_wall_s=values[0].elapsed_wall_s + 1.)
    runner._archive_value(tmp_path / 'A', 'after-transport', changed)
    with pytest.raises(ValueError, match='TRANSPORT_OR_FREEZING'):
        make()(**calls[0])


def test_retained_replay_receipts_cannot_be_changed_by_report_assembly():
    from copy import deepcopy
    from types import SimpleNamespace
    row = dict(label='test', **{q: {s: {'witness': {'replay': {'state': 'original'}}}
                                  for s in ('minimum', 'maximum')} for q in ('unconditioned', 'conditioned')})
    prior = dict(levels=[row])
    current = dict(levels=deepcopy(prior['levels']), bindings=[{'minimum_reuse': {'state_identity': str(i)}} for i in range(7)])
    unused = SimpleNamespace(load=lambda _: pytest.fail('no archive needed without a finding'))
    assert closeout.check_reuse_scope(current, prior, unused, {'rows': []})['retained_minimum_receipts_unchanged'] == 7
    current['levels'][0]['conditioned']['minimum']['witness']['replay']['state'] = 'changed'
    with pytest.raises(ValueError, match='RETAINED_REPLAY_RECEIPT_CHANGED'):
        closeout.check_reuse_scope(current, prior, unused, {'rows': []})
