"""Scientific identities and source-contract checks, not estimate fixtures."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_aspect_ratio as ar


@pytest.mark.parametrize('rho,solid,ep', [(480,1337,0.53), (480,1337,0.5), (300,1400,0.4)])
def test_particle_volume_conservation_and_independent_kc_algebra(rho, solid, ep):
    e0 = ar.initial_porosity(rho, solid, ep)
    for l2, l6 in [(F(0), F(0)), (F(1,10), F(1,20)), (F(1,20), F(1,10))]:
        e2, e6 = ar.consolidated_porosity(e0, l2), ar.consolidated_porosity(e0, l6)
        assert (1-e2)*(1-l2) == (1-e6)*(1-l6) == 1-e0
        independent = ((e0-l6)/(e0-l2))**3*(1-l2)/(1-l6)
        assert ar.kc_ratio(e0, l2, l6) == independent
        assert ar.kc_ratio(e0, l2, l6)*ar.kc_ratio(e0, l6, l2) == 1
        assert ar.kc_ratio(e0, l2, l2) == 1


@pytest.mark.parametrize('args', [(480,1337,0), (480,1337,1), (480,100,.5),
                                  (0,1337,.5), (480,float('nan'),.5)])
def test_invalid_material_domain(args):
    with pytest.raises(ValueError):
        ar.initial_porosity(*args)


@pytest.mark.parametrize('e,l', [(0,0),(1,0),(.2,.2),(.2,.3),(.2,-.01)])
def test_invalid_consolidation(e,l):
    with pytest.raises(ValueError):
        ar.consolidated_porosity(e,l)


def test_shared_calibration_scale_cancellation_and_baseline_dependence():
    z, n, d = F(100), F(20), F(70)
    r = ar.shared_axis_ratio(n,d,1,z,2)
    for top, scale in [(0,1),(-20,F(1,10)),(10,500)]:
        ratio = ar.ordinate(n,z,top,scale)/ar.ordinate(d,z,top,scale)
        assert ratio == r['central']
    assert ar.shared_axis_ratio(n,d,1,z+1,2)['central'] != r['central']
    for zero in range(98,103):
        for nn,dd in itertools.product(range(19,22),range(69,72)):
            v=F(zero-nn,zero-dd)
            assert r['bounds'][0] <= v <= r['bounds'][1]
    reverse=ar.shared_axis_ratio(d,n,1,z,2)
    assert reverse['bounds'] == [1/r['bounds'][1],1/r['bounds'][0]]
    with pytest.raises(ValueError):
        ar.shared_axis_ratio(20,100,1,100,2)


def test_pure_geometry_dimensions_and_darcy_length_cancellation():
    c=json.loads((ar.DATA/'contract.json').read_text())
    ideal=ar.geometry('equal_initial_volume',c,.13,0)
    printed=ar.geometry('printed_dimensions',c,.13,0)
    assert ideal['H0'] == pytest.approx(3**(4/3))
    assert printed['H0'] == pytest.approx((54/37)**2*(18.5/9))
    assert ideal['H0'] != printed['H0']
    for g in [ideal,printed]:
        assert g['bed_length_adjustment'] == F(87,100)
        assert g['H'] == pytest.approx(g['S_geom_m']['6:1']/g['S_geom_m']['2:1'])
        assert g['H'] == pytest.approx(g['H0']*.87)
    # Same supported Q/P slope; changing length changes inferred kappa exactly
    # enough to leave reconstructed conductance unchanged.
    slope,mu,area=3e-11,4e-4,1e-3
    for length in [.0185,.0185*.87,.009]:
        k=ar.inferred_permeability(slope,mu,length,area)
        assert ar.conductance(k,mu,length,area) == pytest.approx(slope, rel=1e-13, abs=0)
        assert ar.conductance(2*k,mu,length,area) == pytest.approx(2*slope, rel=1e-13, abs=0)


def test_source_coverage_paths_ticks_aliases_and_bounds():
    from puckworks.data import rc17_fig6_9_aspect_ratio
    result=ar.analyze()
    assert len(rc17_fig6_9_aspect_ratio()) == 4
    assert result['coverage']['recovered_means'] == 4
    assert result['coverage']['recovered_error_endpoints'] == 8
    assert ar.ALIASES == dict(zip(['Psi_B','Psi_C','Psi_D','Psi_E'],'ABCD'))
    paths=json.loads((ar.DATA/'source_paths.json').read_text())['paths']
    paths={p['drawing_index']:p for p in paths}
    assert paths[23]['items'] == paths[32]['items']
    for r in ar.csv_rows(ar.DATA/'source_coordinates.csv'):
        i,j=map(int,r['outline_indices'].split(';'))
        assert paths[i]['items'][0] == paths[j]['items'][0]
        points=paths[i]['items'][0][1]
        assert float(r['mean_y_pt']) == min(p[1] for p in points)
        assert abs(float(r['mean_y_pt'])-float(r['fill_top_y_pt'])) < .001
        for which in ['upper','lower']:
            cap=paths[32]['items'][int(r[which+'_cap_item'])]
            assert float(r[which+'_endpoint_y_pt']) == cap[1][1] == cap[2][1]
    for tick in result['tick_checks']:
        assert abs(tick['nominal_axis_residual_pt']) < .61
        lo,hi=tick['recovered']['bounds']
        assert lo <= ar.exact(tick['mantissa'])*F(1,10**13) <= hi
    for ratio in result['ratios'].values():
        assert ratio['marginal_outer_bounds'][0] <= ratio['bounds'][0]
        assert ratio['bounds'][1] <= ratio['marginal_outer_bounds'][1]
        assert 'NOT_ALL_COMBINATIONS_JOINTLY_ADMISSIBLE' in ratio['marginal_outer_semantics']
    coarse=result['scenarios'][2]
    assert coarse['R_KC'] == 1
    assert coarse['particle_porosity'] is None
    assert coarse['F_required']['bounds'] == result['ratios']['Psi_E']['bounds']
    for s in result['scenarios']:
        for g in s['geometry']:
            ratio=g['G6_over_G2_equals_Rhyd2_over_Rhyd6']['central']
            assert ratio == pytest.approx(float(s['R_kappa']['central'])*g['H'])
            assert ratio == pytest.approx(g['C_geom_m3']['6:1']/g['C_geom_m3']['2:1'])


def test_contract_rejects_alias_units_and_missing_conditions(tmp_path):
    shutil.copytree(ar.DATA,tmp_path/'data')
    d=tmp_path/'data'
    p=d/'contract.json'; c=json.loads(p.read_text()); c['units']['length']='mm'
    p.write_text(json.dumps(c))
    with pytest.raises(ValueError,match='SI'):
        ar.analyze(d)
    shutil.copy(ar.DATA/'contract.json',p)
    p=d/'source_coordinates.csv'; text=p.read_text()
    p.write_text(text.replace('Psi_E,D','Psi_E,A'))
    with pytest.raises(ValueError,match='alias'):
        ar.analyze(d)
    p.write_text('\n'.join(text.splitlines()[:-1])+'\n')
    with pytest.raises(ValueError,match='four'):
        ar.analyze(d)


def test_deterministic_execution_and_plan_identity(tmp_path):
    subprocess.run([sys.executable,'-m','puckworks.analysis.corrochano2017_aspect_ratio',
                    '--output',str(tmp_path)],check=True,cwd=ar.ROOT)
    for name in ['RESULT.json','readings.csv']:
        assert (tmp_path/name).read_bytes() == (ar.OUTPUT/name).read_bytes()
    c=json.loads((ar.DATA/'contract.json').read_text())
    assert c['plan_sha256'] == hashlib.sha256((ar.OUTPUT/'PLAN.md').read_bytes()).hexdigest()
    assert (tmp_path/'readings.csv').read_bytes() == (ar.DATA/'readings.csv').read_bytes()
    assert Path(ar.__file__).is_file()
