"""Optional source audit; requires external complete PDF and Poppler, never reproduction.

The audit was visually checked against PDF pages 115–118. This script alone does
not authenticate download completeness or replace that visual check.
"""
import argparse
import csv
from fractions import Fraction
import hashlib
from pathlib import Path
import re
import subprocess

TABLES = (
    ('total CQA', '5.2', 'Table_5.2_Total_CQA_concentration.csv'),
    ('caffeine', '5.3', 'Table_5.3_Caffeine_concentration.csv'),
    ('trigonelline', '5.4', 'Table_5.4_Trigonelline_concentration.csv'),
    ('nicotinic acid', '5.5', 'Table_5.5_Nicotinic_acid_concentration.csv'),
)
PDF_HASH = '59065ee31eb23c694c53dd1c7702c141d5c29bdd79413933e1b62e2fc70aa229'


def audit(pdf, data, output):
    raw = pdf.read_bytes()
    if len(raw) != 5146825 or hashlib.sha256(raw).hexdigest() != PDF_HASH:
        raise ValueError('Expected authenticated complete official PDF')
    pages = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-']).decode().split('\f')
    rows = []
    for n in range(115, 118):
        for line in pages[n-1].splitlines():
            label = re.match(r'\s*((7|9|11) bar,?\s*(88|93|98)0C)\s+(.*)', line)
            if not label:
                continue
            # Table 5.4 begins after all nine caffeine rows and continues on p100.
            if n == 115:
                ti = 0
            elif n == 116:
                ti = 1 if len(rows) < 72 else 2
            else:
                ti = 2 if len(rows) < 108 else 3
            analyte, table, filename = TABLES[ti]
            values = label[4].split()
            if len(values) != 12 or not all(re.fullmatch(r'\d+\.\d+', x) for x in values):
                raise ValueError(('Ambiguous text; inspect raster', n, line))
            source_rows = list(csv.DictReader((data/filename).open()))
            condition = next(r for r in source_rows if r['pressure_bar'] == label[2]
                             and r['temperature_C'] == label[3])
            for j, force in enumerate((10,15,20,30)):
                a,c,r = values[3*j:3*j+3]
                for s, suffix in zip((a,c,r), ('mg_per_40ml','mg_per_ml','RSD_pct')):
                    assert Fraction(s) == Fraction(condition[f'{force}kgF_{suffix}'])
                rows.append(dict(analyte=analyte, temperature_C=label[3], pressure_bar=label[2],
                    tamp_force_kgf=force, table=table, printed_page=n-17, pdf_page=n,
                    source_row_label=label[1].replace('0C','⁰C'), source_force_label=f'{force}kgF',
                    amount_string=a, concentration_string=c, rsd_string=r,
                    amount_decimal_places=len(a.split('.')[1]),
                    concentration_decimal_places=len(c.split('.')[1]), rsd_decimal_places=len(r.split('.')[1]),
                    csv_file=filename, csv_row_1based=source_rows.index(condition)+2,
                    mean_support='SUPPORTED', rsd_support='SUPPORTED', precision_support='SUPPORTED',
                    audit_status='NUMERIC_AGREEMENT_VISUALLY_CHECKED'))
    assert len(rows) == 144
    output.mkdir(parents=True,exist_ok=True)
    with (output/'cell_audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
    line=next(x for x in pages[117].splitlines() if re.match(r'\s+1g\s+37',x))
    values=line.split()[1:]
    assert len(values)==8
    source=list(csv.DictReader((data/'Table_5.6_Ground_coffee.csv').open()))[0]
    ground=[]
    for (name,_,_),key,j in zip(TABLES,('total_CQA','caffeine','trigonelline','nicotinic_acid'),range(4)):
        for kind,suffix,k in [('mg/10ml','mg_per_10ml',0),('RSD','RSD_pct',1)]:
            s=values[2*j+k]
            assert Fraction(s)==Fraction(source[f'{key}_{suffix}'])
            ground.append(dict(analyte=name,table='5.6',printed_page=101,pdf_page=118,
                source_row_label='1 g',source_column_label=kind,source_string=s,
                decimal_places=len(s.split('.')[1]),csv_column=f'{key}_{suffix}',
                audit_status='NUMERIC_AGREEMENT_VISUALLY_CHECKED'))
    with (output/'ground_audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ground[0]),lineterminator='\n');w.writeheader();w.writerows(ground)
    print('144 keys / 432 chemistry entries and eight ground entries agree numerically.')
    # Captions and labels are separately retained in source_metadata.json.


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--data',type=Path,default=Path('puckworks/data/khamitova2020'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.pdf,a.data,a.output)
