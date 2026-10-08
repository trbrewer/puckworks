"""Ordinary policy, signed-algebra and serialization QA; no canonical trajectories."""
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from puckworks.analysis import grudeva2026_baseline_observation_005_attribution as attribution
from puckworks.analysis import grudeva2026_baseline_observation_005_report as report


def test_full_cell_amounts_and_partial_polynomial_integrals():
    faces = np.array([0., .1, .3, .6, 1.])
    a, b = faces[:-1], faces[1:]
    averages = 2+(a*a+a*b+b*b)/3
    mean, pieces = attribution.project_cell(faces, averages, .05, .8)
    assert mean == pytest.approx(2+(.05**2+.05*.8+.8**2)/3, abs=3e-14)
    assert sum(p['whole_cell'] for p in pieces) == 2
    for piece in pieces:
        if piece['whole_cell']:
            assert piece['amount'] == averages[piece['cell']]*(piece['right']-piece['left'])
    with pytest.raises(ValueError, match='common physical support'):
        attribution.project_cell(faces, averages, .9, 1.001)


def test_signed_scalar_and_cell_average_nonadditivity():
    values = dict(bed_fine=.3, modes_fine=-.2, time_fine=.1, combined=.25)
    assert attribution.signed_interactions(values) == pytest.approx(.05)
    vectors = {k:np.array([v, -2*v, 3*v]) for k,v in values.items()}
    assert attribution.signed_interactions(vectors) == pytest.approx([.05,-.1,.15])


@pytest.mark.parametrize('damage', [None, 'diagnostics', 'status', 'unavailable_reason', 'environment'])
def test_control_requires_complete_result_and_environment(tmp_path, monkeypatch, damage):
    public = dict(parameters={'p':1}, controls={'n':2}, events=[1.], diagnostics={'residual':0.},
                  status='COMPLETED', unavailable_reason=None)
    normal = dict(public_result=public, public_result_sha256=obs.digest(public), environment={'python':'same'})
    path = tmp_path/'normal.json'; path.write_text(obs.canonical(normal))
    binding = dict(file=path.name, sha256=obs.sha(path))
    candidate = obs.read_json(path)
    candidate.update(row='control', observed=False)
    if damage == 'environment':
        candidate['environment'] = {'python':'other'}
    elif damage:
        candidate['public_result'][damage] = 'different'
        candidate['public_result_sha256'] = obs.digest(candidate['public_result'])
    output = tmp_path/'control.json'; output.write_text(obs.canonical(candidate))
    monkeypatch.setattr(report, 'check_run', lambda *args: [])
    check = attribution.run_check(output, candidate, None, {'attribution':{'normal_binding':binding}}, 'matrix')
    assert check['neutrality']['passed'] == (damage is None)
    assert check['safe_to_continue'] == (damage is None)
    assert check['qualification_override'] is False


def test_partial_output_survives_unserializable_next_stage(tmp_path):
    path = tmp_path/'diagnostic.json'
    attribution.checkpoint(path, {'stage':'saved'})
    before = path.read_bytes()
    with pytest.raises(ValueError):
        attribution.checkpoint(path, {'bad':float('nan')})
    assert path.read_bytes() == before


def policy_archive(tmp_path):
    helper = runpy.run_path(str(Path(__file__).with_name('test_grudeva2026_baseline_observation_005_resources.py')))
    folder, _ = helper['archive'](tmp_path)
    old = obs.sha(folder/'invoke.py')
    for name in ('invoke-before-persistence.py','invoke-before-attribution.py'):
        (folder/name).write_bytes((folder/'invoke.py').read_bytes())
    for name in ('invocations-before-persistence-controller.jsonl','invocations-before-attribution.jsonl'):
        (folder/name).write_bytes((folder/'invocations.jsonl').read_bytes())
    persistence = dict(previous_controller_sha256=old, controller_sha256=old,
        resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'),
        historical_ledger_sha256=obs.sha(folder/'invocations-before-persistence-controller.jsonl'))
    (folder/'persistence-amendment.json').write_text(obs.canonical(persistence))
    binding = dict(previous_controller_sha256=old, controller_sha256=old, policy=report.ATTRIBUTION_POLICY,
        short_limit=21, historical_short_limit=20, attempts=list(report.ATTRIBUTION_ATTEMPTS),
        memory_bytes=8*1024**3, historical_ledger_sha256=obs.sha(folder/'invocations-before-attribution.jsonl'),
        persistence_amendment_sha256=obs.sha(folder/'persistence-amendment.json'))
    (folder/'attribution-amendment.json').write_text(obs.canonical(binding))
    return folder


@pytest.mark.parametrize('damage', [None, 'larger_limit', 'policy', 'controller', 'history', 'unresolved', 'wrong_attempt'])
def test_short_extension_is_exact_and_history_bound(tmp_path, damage):
    folder = policy_archive(tmp_path)
    file = folder/'attribution-amendment.json'
    binding = obs.read_json(file)
    if damage in ('larger_limit','policy','controller','history'):
        key, value = {'larger_limit':('short_limit',22), 'policy':('policy','arbitrary'),
                      'controller':('previous_controller_sha256','wrong'),
                      'history':('historical_ledger_sha256','wrong')}[damage]
        binding[key] = value;file.write_text(obs.canonical(binding))
    elif damage:
        name = 'attribution-control' if damage == 'unresolved' else 'unapproved-pilot'
        row = dict(event='start', name=name, kind='full', phase='final', time_ceiling=300, memory_bytes=8*1024**3)
        with (folder/'invocations.jsonl').open('a') as stream:
            stream.write(json.dumps(row)+'\n')
    audit = report.resource_audit(folder)
    assert audit['passed'] == (damage is None), audit['reasons']
    if damage is None:
        assert audit['remaining_short'] == 20  # one manufactured historical short, ceiling21


@pytest.mark.parametrize('name,kind', [('attribution-bed_fine','full'), ('attribution-reduction','short'),
                                     ('normal-recapture','full'), ('pilot','short')])
def test_controller_cannot_bypass_named_order(tmp_path, name, kind):
    folder = policy_archive(tmp_path)
    allocation = folder/'allocation.json'
    allocation.write_text(obs.canonical(dict(attempt=name, kind=kind,
        controller_sha256=obs.sha(folder/'invoke.py'),
        resource_amendment_sha256=obs.sha(folder/'resource-amendment.json'))))
    controller = runpy.run_path(str(folder/'invoke.py'))
    before = (folder/'invocations.jsonl').read_bytes()
    with pytest.raises(AssertionError):
        controller['main']([name,kind,'final','never-execute','--allocation',str(allocation),'--output',str(folder/'no.json')])
    assert (folder/'invocations.jsonl').read_bytes() == before


@pytest.mark.parametrize('bad_support', [False, True])
def test_retained_accuracy_failure_is_not_a_qualification_override(tmp_path, monkeypatch, bad_support):
    normal_path = tmp_path/'normal.json'
    normal_path.write_text(obs.canonical({'environment':{'python':'same'}}))
    output = tmp_path/'bed.json';output.write_text('{}')
    output.with_name('bed-observations.json').write_text('{}')
    gates = {k: True for k in ('complete_status','solver_segments','horizon','events','activation_support',
        'required_times','independent_inventory_sums','public_inventory_algebra','public_profile_reconstruction',
        'public_cup_outlet_reconstruction','tail_weights_rates','cup_quadrature')}
    gates.update(diagnostic_inlet=False, conservation=False)
    if bad_support:
        gates['horizon'] = False
    monkeypatch.setattr(report,'numeric_gates',lambda *args:gates)
    monkeypatch.setattr(report,'check_run',lambda *args:[])
    meta = dict(row='bed_fine',environment={'python':'same'},segments=[])
    plan = {'attribution':{'normal_binding':dict(file='normal.json',sha256=obs.sha(normal_path))}}
    result = attribution.run_check(output,meta,{'audits':{}},plan,'matrix')
    assert result['safe_to_continue'] == (not bad_support)
    assert result['gates']['diagnostic_inlet'] is False and result['qualification_override'] is False
    assert result['retained_accuracy_failures'] == ['diagnostic_inlet','conservation']
