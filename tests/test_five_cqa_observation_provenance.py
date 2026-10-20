"""Independent synthetic risks for the task-local provenance reader."""
import hashlib
import importlib.util
from pathlib import Path
from zipfile import ZipFile

import pytest

spec = importlib.util.spec_from_file_location('five_cqa_provenance', Path(__file__).resolve().parents[1]/'tools/five_cqa_observation_provenance.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def test_metadata_does_not_filter_hidden_or_nonnumeric_sheets(tmp_path):
    path = tmp_path/'book.xlsx'
    xml = '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <sheets><sheet name="1-3" sheetId="1"/><sheet name="Standards" sheetId="2" state="hidden"/>
    <sheet name="Controls" sheetId="3" state="veryHidden"/></sheets>
    <definedNames><definedName name="calibration">Standards!A2:B8</definedName></definedNames></workbook>'''
    with ZipFile(path, 'w') as z:
        z.writestr('xl/workbook.xml', xml)
        z.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c r="C1"><f>Standards!A2</f></c></row></sheetData></worksheet>')
    result = p.workbook_metadata(path)
    assert [(r['name'], r['state']) for r in result['sheets']] == [
        ('1-3', 'visible'), ('Standards', 'hidden'), ('Controls', 'veryHidden')]
    assert result['defined_names'][0]['text'] == 'Standards!A2:B8'
    assert result['explicit_formula_references'][0]['formula'] == 'Standards!A2'


def test_one_source_failure_preserves_usable_original(tmp_path):
    (tmp_path/'good').write_bytes(b'good')
    (tmp_path/'changed').write_bytes(b'new')
    good = hashlib.sha256(b'good').hexdigest()
    records = [{'source_id': k, 'source_relpath': k, 'sha256': good} for k in ('good', 'missing', 'changed')]
    result = p.admit(tmp_path, records, dict.fromkeys(('good', 'missing', 'changed'), good))
    assert result['good']['identity_status'] == 'MATCH'
    assert result['missing']['state'] == 'not located in the explicitly inspected scope'
    assert result['changed']['identity_status'] == 'IDENTITY_FAILURE'
    assert result['missing']['identity_status'] == 'NOT_CHECKED'


def test_permission_failure_is_not_absence(tmp_path, monkeypatch):
    original = p.sha256
    def blocked(path):
        if Path(path).name == 'blocked':
            raise PermissionError('synthetic access restriction')
        return original(path)
    monkeypatch.setattr(p, 'sha256', blocked)
    result = p.admit(tmp_path, [{'source_id': 'x', 'source_relpath': 'blocked', 'sha256': 'a'}], {'x': 'a'})
    assert result['x']['state'] == 'present but inaccessible here'
    assert result['x']['identity_status'] == 'NOT_CHECKED'


@pytest.mark.parametrize('value,expected', [(1,'BELOW'),(2,'WITHIN'),(3,'WITHIN'),(4,'WITHIN'),(5,'ABOVE')])
def test_exact_support_endpoints(value, expected):
    assert p.support(value, 2, 4, analyte='5CQA', basis='diluted_mg_per_kg',
                     association=True, validity='VALID') == expected


@pytest.mark.parametrize('kwargs', [dict(analyte='CQA_sum'), dict(basis='beverage_mg_per_g'),
                                    dict(basis='mg_per_L'), dict(association=False)])
def test_wrong_analyte_basis_or_unlinked_batch_is_unassessable(kwargs):
    contract = dict(analyte='5CQA', basis='diluted_mg_per_kg', association=True, validity='VALID')
    contract.update(kwargs)
    assert p.support(3, 2, 4, **contract) == 'UNASSESSABLE'


def test_zero_is_not_spill_or_nondetect_and_no_mass_domain_filter():
    contract = dict(analyte='5CQA', basis='response_mV_min_per_10', association=True)
    assert p.support(0, 0, 10, validity='VALID', **contract) == 'WITHIN'
    assert p.support(0, 0, 10, validity='INVALID_SPILL', **contract) == 'NOT_APPLICABLE_INVALID_SPILL'
    # A missing predictor prefix is not an input to this analytical comparison.
    missing_predictor_prefix = None
    assert missing_predictor_prefix is None
    assert p.support(12, 0, 10, validity='VALID', **contract) == 'ABOVE'


def test_preparation_or_batch_join_requires_unique_known_key():
    row = {'key': ['FIT', 7, 3]}
    assert p.unique_join([row], ('FIT',7,3)) == ('MATCH',row)
    assert p.unique_join([row,row], ('FIT',7,3)) == ('AMBIGUOUS',None)
    assert p.unique_join([row], ('PRED',7,3)) == ('UNMATCHED',None)
    assert p.unique_join([{'key':['UNKNOWN',7,3]}], ('UNKNOWN',7,3)) == ('UNKNOWN_KEY',None)


def test_gravimetric_ratio_not_water_over_sample_or_vial_mass():
    assert p.dilution(9, 1) == 10
    assert p.dilution(0, 1) == 1
    assert p.dilution(None, 1) is None
    assert p.dilution(9, 0) is None
    assert p.dilution(-1, 1) is None


def test_response_on_concentration_free_intercept_without_zero_substitution():
    # Hand-computed response y=3x+7; missing chart cells are not artificial (0,0).
    assert p.trendline([(1,10),(2,13),(4,19)]) == (3,7)
    with pytest.raises(ValueError):
        p.trendline([(1,10),(None,None)])
    with pytest.raises(ValueError):
        p.trendline([(1,10),(1,13)])


def test_synthetic_preparation_layout_is_keyed_not_positional():
    openpyxl = pytest.importorskip('openpyxl')
    book = openpyxl.Workbook(); s=book.active
    s['A1']='No.'; s['B1']=9; s['F1']=2
    s['A2']='Fr.'; s['B2']=3; s['F2']=3
    for start in (2,6):
        for j, label in enumerate(['SOLL H20','IST H20','SOLL Kaffee','IST Kaffee']):
            s.cell(4,start+j,label)
        s.cell(5,start+1,9); s.cell(5,start+3,1)
    rows = p.preparation_records(s,'PRED')
    assert [r['key'] for r in rows] == [['PRED',9,3],['PRED',2,3]]
    assert rows[0]['water_cell']=='C5' and rows[0]['coffee_cell']=='E5'


def test_stock_units_and_plot_cache_synthetic(tmp_path):
    openpyxl = pytest.importorskip('openpyxl')
    fs=openpyxl.Workbook(); fs.active.title='CGA'
    cs=openpyxl.Workbook(); cs.active.title='CGA'
    f,c=fs.active,cs.active
    for stock in (5,8):
        f[f'F{stock}']=f'=B{stock}*1000/(C{stock}/1000)'
        c[f'B{stock}']=0.001; c[f'C{stock}']=10; c[f'F{stock}']=100
    data=[]
    for i,r in enumerate(list(range(11,16))+list(range(25,30))):
        stock=5 if r<20 else 8
        f[f'J{r}']=f'=H{r}*$F${stock}/(H{r}+I{r})'
        c[f'H{r}']=1; c[f'I{r}']=i; c[f'D{r}']=100/(i+1); c[f'J{r}']=100/(i+1)
        c[f'K{r}']=3*100/(i+1)+7
        c[f'D{43+i}']=100/(i+1); c[f'E{43+i}']=3*100/(i+1)+7
        data.append((c[f'D{43+i}'].value,c[f'E{43+i}'].value))
    axes=''
    for j,(axis,col) in enumerate((('xVal','D'),('yVal','E'))):
        points=''.join(f'<c:pt idx="{i}"><c:v>{xy[j]}</c:v></c:pt>' for i,xy in enumerate(data))
        axes+=f'<c:{axis}><c:numRef><c:f>CGA!${col}$43:${col}$55</c:f><c:numCache>{points}</c:numCache></c:numRef></c:{axis}>'
    path=tmp_path/'chart.xlsx'
    with ZipFile(path,'w') as z:
        z.writestr('xl/charts/chart2.xml','<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"><c:ser><c:trendline><c:trendlineType val="linear"/></c:trendline>'+axes+'</c:ser></c:chartSpace>')
    result=p.calibration(fs,cs,path,'FIT')
    assert all(r['cache_match'] for r in result['stock_checks'])
    assert result['blank_chart_rows']==[53,54,55]
    assert result['slope']==pytest.approx(3) and result['intercept']==pytest.approx(7)
    c['F5']=0.1  # factor-of-1000 error must surface, not be treated as the correct basis
    result=p.calibration(fs,cs,path,'FIT')
    assert result['stock_checks'][0]['cache_match'] is False


def test_missing_nominal_header_does_not_erase_actual_quantity_evidence():
    openpyxl = pytest.importorskip('openpyxl')
    book = openpyxl.Workbook(); s=book.active
    s['A1']='No.'; s['B1']=1; s['A2']='Fr.'; s['B2']=1
    s['C4']='IST H20'; s['D4']='SOLL Kaffee'; s['E4']='IST Kaffee'
    s['C5']=9; s['E5']=1
    rows=p.preparation_records(s,'FIT')
    assert len(rows)==1 and rows[0]['quantity_headers_ok']
    assert p.dilution(rows[0]['water_g'],rows[0]['coffee_g'])==10
    s['E4']=None
    rows=p.preparation_records(s,'FIT')
    assert len(rows)==1 and not rows[0]['quantity_headers_ok']
