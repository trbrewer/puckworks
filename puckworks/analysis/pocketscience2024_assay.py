"""Pocket Science Coffee (2024) workbook and conditional recovery observation.

SI masses at public interfaces; TDS and EY are fractions, never display percent.
This is an offline observation calculation, not a production component.
"""
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Literal


def bounded(value, name, low=0., high=float('inf')):
    if value is None or not isfinite(value) or not low <= value <= high:
        raise ValueError(f'UNKNOWN or invalid {name}')
    return value


@dataclass(frozen=True)
class SourceProtocol:
    sheet: Literal['Sworks High Flow', 'VST18']
    outer_initial_mass_fraction: float
    recovery_lrr_kg_per_kg_residue: float

    def __post_init__(self):
        if self.sheet not in ('Sworks High Flow', 'VST18'):
            raise ValueError('unsupported source protocol')
        bounded(self.outer_initial_mass_fraction, 'outer fraction', 1e-15, 1-1e-15)
        bounded(self.recovery_lrr_kg_per_kg_residue, 'recovery LRR')
        if self.sheet == 'VST18' and self.recovery_lrr_kg_per_kg_residue != 0:
            raise ValueError('VST workbook does not apply LRR')


@dataclass(frozen=True)
class SectionMeasurement:
    dry_residue_kg: float
    recovery_beverage_kg: float
    recovery_tds_fraction: float


@dataclass(frozen=True)
class RawMeasurements:
    initial_dry_coffee_kg: float
    cup_beverage_kg: float
    cup_tds_fraction: float  # selected source anchor, Y54 uses unfiltered
    center: SectionMeasurement
    edge: SectionMeasurement


@dataclass(frozen=True)
class AssayResult:
    raw_recovered_solute_kg: tuple[float, float]
    corrected_recoverable_solute_kg: tuple[float, float]
    remainder_fraction_of_residue: tuple[float, float]
    inferred_initial_section_kg: tuple[float, float]
    whole_shot_ey_fraction: float
    inferred_total_soluble_fraction: float
    apparent_section_ey_fraction: tuple[float, float]
    edge_minus_center_fraction: float
    fractional_edge_loss: float | None
    initial_mass_weighted_ey_fraction: float


def reconstruct_source_assay(raw_measurements: RawMeasurements,
                             source_protocol: SourceProtocol) -> AssayResult:
    """Reproduce each sheet's actual denominator and shared shot anchor."""
    m, p = raw_measurements, source_protocol
    d = bounded(m.initial_dry_coffee_kg, 'dose', 1e-15)
    b = bounded(m.cup_beverage_kg, 'cup beverage')
    t = bounded(m.cup_tds_fraction, 'cup TDS fraction', 0, 1)
    masses = (d*(1-p.outer_initial_mass_fraction), d*p.outer_initial_mass_fraction)
    raw, recovered, remainder = [], [], []
    for s in (m.center, m.edge):
        dry = bounded(s.dry_residue_kg, 'dry residue', 1e-15)
        bev = bounded(s.recovery_beverage_kg, 'recovery beverage')
        tds = bounded(s.recovery_tds_fraction, 'recovery TDS fraction', 0, 1)
        raw.append(bev*tds)
        recovered.append((bev+p.recovery_lrr_kg_per_kg_residue*dry)*tds)
        remainder.append(recovered[-1]/dry)
    anchor = b*t/d
    total = anchor+sum(recovered)/d
    denom = masses if p.sheet == 'Sworks High Flow' else (m.center.dry_residue_kg, m.edge.dry_residue_kg)
    ey = tuple(total-u/dj for u, dj in zip(recovered, denom))
    delta = ey[1]-ey[0]
    return AssayResult(tuple(raw), tuple(recovered), tuple(remainder), masses,
                       anchor, total, ey, delta, delta/ey[0] if ey[0] else None,
                       sum(x*y for x,y in zip(ey,masses))/d)


@dataclass(frozen=True)
class CompartmentState:
    initial_dry_coffee_kg: float
    initial_model_soluble_kg: float
    remaining_solid_soluble_kg: float
    retained_dissolved_solute_kg: float
    retained_solvent_kg: float


@dataclass(frozen=True)
class RecoveryProtocol:
    # Fractions explicitly describe survival through drainage/handling/drying.
    nonextractable_survival: float
    solid_soluble_survival: float
    dissolved_solute_survival: float
    solvent_survival_before_drying: float
    solid_recovery_efficiency: float
    dissolved_recovery_efficiency: float
    recovery_water_per_residue: float
    actual_recovery_liquid_retention_per_residue: float
    source: SourceProtocol


@dataclass(frozen=True)
class AnchorPolicy:
    cup_beverage_kg: float
    cup_solute_kg: float
    role: Literal['MODEL_DERIVED', 'MEASURED_CONDITIONAL']


@dataclass(frozen=True)
class ForwardResult:
    assay: AssayResult
    sections: tuple[dict, dict]
    role: str
    qualification: str = 'CONDITIONAL'


def forward_assay(compartment_state: tuple[CompartmentState, CompartmentState],
                  recovery_protocol: RecoveryProtocol, anchor_policy: AnchorPolicy) -> ForwardResult:
    """ILLUSTRATIVE_CONDITIONAL_MODEL; never infer unspecified recovery inputs.

    Ideal dry residue = (D0-I0)+R+L. Solvent evaporates; L remains.
    With losses: H=aN(D0-I0)+aR R+aL L; recovered U=eR aR R+eL aL L.
    For added water W, dissolved solution is W+U. A specified solution retention
    T leaves beverage B=W+U-T with TDS=U/(W+U). Source LRR is a separate correction.
    """
    if len(compartment_state) != 2:
        raise ValueError('center and edge required')
    p, a = recovery_protocol, anchor_policy
    for name in ('nonextractable_survival','solid_soluble_survival','dissolved_solute_survival',
                 'solvent_survival_before_drying','solid_recovery_efficiency','dissolved_recovery_efficiency'):
        bounded(getattr(p,name), name, 0, 1)
    bounded(p.recovery_water_per_residue, 'recovery water ratio', 1e-15)
    bounded(p.actual_recovery_liquid_retention_per_residue, 'actual recovery retention')
    if a.role not in ('MODEL_DERIVED','MEASURED_CONDITIONAL'):
        raise ValueError('anchor provenance required')
    bounded(a.cup_beverage_kg, 'anchor beverage', 1e-15)
    bounded(a.cup_solute_kg, 'anchor solute', 0, a.cup_beverage_kg)
    measurements, details = [], []
    for s in compartment_state:
        for name, value in asdict(s).items(): bounded(value,name)
        d,i,r,l,w = asdict(s).values()
        if not 0 <= r <= i <= d or d == 0:
            raise ValueError('invalid initial or remaining inventory')
        n = d-i
        h = p.nonextractable_survival*n+p.solid_soluble_survival*r+p.dissolved_solute_survival*l
        u = p.solid_recovery_efficiency*p.solid_soluble_survival*r+p.dissolved_recovery_efficiency*p.dissolved_solute_survival*l
        water = p.recovery_water_per_residue*h
        retained = p.actual_recovery_liquid_retention_per_residue*h
        if h <= 0 or water+u <= retained:
            raise ValueError('nonpositive recovery residue or beverage')
        bev = water+u-retained
        measurements.append(SectionMeasurement(h,bev,u/(water+u)))
        details.append(dict(initial_dry_coffee_kg=d, initial_model_soluble_kg=i,
                            solid_depletion_kg=i-r, ideal_dry_residue_kg=n+r+l,
                            dry_residue_kg=h, recovery_soluble_kg=u,
                            recovery_water_kg=water,recovery_beverage_kg=bev,
                            retained_recovery_solution_kg=retained,
                            lost_dry_material_kg=n+r+l-h,
                            lost_pore_solvent_kg=(1-p.solvent_survival_before_drying)*w,
                            evaporated_solvent_kg=p.solvent_survival_before_drying*w))
    d = sum(s.initial_dry_coffee_kg for s in compartment_state)
    result = reconstruct_source_assay(RawMeasurements(d,a.cup_beverage_kg,a.cup_solute_kg/a.cup_beverage_kg,*measurements),p.source)
    return ForwardResult(result,tuple(details),a.role)


def nonidentifiability_example():
    """Generic synthetic pair: same every assay primitive, anchor and global mass.

    Transfer .0002 kg from center R to L and the opposite at edge; initial
    inventories, solvent, R+L and all residue/recovery measurements stay fixed.
    """
    a = (CompartmentState(.014,.00392,.0015,.0005,.004),
         CompartmentState(.006,.00168,.0008,.0002,.002))
    b = (CompartmentState(.014,.00392,.0013,.0007,.004),
         CompartmentState(.006,.00168,.0010,.0000,.002))
    return a,b

# Literal, source-specific calculation graph. No workbook expression is evaluated.
def workbook_graph(sheet, row):
    r = row
    graph = {}
    def add(col, formula, deps, fn):
        graph[f'{col}{r}'] = (formula, [f'{x}{r}' for x in deps], fn)
    add('N',f'=S{r}-Q{r}',('S','Q'),lambda s,q:s-q)
    add('P',f'=T{r}-R{r}',('T','R'),lambda t,r:t-r)
    sw = sheet == 'Sworks High Flow'
    cols = ('V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR AS AT AU' if sw else
            'U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR AS AT').split()
    rc,re,x,y,z,aa,ab,ac,ad,q,dc,de,hc,he,pc,pe,uc,ue,xc,xe,total,f,ec,ee,absolute,signed = cols
    if sw:
        add(rc,f'=(N{r}+(K{r}*U{r}))*M{r}/K{r}',('N','K','U','M'),lambda b,h,l,t:(b+h*l)*t/h)
        add(re,f'=(P{r}+(L{r}*U{r}))*O{r}/L{r}',('P','L','U','O'),lambda b,h,l,t:(b+h*l)*t/h)
    else:
        add(rc,f'=N{r}*M{r}/K{r}',('N','M','K'),lambda b,t,h:b*t/h)
        add(re,f'=P{r}*O{r}/L{r}',('P','O','L'),lambda b,t,h:b*t/h)
    add(x,f'=C{r}*E{r}/D{r}',('C','E','D'),lambda t,b,d:t*b/d)
    anchor_col = 'C' if sw and r == 54 else 'B'
    add(y,f'={anchor_col}{r}*E{r}/D{r}',(anchor_col,'E','D'),lambda t,b,d:t*b/d)
    for col,dep in ((z,x),(aa,y)):
        add(col,f'={dep}{r}*D{r}/100',(dep,'D'),lambda ey,d:ey*d/100)
    add(ab,f'=D{r}-{z}{r}',('D',z),lambda d,z:d-z)
    add(ac,f'=K{r}+L{r}',('K','L'),lambda k,l:k+l)
    add(ad,f'=({ab}{r}-{ac}{r})/{ab}{r}',(ab,ac),lambda expected,actual:(expected-actual)/expected)
    numerator,denominator = ((6.19,18.17 if r<16 else 18.22) if sw else (5.6,18.03) if r<17 else (5.52,18.07))
    add(q,f'={numerator}/{denominator}',(),lambda:numerator/denominator)
    add(dc,f'=(1-{q}{r})*D{r}',(q,'D'),lambda q,d:(1-q)*d)
    add(de,f'={q}{r}*D{r}',(q,'D'),lambda q,d:q*d)
    for col,orig,dry in ((hc,dc,'K'),(he,de,'L')):
        add(col,f'={orig}{r}-{dry}{r}',(orig,dry),lambda d,h:d-h)
    for col,orig,dry in ((pc,dc,'K'),(pe,de,'L')):
        add(col,f'=({orig}{r}-{dry}{r})/{orig}{r}',(orig,dry),lambda d,h:(d-h)/d)
    for col,rem,dry in ((uc,rc,'K'),(ue,re,'L')):
        add(col,f'={rem}{r}*{dry}{r}/100',(rem,dry),lambda rem,h:rem*h/100)
    if sw and r == 9:
        graph['AL9'] = ('=V10*K10/100',['V10','K10'],lambda v,k:v*k/100)
    for col,orig in ((xc,dc),(xe,de)):
        add(col,f'={y}{r}*{orig}{r}/100',(y,orig),lambda ey,d:ey*d/100)
    add(total,f'={xe}{r}+{xc}{r}+{ue}{r}+{uc}{r}',(xe,xc,ue,uc),lambda a,b,c,d:a+b+c+d)
    add(f,f'={total}{r}/D{r}',(total,'D'),lambda u,d:u/d)
    for col,orig,u,rem in ((ec,dc,uc,rc),(ee,de,ue,re)):
        if sw:
            add(col,f'= (({f}{r}*{orig}{r})-{u}{r})/{orig}{r}',(f,orig,u),lambda f,d,u:(f*d-u)/d)
        else:
            add(col,f'={f}{r}-({rem}{r}/100)',(f,rem),lambda f,rem:f-rem/100)
    add(absolute,f'=ABS({ee}{r}-{ec}{r})',(ee,ec),lambda e,c:abs(e-c))
    add(signed,f'={ec}{r}-{ee}{r}',(ec,ee),lambda c,e:c-e)
    return graph


def inspect_workbook(path):
    """Return both views, preserving headers/formats. openpyxl never calculates."""
    import openpyxl
    f = openpyxl.load_workbook(path,data_only=False,keep_links=False)
    c = openpyxl.load_workbook(path,data_only=True,keep_links=False)
    return f,c


def replay_workbook(path):
    """Full local replay; result contains source values and must remain external."""
    import hashlib
    from collections import defaultdict
    f,c = inspect_workbook(path)
    rows, comparisons, unsupported, groups, retention = [],[],[],defaultdict(list),[]
    for sheet in f:
        graph = {}
        shot_rows = [row[0].row for row in sheet if isinstance(row[0].value,(int,float))]
        if sheet.title == 'LRR':
            for r in shot_rows:
                graph[f'C{r}']=(f'=(E{r}-F{r})/D{r}',[f'E{r}',f'F{r}',f'D{r}'],lambda w,b,d:(w-b)/d)
            for r,lo,hi in ((7,2,6),(14,9,13)):
                graph[f'C{r}']=(f'=AVERAGE(C{lo}:C{hi})',[f'C{i}' for i in range(lo,hi+1)],lambda *v:sum(v)/len(v))
        elif sheet.title in ('Sworks High Flow','VST18'):
            for r in shot_rows: graph.update(workbook_graph(sheet.title,r))
        else:
            raise ValueError('unexpected sheet '+sheet.title)
        memo = {}
        def value(address):
            if address in memo:return memo[address]
            cell = sheet[address]
            if cell.data_type != 'f':
                return 0. if cell.value is None else cell.value  # Excel blank semantics, replay ONLY
            spec = graph.get(address)
            if spec is None or spec[0] != cell.value:
                raise ValueError('unsupported formula '+sheet.title+'!'+address)
            args=[value(d) for d in spec[1]]
            try:
                out = next((v for v in args if isinstance(v,str) and v.startswith('#')),None)
                if out is None:out=spec[2](*args)
            except ZeroDivisionError:out='#DIV/0!'
            memo[address]=out
            return out
        for cells in sheet:
            for cell in cells:
                if cell.data_type != 'f':continue
                try:computed=value(cell.coordinate)
                except ValueError as e:
                    unsupported.append(str(e));continue
                cached=c[sheet.title][cell.coordinate].value
                percent='%' in cell.number_format
                scale=100 if percent else 1
                unit='percent_display' if percent or (sheet.title!='LRR' and cell.column_letter in (('V','W','X','Y') if sheet.title=='Sworks High Flow' else ('U','V','W','X'))) else ('dimensionless_ratio' if sheet.title=='LRR' or cell.column_letter==('AE' if sheet.title=='Sworks High Flow' else 'AD') else 'g')
                error = abs(computed-cached)*scale if isinstance(computed,(int,float)) and isinstance(cached,(int,float)) else None
                okay = error <= 1e-8+1e-10*abs(computed*scale) if error is not None else computed == cached
                comparisons.append(dict(sheet=sheet.title,cell=cell.coordinate,formula=cell.value,dependencies=graph[cell.coordinate][1],computed=computed,cached=cached,number_format=cell.number_format,display_unit=unit,absolute_display_error=error,within_frozen_tolerance=okay))
        if sheet.title=='LRR':
            retention=[dict(cell=a,computed=value(a),cached=c[sheet.title][a].value) for a in graph]
            continue
        header = None
        for r in range(1,sheet.max_row+1):
            if sheet[f'A{r}'].value == 'Shot':header=r
            if r not in shot_rows:continue
            sw=sheet.title=='Sworks High Flow'
            note=sheet[f'{"AV" if sw else "AU"}{r}'].value
            excluded=bool(note and 'reject' in note.lower())
            item=dict(sheet=sheet.title,row=r,header_row=header,source_shot_id=sheet[f'A{r}'].value,
                      condition=[sheet.title]+[sheet[f'{x}{r}'].value for x in ('F','I','J')],
                      treatment='METAL_SCREEN' if sheet[f'I{r}'].value=='Y' else 'PAPER_ON_TOP',
                      excluded=excluded,source_comment=note,
                      cells={x.coordinate:dict(raw=x.value,cached=c[sheet.title][x.coordinate].value,format=x.number_format) for x in sheet[r] if x.value is not None})
            if not excluded:
                def v(col):return value(f'{col}{r}')
                p=SourceProtocol(sheet.title,v('AE' if sw else 'AD'),v('U') if sw else 0)
                raw=RawMeasurements(v('D')/1000,v('E')/1000,v('C' if sw and r==54 else 'B')/100,
                     SectionMeasurement(v('K')/1000,v('N')/1000,v('M')/100),
                     SectionMeasurement(v('L')/1000,v('P')/1000,v('O')/100))
                item['assay']=asdict(reconstruct_source_assay(raw,p))
                groups[tuple(item['condition'])].append(item['assay'])
            else:item['assay_status']='SOURCE_EXCLUDED'
            rows.append(item)
    means=[]
    for group,items in groups.items():
        means.append(dict(condition=group,n_shots=len(items),ey_center_pct=100*sum(x['apparent_section_ey_fraction'][0] for x in items)/len(items),ey_edge_pct=100*sum(x['apparent_section_ey_fraction'][1] for x in items)/len(items),edge_yield_loss_pct=100*sum(x['fractional_edge_loss'] for x in items)/len(items),shot_ey_filtered_pct=100*sum(x['whole_shot_ey_fraction'] for x in items)/len(items)))
    return dict(workbook_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exposure='SOURCE_INTERNAL / TARGET_EXPOSED',
                experimental_rows=rows,retention_rows=retention,condition_means=means,cell_replay=comparisons,unsupported=unsupported,
                discrepancies=[x for x in comparisons if not x['within_frozen_tolerance']],
                headers={s.title:[{x.coordinate:dict(value=x.value,format=x.number_format) for x in row if x.value is not None} for row in s if row[0].value=='Shot'] for s in f})


def compare_exports(root, replay):
    """Compare source CSV display strings using their individual rounding intervals.

    CSVs share workbook lineage: supporting export checks, not an independent
    formula reconstruction. Registry means are a separate comparison artifact.
    """
    import csv
    import hashlib
    from decimal import Decimal, InvalidOperation
    _,cached=inspect_workbook(root/'Espresso water flow experiment.xlsx')
    receipts=[]
    for sheet in cached:
        p=root/f'Espresso water flow experiment - {sheet.title}.csv'
        checked=0; differences=[]
        with p.open(newline='') as stream:
            for row,values in enumerate(csv.reader(stream),1):
                for col,token in enumerate(values,1):
                    actual=sheet.cell(row,col).value
                    if not isinstance(actual,(int,float)) or not token.strip():continue
                    percent=token.endswith('%')
                    try:v=Decimal(token.rstrip('%'))
                    except InvalidOperation:continue
                    half=Decimal(10)**v.as_tuple().exponent/2
                    observed=Decimal(str(actual))*(100 if percent else 1)
                    checked+=1
                    if abs(observed-v)>half+Decimal('1e-12'):
                        differences.append(dict(cell=sheet.cell(row,col).coordinate,export=token,cached=actual))
        receipts.append(dict(sheet=sheet.title,file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),numeric_cells=checked,discrepancies=differences))
    p=root/'edge_ey_condition_means.csv';differences=[]
    with p.open(newline='') as stream:
        for row in csv.DictReader(stream):
            matches=[x for x in replay['condition_means'] if
                     ('Sworks' if x['condition'][0]=='Sworks High Flow' else 'VST18')==row['basket'] and
                     ('traditional' if 'Niche' in x['condition'][1] else 'turbo')==row['shot_style'] and
                     x['condition'][2]==row['puck_screen'] and x['condition'][3].lower()==row['dispersion_block'].lower()]
            if len(matches)!=1:raise ValueError('registry group mapping')
            x=matches[0]
            for key in ('ey_center_pct','ey_edge_pct','edge_yield_loss_pct','shot_ey_filtered_pct'):
                v=Decimal(row[key]);half=Decimal(10)**v.as_tuple().exponent/2
                if abs(Decimal(str(x[key]))-v)>half:
                    differences.append(dict(condition=x['condition'],quantity=key,registry=row[key],reconstructed=x[key],rounding_half_width=str(half)))
    return dict(source_exports=receipts,registry_comparison=dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),discrepancies=differences),role='SHARED_LINEAGE_EXPORT_AND_ROUNDED_CARD_COMPARISON_NOT_FORMULA_ORACLE')
