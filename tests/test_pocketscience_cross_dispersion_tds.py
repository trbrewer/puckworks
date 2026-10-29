"""Synthetic dispersion tests; labels here do not authenticate original workbook J."""
from dataclasses import replace

import numpy as np
import pytest
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as basket
from puckworks.analysis import pocketscience_cross_style_tds as style_model
from puckworks.analysis import pocketscience_cross_dispersion_tds as model
from tools import pocketscience_cross_dispersion_tds as runner


def fixture():
    # Deliberately synthetic ordering: inclusion changes BOTH sides here.
    shots = []
    for dispersion in ('Teflon', 'Brass'):
        for grinder, style in parent.STYLE_MAP.items():
            for prep in ('Y', 'N'):
                g = len(shots)//5
                for i in range(5):
                    row = len(shots)+1
                    shots.append(parent.Shot(model.BASKET, row, (model.BASKET, grinder, prep, dispersion),
                        style, .019+.0001*i, .032+.0007*g+.0002*i, 6+.3*g+.07*i,
                        6.5+.25*g+.04*i, row in (7, 9, 23)))
    return shots


def test_sworks_only_subset_partition_literal_labels_and_additions():
    all40 = fixture()
    vst = [replace(s, sheet='VST18', condition=('VST18', *s.condition[1:])) for s in all40[:20]]
    primary, selected = runner.cohorts(all40+vst)
    assert selected == all40 and len(primary) == 37
    split = runner.dispersion_splits(all40+vst)
    assert split == runner.dispersion_splits(all40)
    assert split['primary']['original_order'] == [s.identity for s in primary]
    assert set(split['primary']['source']).isdisjoint(split['primary']['target'])
    assert len(split['primary']['conditions']) == 8
    assert [len(split['ALL40_SWORKS'][k]) for k in ('source', 'target')] == [20, 20]
    for a in split['additions']:
        s = next(s for s in all40 if s.identity == a['identity'])
        assert a['side'] == ('source' if s.condition[3] == 'Brass' else 'target')
        assert s.identity not in split['primary'][a['side']]
        assert s.identity in split['ALL40_SWORKS'][a['side']]
    assert {a['side'] for a in split['additions']} == {'source', 'target'}
    with pytest.raises(ValueError, match='VST contamination'):
        model.evaluate(primary+vst, draws=2)
    with pytest.raises(ValueError, match='duplicate'):
        model.split(primary+[primary[0]])
    for label in ('brass', 'BRASS', 'Brass ', 'teflon', 'unknown'):
        with pytest.raises(ValueError, match='literal dispersion'):
            model.split([replace(s, condition=(*s.condition[:3], label)) if i == 0 else s
                         for i, s in enumerate(primary)])


def test_vst_never_enters_fits_scores_or_bootstrap(monkeypatch):
    primary, _ = runner.cohorts(fixture())
    source, target = model.split(primary)
    seen = []
    original = parent.bootstrap_weights
    def weights(group, rng):
        seen.append((len(group), len(np.unique(group))))
        return original(group, rng)
    monkeypatch.setattr(parent, 'bootstrap_weights', weights)
    result = model.evaluate(primary, draws=4)
    assert seen == [(37, 8)]*4
    assert result['scientific_n'] == 37 and result['vst_scientific_n'] == 0
    assert result['training_n'] == source.sum() and result['evaluation_n'] == target.sum()
    assert result['coverage_per_arm'] == target.sum()
    assert [(p['sheet'], p['row']) for p in result['predictions']] == [s.identity for s,k in zip(primary,target) if k]
    assert len(result['condition_errors']) == 4 and len(result['style_errors']) == 2
    assert all(len(d['multiplicities']) == 37 for d in result['bootstrap_samples'])


def test_target_tds_changes_leave_all_fits_and_predictions_unchanged():
    primary, _ = runner.cohorts(fixture())
    changed = [replace(s, filtered_tds_pp=99, unfiltered_tds_pp=97) if s.condition[3] == 'Teflon' else s for s in primary]
    for observation in ('filtered', 'unfiltered'):
        a,b = [model.evaluate(shots, observation, draws=3) for shots in (primary,changed)]
        assert a['source_fit'] == b['source_fit']
        assert [p['predictions'] for p in a['predictions']] == [p['predictions'] for p in b['predictions']]
        assert a['scores'] != b['scores']
        for u,v in zip(a['bootstrap_samples'],b['bootstrap_samples'],strict=True):
            assert u['multiplicities'] == v['multiplicities'] and u['fit'] == v['fit']


def test_weighted_fits_scores_independent_solver_and_nesting():
    shots = fixture(); source,target=model.split(shots)
    x,y,style,group=parent.arrays(shots)
    for seed in range(4):
        w=parent.bootstrap_weights(group,np.random.default_rng(seed))
        assert all(w[group==g].sum()==(group==g).sum() for g in np.unique(group))
        fit=model.fit_source(x[source],y[source],style[source],w[source])
        copies=np.repeat(np.flatnonzero(source),w[source])
        literal=model.fit_source(x[copies],y[copies],style[copies])
        pred=model.predict(fit,x[target],style[target])
        np.testing.assert_allclose(pred,model.predict(literal,x[target],style[target]),rtol=0,atol=1e-10)
        for j,a in enumerate(model.ARMS):
            z=basket.design(x[copies],style[copies],a)
            solved=lsq_linear(z,y[copies],bounds=(0,100),method='bvls',tol=1e-14)
            assert solved.success
            np.testing.assert_allclose(pred[:,j],basket.design(x[target],style[target],a)@solved.x,rtol=0,atol=1e-10)
        repeated=np.repeat(np.flatnonzero(target),w[target])
        weighted=model.scores(y[target],pred,group[target],w[target])
        expanded=model.scores(y[repeated],model.predict(fit,x[repeated],style[repeated]),group[repeated])
        for a in model.ARMS: assert weighted[a] == pytest.approx(expanded[a])
        assert fit['training_sse']['M'] <= fit['training_sse']['P']+fit['nesting_roundoff_allowance']


def test_rank_bounds_invalid_values_and_support():
    shots=fixture(); source,target=model.split(shots)
    x,y,style,_=parent.arrays(shots)
    with pytest.raises(ValueError,match='both styles'):
        model.split([s for s in shots if s.condition[3]=='Teflon' or s.style=='traditional'])
    with pytest.raises(ValueError,match='rank'):
        model.fit_source(x[source],y[source],style[source],(style[source]==0).astype(int))
    for w in (np.zeros(source.sum()),-np.ones(source.sum()),np.full(source.sum(),np.nan)):
        with pytest.raises(ValueError): model.fit_source(x[source],y[source],style[source],w)
    with pytest.raises(ValueError): model.fit_source(x[source]*0,y[source],style[source])
    with pytest.raises(ValueError): model.fit_source(x[source],y[source]*np.nan,style[source])
    f=model.fit_source(x[source]*.001,y[source],style[source])
    assert f['parameters']['P']['active_bounds']==[True]
    assert model.oracle_error(f,x[target]*.001,style[target]) <= 1e-10
    extrap=[replace(s,beverage_kg=.009) if s.condition[3]=='Teflon' else s for s in shots]
    r=model.evaluate(extrap,draws=2)
    assert r['support']['overall']['target_extrapolation_count']==r['evaluation_n']
    assert r['coverage_per_arm']==r['evaluation_n']
    assert all(p['extrapolation']['style_preparation'] for p in r['predictions'])


def test_condition_influence_preserves_source_fit_for_target_deletions():
    shots,_=runner.cohorts(fixture());p=model.evaluate(shots,draws=2)
    influence=model.deletion_influence(shots,p)
    assert len(influence['deletions'])==8
    for r in influence['deletions']:
        if r['side']=='target':
            assert r['source_fit'] is p['source_fit'] and r['training_n']==p['training_n']
        else:
            assert r['evaluation_n']==p['evaluation_n'] and r['training_n']<p['training_n']
        fit=r['source_fit']
        assert fit['training_sse']['M']<=fit['training_sse']['P']+fit['nesting_roundoff_allowance']


def test_zero_reference_and_primary_secondary_zero_endpoints():
    r=model.evaluate([replace(s,filtered_tds_pp=0) for s in fixture()],draws=3)
    assert r['decision']=='CROSS_DISPERSION_COMPARISON_UNRESOLVED'
    assert r['mc_interpretation']=='INCREMENTAL_SCALING_CLAIM_UNESTABLISHED'
    for c in r['contrasts'].values():
        assert c['gain'] is None and c['gain_ci95'] is None and c['gain_undefined_draws']==3
        assert c['difference_ci95']==[0,0] and len(c['boundary_check'])==9
    for ci,expected in [([-2,-1],'P_CROSS_DISPERSION_ADDED_VALUE_OVER_N'),
                        ([1,2],'N_LOWER_CROSS_DISPERSION_LOSS'),
                        ([-1,0],'CROSS_DISPERSION_COMPARISON_UNRESOLVED'),
                        ([0,1],'CROSS_DISPERSION_COMPARISON_UNRESOLVED')]:
        assert model.decision({'P/N':{'difference_ci95':ci}})==expected
    c=model.contrasts({a:{'rmse':0 if a=='N' else 1} for a in model.ARMS})['P/N']
    assert c==dict(difference=1,gain=None)


def test_failed_draw_stops_and_preserves_success_and_failed_attempt(monkeypatch):
    original=model.fit_source; count=0
    def fail(x,y,style,weights=None,**kwargs):
        nonlocal count
        if weights is not None:
            count+=1
            if count==2: raise ValueError('synthetic second draw failure')
        return original(x,y,style,weights,**kwargs)
    monkeypatch.setattr(model,'fit_source',fail)
    r=model.evaluate(fixture(),draws=4)
    assert r['bootstrap']['completed']==1 and r['bootstrap']['failed']==1 and r['bootstrap']['not_run']==2
    assert len(r['bootstrap']['failures'][0]['multiplicities'])==40
    assert r['decision']==r['mc_interpretation']=='INCOMPLETE_BOOTSTRAP'
    assert all(c['difference_ci95'] is None and c['gain_ci95'] is None for c in r['contrasts'].values())


def test_predecessor_contracts_unchanged():
    assert parent.ARMS==('M','C','N') and pooled.ARMS==basket.ARMS==('M','C','N','P')
    assert style_model.ARMS==('P','N')
    shots=[s for s in fixture() if s.style=='traditional']
    x,y,style,_=parent.arrays(shots)
    with pytest.raises(ValueError,match='rank'): basket.fit_source(x,y,style)
    with pytest.raises(ValueError,match='missing training style'): basket.split(shots+[replace(s,sheet=basket.TARGET,condition=(basket.TARGET,*s.condition[1:])) for s in shots])
