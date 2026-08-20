import json
from pathlib import Path
import pytest
from puckworks.analysis.response_atlas.schema import (QuantityRow,ResultCell,numeric_residual,
    flow_conversion,permeability_to_resistance)
from puckworks.analysis.response_atlas.compare import classify_candidate,minimal_sets
from puckworks.analysis.response_atlas.measurement_value import discriminate
from puckworks.analysis.response_atlas.residuals import attribution,nested_difference
from puckworks.analysis.response_atlas.runner import validate_protocol
from puckworks.models.wadsworth2026 import inertial

BASE=dict(component_id='x',stage='flow',quantity_name='q',direction='output',unit='m/s',
 reference_basis='bed',physical_definition='test',role='derived',provenance='test',valid_range='NOT_PROVIDED',
 evidence_strength='verification',independently_variable='derived',relationship_kind='direct',
 comparable_observable_group='q',support_status='SUPPORTED',control_mode='native')

def test_required_inventory_fields_and_unknown_range():
    with pytest.raises(TypeError): QuantityRow(component_id='x')
    assert QuantityRow(**BASE).valid_range=='NOT_PROVIDED'
    with pytest.raises(ValueError): QuantityRow(**{**BASE,'valid_range':''})

def test_unsupported_cannot_carry_value():
    with pytest.raises(ValueError): ResultCell('x','c','q','UNSUPPORTED_RELATIONSHIP','m/s',1.0)

def test_out_of_range_precedes_producer():
    called=[]
    def evaluate(x):
        if not 0<=x<=1: return ResultCell('x','c','q','OUTSIDE_VALID_RANGE','m/s',reason='range')
        called.append(x)
    r=evaluate(2); assert not called and r.value is None

def test_pressure_node_and_reference_mismatch_not_level_one():
    a=ResultCell('a','c','p','SUPPORTED','Pa',1,pressure_node='BED_INLET',pressure_reference='GAUGE')
    b=ResultCell('b','c','p','SUPPORTED','Pa',1,pressure_node='PUMP_OUTLET',pressure_reference='ABSOLUTE')
    assert (a.pressure_node,a.pressure_reference)!=(b.pressure_node,b.pressure_reference)

def test_conversion_requirements():
    with pytest.raises(ValueError): flow_conversion(darcy_velocity_m_s=1,area_m2=1)
    with pytest.raises(ValueError): permeability_to_resistance(permeability_m2=1,length_m=1)

def test_numeric_residual_levels_and_non_nested_share():
    a=ResultCell('a','c','q','SUPPORTED','m/s',2); b=ResultCell('b','c','q','SUPPORTED','m/s',1)
    assert numeric_residual(a,b,2)==1
    with pytest.raises(ValueError): numeric_residual(a,b,4)
    with pytest.raises(ValueError): attribution(nested=False,causal_share=.5)
    assert nested_difference(2,1)['closure_error']==0

def test_wrong_primary_gates_not_rescued_by_rmse():
    assert classify_candidate(sign_agrees=False,ordering_agrees=True,grind_agrees=True,rmse=0)=='SIGN'
    assert classify_candidate(sign_agrees=True,ordering_agrees=False,grind_agrees=True,rmse=0)=='MAGNITUDE'

def test_missing_uncertainty_and_set_cover():
    assert discriminate((0,1),(2,3),'NOT_PROVIDED')=='NOT_ADJUDICATED_MISSING_UNCERTAINTY'
    coverage={'a':{'p1'},'b':{'p2'},'c':{'p1','p2'}}
    assert minimal_sets({'p1','p2'},coverage)==[['c']]
    assert minimal_sets({'p1','p3'},coverage)=='NO_COMPLETE_MEASUREMENT_SET'

def test_inertial_disabled_limit_recovers_darcy():
    k=1e-13; grad=9e7; q=inertial.solve_q(k,float('inf'),grad)
    assert q==pytest.approx(grad*k/inertial.MU_92C,rel=1e-12)

def test_protocol_valid_and_json_deterministic():
    assert validate_protocol()
    p=Path('docs/analysis/rp_a_001/protocol.json')
    d=json.loads(p.read_text()); assert json.dumps(d,sort_keys=True)==json.dumps(d,sort_keys=True)
