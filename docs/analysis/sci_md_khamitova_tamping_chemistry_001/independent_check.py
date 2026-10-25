"""Independent-method review: no import of the analysis producer or audit script.

Read the original CSVs directly and use PyMuPDF's positioned words as a second
PDF extraction engine. PDF and optional PyMuPDF are needed only for this review.
"""
import argparse
import csv
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import re

FORCES = (10,15,20,30)
TABLES = [('total CQA','Table_5.2_Total_CQA_concentration.csv'),
          ('caffeine','Table_5.3_Caffeine_concentration.csv'),
          ('trigonelline','Table_5.4_Trigonelline_concentration.csv'),
          ('nicotinic acid','Table_5.5_Nicotinic_acid_concentration.csv')]


def check(root, pdf):
    import pymupdf
    bundle=root/'docs/analysis/sci_md_khamitova_tamping_chemistry_001'
    data=root/'puckworks/data/khamitova2020'
    expected_hash='59065ee31eb23c694c53dd1c7702c141d5c29bdd79413933e1b62e2fc70aa229'
    assert len(pdf.read_bytes()) == 5146825
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == expected_hash
    doc=pymupdf.open(pdf)
    assert len(doc)==189
    audit=list(csv.DictReader((bundle/'cell_audit.csv').open()))
    audit_by_key={(r['analyte'],int(r['temperature_C']),int(r['pressure_bar']),int(r['tamp_force_kgf'])):r for r in audit}
    source={}
    for page in (115,116,117):
        words=doc[page-1].get_text('words')
        rows={}
        for w in words:
            if re.fullmatch(r'\d+\.\d+',w[4]):
                rows.setdefault(round(w[1],1),[]).append((w[0],w[4]))
        for y, values in sorted(rows.items()):
            assert len(values)==12
            ti=(0 if page==115 else (1 if y<400 else 2) if page==116 else (2 if y<300 else 3))
            label=[w[4] for w in sorted(words,key=lambda w:w[0]) if abs(w[1]-y)<3 and w[0]<130]
            assert label[1] in ('bar','bar,') and label[2] in ('880C','930C','980C')
            pressure,temp=int(label[0]),int(label[2][:2])
            values=[v for x,v in sorted(values)]
            for j,f in enumerate(FORCES):
                key=(TABLES[ti][0],temp,pressure,f)
                assert key not in source
                source[key]=values[3*j:3*j+3]
                r=audit_by_key[key]
                assert [r[n] for n in ('amount_string','concentration_string','rsd_string')]==source[key]
                assert int(r['pdf_page'])==page and int(r['printed_page'])==page-17
                assert r['source_row_label']==' '.join(label).replace('0C','⁰C')
    assert len(source)==144
    ground_words=doc[117].get_text('words')
    ground=[w[4] for w in sorted(ground_words,key=lambda w:w[0])
            if 610<w[1]<620 and re.fullmatch(r'\d+\.\d+',w[4])]
    assert ground==['37.17','0.1','16.24','7.0','8.55','9.9','0.36','2.6']
    assert ground==[r['source_string'] for r in csv.DictReader((bundle/'ground_audit.csv').open())]
    result=json.loads((bundle/'results.json').read_text())
    produced={(r['analyte'],r['temperature_C'],r['pressure_bar']):r for r in result['blocks']}
    selected=[]
    for name,filename in TABLES:
        for raw in csv.DictReader((data/filename).open()):
            temp,pressure=int(raw['temperature_C']),int(raw['pressure_bar'])
            y=[F(raw[f'{f}kgF_mg_per_40ml']) for f in FORCES]
            r=[F(raw[f'{f}kgF_RSD_pct']) for f in FORCES]
            for j,f in enumerate(FORCES):
                assert list(map(F,source[name,temp,pressure,f])) == [y[j],F(raw[f'{f}kgF_mg_per_ml']),r[j]]
            b=produced[name,temp,pressure]
            distances={(i,j):abs(y[i]-y[j]) for i,j in combinations(range(4),2)}
            # Independently compute the diameter from all six pair distances.
            diameter=max(distances.values());cost=diameter/2;center=min(y)+cost
            assert F(b['R'])==diameter and F(b['E'])==cost and F(b['c_star'])==center
            assert all(abs(v-center)<=cost for v in y)
            assert F(b['Delta'])==y[3]-y[0]
            assert F(b['Percent_change'])==100*(y[3]-y[0])/y[0]
            assert F(b['E_percent_reference'])==100*cost/y[0]
            assert F(b['endpoint_missed_range'])==diameter-abs(y[3]-y[0])
            assert b['minimum_forces']==[f for f,v in zip(FORCES,y) if v==min(y)]
            assert b['maximum_forces']==[f for f,v in zip(FORCES,y) if v==max(y)]
            scales=[v*rsd/100 for v,rsd in zip(y,r)]
            pairs={p:d/(scales[p[0]]+scales[p[1]]) for p,d in distances.items()}
            lam=max(pairs.values())
            assert F(b['lambda_star'])==lam
            assert b['lambda_attaining_pairs']==[[FORCES[i],FORCES[j]] for (i,j),v in pairs.items() if v==lam]
            # Check the constructed-interval interpretation directly, not just ratio equality.
            assert max(v-lam*s for v,s in zip(y,scales))==min(v+lam*s for v,s in zip(y,scales))
            # Actual source has equal 0.01 printed units: extrema stay separated.
            assert diameter>F('.01')
            assert F(b['E_lower'])==cost-F('.005') and F(b['E_upper'])==cost+F('.005')
            assert F(b['Delta_lower'])==y[3]-y[0]-F('.01')
            assert F(b['Delta_upper'])==y[3]-y[0]+F('.01')
            if (temp,pressure) in ((88,7),(93,7),(98,9)):
                selected.append(dict(analyte=name,temperature_C=temp,pressure_bar=pressure,
                    E=str(cost),Delta=str(y[3]-y[0]),missed_range=b['endpoint_missed_range'],lambda_star=str(lam)))
    # Exact rational pair-consistency comparison for all source columns.
    bad=[]
    for key,(a,c,r) in source.items():
        a,c=F(a),F(c)
        if max(a-F('.005'),40*(c-F('.005')))>min(a+F('.005'),40*(c+F('.005'))):bad.append(key)
    assert bad==[('total CQA',88,7,10)]
    assert len(produced)==36 and set(produced)==set(product([t[0] for t in TABLES],(88,93,98),(7,9,11)))
    return dict(disposition='PASS_INDEPENDENT_METHOD_CHECK',
        independence='Separate extraction engine and direct-CSV calculation; same-session audit, not a claim of an independent human reviewer.',
        pdf_sha256=expected_hash,source_strings_rechecked=440,observation_keys_rechecked=144,
        complete_blocks_recomputed=36,source_pair_mismatches=bad,selected_calculations=selected,
        reviewed_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [root/'puckworks/analysis/khamitova2020_tamping_chemistry.py',bundle/'cell_audit.csv',
                      bundle/'ground_audit.csv',bundle/'source_metadata.json',bundle/'results.json',bundle/'chemistry.png']})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path('.'))
    p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=check(a.root,a.pdf)
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(r['disposition'],r['source_strings_rechecked'],r['complete_blocks_recomputed'])
