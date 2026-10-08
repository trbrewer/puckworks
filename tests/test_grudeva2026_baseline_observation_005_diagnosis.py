"""Small ordinary algebra/serialization tests; no canonical archives or spectra."""
import json
from decimal import Decimal, localcontext

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from puckworks.analysis import grudeva2026_baseline_observation_005_diagnosis as diagnostic


@pytest.mark.parametrize('z', [0., .2, .7, 1.])
def test_independent_moments_and_integrals(z):
    faces = np.array([0., .13, .31, .56, .82, 1.])
    # p(x)=2-3x+4x²; exact averages are not the center samples.
    a, b = faces[:-1], faces[1:]
    averages = 2-1.5*(a+b)+4*(a*a+a*b+b*b)/3
    poly = diagnostic.moment_polynomial(faces, averages, z)
    assert poly['value'] == pytest.approx(2-3*z+4*z*z, abs=2e-14)
    for j in poly['indices']:
        assert diagnostic.polynomial_integral(poly, faces[j], faces[j+1]) == pytest.approx(
            averages[j]*(faces[j+1]-faces[j]), abs=2e-14)
    assert max(abs(averages-(2-3*(a+b)/2+4*((a+b)/2)**2))) > .01


def test_overlap_integrals_and_signed_decomposition():
    fine = np.array([0., .08, .25, .48, .67, .81, 1.])
    coarse = np.array([0., .18, .39, .72, 1.])
    left, right = fine[:-1], fine[1:]
    fine_means = 1+(left*left+left*right+right*right)/3
    projected = np.array([diagnostic.reaverage(fine, fine_means, a, b)[0]
                          for a, b in zip(coarse[:-1], coarse[1:])])
    expected = 1+(coarse[:-1]**2+coarse[:-1]*coarse[1:]+coarse[1:]**2)/3
    assert projected == pytest.approx(expected, abs=2e-14)
    actual = projected+np.array([.02, -.03, .01, -.02])
    z = .5
    p = diagnostic.moment_polynomial(coarse, actual, z)
    total = p['value']-(1+z*z)
    stored = (actual-projected)[p['indices']] @ p['weights']
    remainder = projected[p['indices']] @ p['weights']-(1+z*z)
    assert total-stored-remainder == pytest.approx(0., abs=2e-14)
    with pytest.raises(ValueError, match='outside fine physical domain'):
        diagnostic.reaverage(fine, fine_means, .9, 1.0001)


def test_stable_exponential_average_against_decimal_antiderivative():
    with localcontext() as context:
        context.prec = 60
        r, lo, hi = Decimal('3'), Decimal('.01'), Decimal('.04')
        initial, b0, a, b = map(Decimal, ['1.388', '.07', '.1', '.02'])
        A, B, C = initial-b0+a/r-2*b/r**2, b0-a/r+2*b/r**2, a-2*b/r
        def primitive(age):
            return -A/r*(-r*age).exp()+B*age+C*age**2/2+b*age**3/3
        expected = float((primitive(hi)-primitive(lo))/(hi-lo))
    # t=.1, activation=z/.2: age limits .01,.04.
    actual = diagnostic.finite_averages(np.array([.012, .018]), .1, [3.], [.07, .1, .02])
    assert actual[0, 0] == pytest.approx(expected, abs=5e-15)


def test_scalar_modal_axes_and_serialization(tmp_path):
    faces = np.array([0., .1, .4, 1.])
    values = np.array([[2., 2., 2.], [3., 3., 3.]])
    p = diagnostic.moment_polynomial(faces, values, 0.)
    assert p['value'] == pytest.approx([2., 3.], abs=2e-14)
    assert np.array([.3, .7]) @ p['value'] == pytest.approx(2.7)
    path = tmp_path/'output.json'
    diagnostic.checkpoint(path, {'p': p})
    assert len(json.loads(path.read_text())['p']['weights']) == 3
    with pytest.raises(ValueError):
        diagnostic.checkpoint(path, {'bad': float('nan')})


def test_cli_preserves_partial_failure_and_refuses_existing_name(tmp_path, monkeypatch):
    plan = tmp_path/'plan.json'
    plan.write_text(obs.canonical({'attempt': 'ordinary-software-test'}))
    allocation = tmp_path/'allocation.json'
    allocation.write_text(obs.canonical(dict(attempt='ordinary-software-test',
        diagnostic_plan_sha256=obs.sha(plan), diagnostic_source_sha256=obs.sha(diagnostic.__file__))))
    output = tmp_path/'result.json'
    def fail(folder, plan, result, save):
        result['archive_checks']['manufactured'] = {'metadata_only': True}
        save()
        raise RuntimeError('original diagnostic exception')
    monkeypatch.setattr(diagnostic, 'run', fail)
    argv = ['--runs-directory', str(tmp_path), '--plan', str(plan), '--allocation', str(allocation), '--output', str(output)]
    with pytest.raises(RuntimeError, match='original diagnostic exception'):
        diagnostic.main(argv)
    saved = obs.read_json(output)
    assert saved['failure'] == {'type': 'RuntimeError', 'message': 'original diagnostic exception'}
    assert saved['execution'] == 'INCOMPLETE' and saved['archive_checks']['manufactured']['metadata_only']
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        diagnostic.main(argv)
    assert output.read_bytes() == original
    allocation.write_text(obs.canonical(dict(attempt='ordinary-software-test',
        diagnostic_plan_sha256='incorrect', diagnostic_source_sha256=obs.sha(diagnostic.__file__))))
    with pytest.raises(ValueError, match='allocation identity mismatch'):
        diagnostic.main(argv)
