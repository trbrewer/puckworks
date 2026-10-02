"""Synthetic reporting negative paths; these are not solver observations."""
import dataclasses
import json

import pytest

from puckworks.models.grudeva2026 import __main__ as cli
from puckworks.models.grudeva2026.reduced import Result


@pytest.mark.parametrize('case,refine,expected,exit_code', [
    ('quick_failure', False, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('populated_failure', False, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('numerical_error', False, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('unsupported', False, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('empty_inventory', False, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('unsupported', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('quick_failure', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('fine_gate_failure', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('refinement_failure', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('empty_completed', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('grid_mismatch', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('no_smooth_samples', True, 'NUMERICAL_VERIFICATION_FAILED', 1),
    ('success', False, 'SINGLE_RUN_COMPLETE_REFINEMENT_NOT_ASSESSED', 0),
    ('success', True, 'GRUDEVA2026_STANDALONE_NUMERICALLY_VERIFIED_REFERENCE_INCOMPLETE', 0),
])
def test_cli_qualification_precedes_execution_mode(monkeypatch, tmp_path, capsys,
                                                  case, refine, expected, exit_code):
    from puckworks.product import lab_reference_producers

    reason = 'Synthetic negative-path fixture; not a solver observation'
    figures = {'figure3': {'status': 'FAIL'}, 'figure4': {'status': 'FAIL'},
               'figure5': {'status': 'FIG5_REFERENCE_INCOMPLETE', 'reason': 'No qualified arrays'}}
    calls = []

    def producer(*, parameters, controls):
        result = Result('COMPLETED', dataclasses.asdict(parameters), dataclasses.asdict(controls),
                        time=[0., 1., 2., 3.], outlet_concentration=[0., 1., .5, .2],
                        cumulative_discharged_solute=[0., 0., .7, 1.],
                        events={'first_drip': 1., 'desaturation_exit': 1.5},
                        inventories={'initial': 4., 'external_liquid': [0., .1, .2, .1]})
        if case == 'populated_failure':
            result = dataclasses.replace(result, status='NUMERICAL_VERIFICATION_FAILED',
                                         unavailable_reasons={'boundedness': reason})
        elif case in ('unsupported', 'numerical_error', 'empty_inventory'):
            result = Result('NUMERICAL_FAILURE' if case == 'numerical_error' else 'UNSUPPORTED_REGIME',
                            result.parameters, result.controls, unavailable_reasons={'simulation': reason})
            if case == 'empty_inventory':
                result = dataclasses.replace(result, inventories={'external_liquid': []})
        elif case == 'refinement_failure' and controls.cells == 256:
            result = dataclasses.replace(result, outlet_concentration=[0., 1., .51, .2])
        elif case == 'empty_completed':
            result = Result('COMPLETED', result.parameters, result.controls)
        elif case == 'grid_mismatch' and controls.cells == 256:
            result = dataclasses.replace(result, time=[0., 1., 2., 4.])
        elif case == 'no_smooth_samples':
            result = dataclasses.replace(result, time=[1.48, 1.49, 1.51, 1.52])
        failed_gate = case == 'quick_failure' or (case == 'fine_gate_failure' and controls.cells == 256)
        gate = {'passed': not failed_gate, 'evidence_strength': 'code_verification',
                'metrics': {}, 'publication_reproduction': 'NOT_EARNED_BY_THIS_QUICK_GATE',
                'physical_validation': 'NOT_ESTABLISHED'}
        if failed_gate:
            gate['reason'] = reason
        calls.append(result.to_dict())
        return {'scientific_result': result.to_dict(), 'gate_verdict': gate,
                'reference_qualification': figures}

    monkeypatch.setattr(lab_reference_producers, 'grudeva2026_reference_summary', producer)
    destination = tmp_path / 'report.json'
    args = ['--output', str(destination)] + (['--refine'] if refine else [])
    assert cli.main(args) == exit_code
    assert capsys.readouterr().out.strip() == expected
    report = json.loads(destination.read_text())
    assert report['disposition'] == expected
    assert report['physical_validation'] == 'NOT_ESTABLISHED'
    assert report['publication_references'] == figures
    assert 'numerical' in report['verification_scope'].lower()
    assert 'publication reproduction' in report['verification_scope'].lower()
    assert bool(report['numerical_failure_reasons']) == bool(exit_code)
    if case in ('populated_failure', 'unsupported', 'numerical_error', 'empty_inventory'):
        assert report['runs']['normal']['status'] == calls[0]['status']
        assert report['runs']['normal']['unavailable_reasons'] == calls[0]['unavailable_reasons']
        assert reason in json.dumps(report['numerical_failure_reasons'])
    if case in ('quick_failure', 'fine_gate_failure'):
        assert reason in json.dumps(report['numerical_failure_reasons'])
    if case == 'refinement_failure':
        assert not report['refinement']['space_fine']['passed']
        assert 'space_fine' in json.dumps(report['numerical_failure_reasons'])
    if case in ('empty_completed', 'grid_mismatch', 'no_smooth_samples'):
        assert not report['refinement']['space_fine']['passed']
        assert report['refinement']['space_fine']['reason']
    if case == 'empty_inventory':
        assert report['runs']['normal']['final_inventory']['external_liquid'] is None
