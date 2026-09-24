"""Synthetic, no private source or native solver required."""
import dataclasses
import math
import pytest
from puckworks.analysis.pocketscience2024_assay import (
    SourceProtocol, SectionMeasurement, RawMeasurements, RecoveryProtocol,
    AnchorPolicy, reconstruct_source_assay, forward_assay, nonidentifiability_example,
    workbook_graph,
)


def raw():
    return RawMeasurements(.020,.040,.10,SectionMeasurement(.010,.180,.005),SectionMeasurement(.004,.075,.006))


def protocol(sheet='Sworks High Flow',lrr=3):
    return SourceProtocol(sheet,.3,lrr)


def recovery(sheet='Sworks High Flow', survival=1):
    return RecoveryProtocol(1,1,survival,1,1,1,20,3 if sheet=='Sworks High Flow' else 0,protocol(sheet,3 if sheet=='Sworks High Flow' else 0))


def test_percentage_mass_bases_and_unequal_regions():
    x=reconstruct_source_assay(raw(),protocol())
    assert x.raw_recovered_solute_kg==pytest.approx((.0009,.00045))
    assert x.corrected_recoverable_solute_kg==pytest.approx((.00105,.000522))
    assert x.inferred_initial_section_kg==pytest.approx((.014,.006))
    assert x.initial_mass_weighted_ey_fraction==pytest.approx(.2)
    y=reconstruct_source_assay(raw(),protocol('VST18',0))
    assert y.edge_minus_center_fraction==pytest.approx(.09-.1125)
    assert y.initial_mass_weighted_ey_fraction != pytest.approx(.2)


def test_anchor_cancels_difference_not_ratio():
    a=reconstruct_source_assay(raw(),protocol())
    b=reconstruct_source_assay(dataclasses.replace(raw(),cup_tds_fraction=.12),protocol())
    assert a.edge_minus_center_fraction==pytest.approx(b.edge_minus_center_fraction)
    assert a.fractional_edge_loss != pytest.approx(b.fractional_edge_loss)


@pytest.mark.parametrize('sheet',['Sworks High Flow','VST18'])
def test_constructive_global_nonidentifiability(sheet):
    a,b=nonidentifiability_example()
    anchor=AnchorPolicy(.03,.0026,'MODEL_DERIVED')
    x,y=[forward_assay(s,recovery(sheet),anchor) for s in (a,b)]
    assert dataclasses.asdict(x.assay)==pytest.approx(dataclasses.asdict(y.assay))
    assert x.sections[0]['solid_depletion_kg'] != y.sections[0]['solid_depletion_kg']
    for s in (a,b):
        assert sum(j.initial_model_soluble_kg for j in s)==pytest.approx(sum(j.remaining_solid_soluble_kg+j.retained_dissolved_solute_kg for j in s)+anchor.cup_solute_kg)


def test_retained_liquid_drying_and_recovery():
    a,_=nonidentifiability_example()
    x=forward_assay(a,recovery(),AnchorPolicy(.03,.0026,'MODEL_DERIVED'))
    assert x.sections[0]['dry_residue_kg']==pytest.approx(.014-.00392+.0015+.0005)
    assert x.assay.corrected_recoverable_solute_kg==pytest.approx((.002,.001))
    y=forward_assay(a,recovery(survival=0),AnchorPolicy(.03,.0026,'MEASURED_CONDITIONAL'))
    assert y.role=='MEASURED_CONDITIONAL'
    assert y.assay.corrected_recoverable_solute_kg==pytest.approx((.0015,.0008))
    assert y.sections[0]['lost_dry_material_kg']==pytest.approx(.0005)


@pytest.mark.parametrize('value',[None,-1,math.nan,math.inf])
def test_invalid_missing(value):
    with pytest.raises(ValueError):
        reconstruct_source_assay(dataclasses.replace(raw(),initial_dry_coffee_kg=value),protocol())


def test_source_anomalies_are_preserved():
    assert workbook_graph('Sworks High Flow',54)['Y54'][1]==['C54','E54','D54']
    assert workbook_graph('Sworks High Flow',9)['AL9'][1]==['V10','K10']
    assert workbook_graph('VST18',3)['AQ3'][1]==['AP3','U3']


def test_synthetic_workbook_replay_grouping(tmp_path):
    openpyxl=pytest.importorskip('openpyxl')
    from puckworks.analysis.pocketscience2024_assay import replay_workbook
    w=openpyxl.Workbook();s=w.active;s.title='VST18'
    s['A2']='Shot'
    literals=dict(A=1,B=10,C=11,D=20,E=40,F='Niche Zero',I='N',J='Teflon',K=10,L=4,M=.5,O=.6,Q=100,R=100,S=280,T=175)
    for col,v in literals.items():s[f'{col}3']=v
    for cell,(formula,_,_) in workbook_graph('VST18',3).items():s[cell]=formula
    s['A4']=2;s['AU4']='Reject sample'
    p=tmp_path/'synthetic.xlsx';w.save(p)
    r=replay_workbook(p)
    assert len(r['experimental_rows'])==2
    assert r['experimental_rows'][1]['excluded']
    assert r['experimental_rows'][0]['treatment']=='PAPER_ON_TOP'
    assert r['condition_means'][0]['n_shots']==1
    assert r['discrepancies'] # openpyxl does not calculate: no fabricated caches
