#!/usr/bin/env python3
"""Independent-method packet check: raw tokens + exact 3-variable LP vertices.

Does not import/call the analysis producer. Optional --source-dir checks original
PDF streams with pypdf (different PDF engine from recovery). All defaults offline.
"""
import argparse
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path
import re
import tarfile
import hashlib


def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def vertices(intervals):
    # alpha + beta*x - e <= u; -alpha - beta*x - e <= -l;
    # beta <= 0; -e <= 0. All exact intersections of three boundary planes.
    constraints=[]
    for x,(l,u) in enumerate(intervals):
        constraints.extend([((F(1),F(x),F(-1)),u),((F(-1),F(-x),F(-1)),-l)])
    constraints.extend([((F(0),F(1),F(0)),F(0)),((F(0),F(0),F(-1)),F(0))])
    best=None;count=0
    for triple in combinations(constraints,3):
        matrix=[list(a) for a,b in triple];rhs=[b for a,b in triple]
        det=determinant(matrix)
        if det==0:continue
        point=[]
        for col in range(3):
            replaced=[[rhs[i] if j==col else matrix[i][j] for j in range(3)] for i in range(3)]
            point.append(determinant(replaced)/det)
        if all(sum(a*v for a,v in zip(row,point))<=b for row,b in constraints):
            count+=1
            if best is None or point[2]<best:best=point[2]
    assert best is not None
    return best,count


def independent_bounds(value,tick100,tick1000,radius):
    nominal=2+(tick100-value)/(tick100-tick1000)
    samples=[]
    for e0,e1,e2 in product((-radius,radius),repeat=3):
        samples.append(2+(tick100+e1-value-e0)/(tick100+e1-tick1000-e2))
    return nominal,min(samples),max(samples)


def run(root,bundle,source_dir=None):
    raw_path=root/'puckworks/data/matias2023/figure_geometry.json'
    g=json.loads(raw_path.read_text());r=json.loads((bundle/'results.json').read_text())
    source_check='NOT_REQUESTED; compact literal streams inspected'
    if source_dir is not None:
        from pypdf import PdfReader
        from io import BytesIO
        for filename in ('paper.pdf','source.tar'):
            assert hashlib.sha256((source_dir/filename).read_bytes()).hexdigest()==g['source_hashes'][filename]
        with tarfile.open(source_dir/'source.tar') as a:
            pdf=a.extractfile('img/experiment.pdf').read()
        assert hashlib.sha256(pdf).hexdigest()==g['source_hashes']['img/experiment.pdf']
        page=PdfReader(BytesIO(pdf)).pages[0]
        pstream=page.get_contents().get_data()
        assert hashlib.sha256(pstream).hexdigest()==g['source_stream_sha256']
        forms=page['/Resources']['/XObject']
        for name,stream in g['forms'].items():assert forms['/'+name].get_data().decode()==stream
        article=PdfReader(source_dir/'paper.pdf').pages[3]
        embedded=article['/Resources']['/XObject']['/Im3']
        assert embedded.get_data()==pstream
        source_check='PASS; pypdf independently authenticates original member and article streams'
    # Reparse literal source streams, rather than trusting the normalized rows.
    rects=re.findall(r'([\d.]+) ([\d.]+) 3 3 re B',g['forms']['x27'])
    assert len(rects)==10
    ticks=g['calibration']['y_major_segments_tokens']
    a,b=F(ticks[0][1]),F(ticks[1][1]);rho=F(g['calibration']['uniform_coordinate_radius_pt'])
    N=[];G=[];Po=[];Pi=[]
    for i,(rx,ry) in enumerate(rects):
        cy=F(ry)+F(3,2);cx=F(rx)+F(3,2)
        row=r['observations'][i]
        assert F(row['center_native_y'])==cy and F(row['center_native_x'])==cx
        assert i==row['x'] and row['fraction_id']==f'F{i+1:02}'
        z,l,u=independent_bounds(cy,a,b,rho)
        assert [str(v) for v in (z,l,u)]==[row[k] for k in ('z','G_lower','G_upper')]
        N.append((z,z));G.append((l,u))
        vals=re.search(r'([\d.]+) ([\d.]+) m ([\d.]+) ([\d.]+) l S',g['forms'][f'x{i+17}']).groups()
        assert vals[0]==vals[2]
        low=independent_bounds(F(vals[1]),a,b,rho);up=independent_bounds(F(vals[3]),a,b,rho)
        assert [str(v) for v in low]==[row[k] for k in ('L','L_minus','L_plus')]
        assert [str(v) for v in up]==[row[k] for k in ('U','U_minus','U_plus')]
        Po.append((low[1],up[2]));Pi.append((low[2],up[1]))
        h=re.search(r'([\d.]+) ([\d.]+) m ([\d.]+) ([\d.]+) l S',g['forms'][f'x{i+7}']).groups()
        assert F(h[1])==F(h[3])==cy
        assert F(row['horizontal_left_native_x'])==F(h[0]) and F(row['horizontal_right_native_x'])==F(h[2])
        if i<6:
            assert all(abs(F(v)-cy)<2 for v in (vals[1],vals[3]))
            assert row['L_status']==row['U_status']=='COVERED_BUT_RECOVERED'
    assert F(r['observations'][-1]['horizontal_right_native_x'])>F('227.114')
    results={}
    for layer,intervals in [('N',N),('G',G),('P_outer',Po),('P_inner',Pi)]:
        optimum,vertex_count=vertices(intervals)
        c=r['layers'][layer]
        assert optimum==F(c['epsilon'])
        alpha,beta=F(c['alpha']),F(c['beta']);assert beta<=0
        distances=[]
        for i,(l,u) in enumerate(intervals):
            y=alpha+beta*i
            assert l-optimum<=y<=u+optimum
            distances.append(y-min(u,max(l,y)))
        assert max(map(abs,distances))==optimum
        assert list(map(str,distances))==c['interval_distance']
        # Re-evaluate each asserted lower certificate with original interval bounds.
        for identity in c['attaining_constraints']:
            if identity=='NONNEGATIVITY':bound=F(0)
            elif identity.startswith('NONINCREASING:'):
                i,j=[int(v)-1 for v in identity.split(':')[1].split(',')]
                bound=(intervals[j][0]-intervals[i][1])/2
            else:
                p,q=identity.split(':')[1].split('|')
                i,j=[int(v)-1 for v in p.split(',')];k,t=[int(v)-1 for v in q.split(',')]
                bound=((intervals[j][0]-intervals[i][1])*(t-k)-(intervals[t][1]-intervals[k][0])*(j-i))/(2*((j-i)+(t-k)))
            assert bound==optimum
        results[layer]={'epsilon_exact':str(optimum),'feasible_vertices':vertex_count,
                        'original_witness_and_lower_constraints':'PASS'}
    return {'method':'same-session independent-method review; exact LP vertex enumeration; no producer import',
            'source_geometry_check':source_check,'center_vertical_horizontal_counts':[10,20,10],
            'layers':results,'disposition':'PASS','separate_human_audit':False,
            'reviewed_sha256': {str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest()
                for path in [raw_path, root/'puckworks/analysis/matias2023_caffeine_fraction_shape.py',
                             root/'tools/recover_matias2023_figure.py', root/'tests/test_matias_caffeine_fraction_shape.py',
                             bundle/'results.json', bundle/'comparison.png', bundle/'source_overlay.png']}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();bundle=Path(__file__).resolve().parent;root=bundle.parents[2]
    result=run(root,bundle,args.source_dir)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
