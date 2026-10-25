#!/usr/bin/env python3
"""Independent review check for SCI-MD-FOSTER-RADIAL-FRONT-001.

Optional review dependencies: numpy, scipy, PyMuPDF. Does not import the producer.
The floating LP results are corroboration, not strict numerical certificates.
An exact Fraction check of the nominal feasible witness follows the LP check.
Source membership/visibility requires the separate substantive raster review.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,argparse
import numpy as np
from scipy.optimize import linprog
parser=argparse.ArgumentParser(description='Independent fixed-cohort affine LP cross-check; no producer arithmetic import')
parser.add_argument('--root','--repo',dest='repo',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--pdf',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
ROOT=args.repo; B=ROOT/'docs/analysis/sci_md_foster_radial_front_001'; D=json.loads((ROOT/'puckworks/data/foster2025_2/fig8_fig9_radial_front.json').read_text()); R=json.loads((B/'scan_results.json').read_text())
# Independent construction: explicit latent ordinates and affine pixel inequalities.
keys=['a9','b9','a8','b8']
for row in D['observations']:
 for f in ['center','lower_endpoint','upper_endpoint']:
  if row[f]['support']=='SUPPORTED':keys.append(row['observation_id']+f)
keys += ['epi']
ix={k:i for i,k in enumerate(keys)}; N=len(keys); A=[]; bb=[]
def con(terms,b):
 v=np.zeros(N)
 for k,x in terms.items():v[ix[k]]=float(x)
 A.append(v);bb.append(float(b))
for cal,prefix in [(D['calibrations']['fig9_ticks'],'9'),(D['calibrations']['fig8_ticks'],'8')]:
 for tick in cal['ticks']:
  p,h,z=tick['p'],tick['allowance'],tick['z']
  con({'a'+prefix:p-h,'b'+prefix:1},z); con({'a'+prefix:-(p+h),'b'+prefix:-1},-z)
for row in D['observations']:
 id=row['observation_id']; fs=[]
 for f in ['lower_endpoint','center','upper_endpoint']:
  r=row[f]
  if r['support']=='SUPPORTED':
   lo,hi=r['enclosure_px']; k=id+f;fs.append(k)
   con({'a9':lo,'b9':1,k:-1},0);con({'a9':-hi,'b9':-1,k:1},0)
 for f,g in zip(fs,fs[1:]):con({f:1,g:-1},0)
 for dup in row['duplicate_records']:
  if dup['linkage']=='AUTHENTICATED_SHARED_CENTER':
   lo,hi=dup['center']['enclosure_px'];k=id+'center'
   con({'a8':lo,'b8':1,k:-1},0);con({'a8':-hi,'b8':-1,k:1},0)
bounds=[(None,None)]*N
bounds[ix['a9']]=(0,None);bounds[ix['a8']]=(0,None)
A=np.array(A);bb=np.array(bb)
def solve(obj,extra=()):
 c=np.zeros(N)
 for k,v in obj.items():c[ix[k]]=v
 aa=[]
 for terms in extra:
  v=np.zeros(N)
  for k,x in terms.items():v[ix[k]]=x
  aa.append(v)
 a=np.vstack([A,aa]) if aa else A;b=np.r_[bb,np.zeros(len(aa))]
 res=linprog(c,A_ub=a,b_ub=b,bounds=bounds,method='highs')
 assert res.success,res.message
 return res.fun
result={}
for t in [3,4,5]:
 rows=[r for r in D['observations'] if r['scan_label_s']==t]
 C=[r['observation_id']+'center' for r in rows];L=[r['observation_id']+'lower_endpoint' for r in rows];U=[r['observation_id']+'upper_endpoint' for r in rows]
 ep=[{i:1,j:-1,'epi':-1} for i in C for j in C if i!=j]+[{'epi':-1}]
 e_min=solve({'epi':.5},ep)
 e_max=max(-solve({i:-.5,j:.5}) for i in C for j in C if i!=j)
 complete_g=all(k in ix for k in L+U)
 g_min=solve({'epi':1},[{i:1,j:-1,'epi':-1} for i in L for j in U]) if complete_g else None
 g_max=max(-solve({i:-1,j:1}) for i in L for j in U) if complete_g else None
 d_min=solve({C[-1]:1,C[0]:-1});d_max=-solve({C[-1]:-1,C[0]:1})
 result[t]={'E':(e_min,e_max),'D':(d_min,d_max),'G':(g_min,g_max)}
 for k,(lo,hi) in result[t].items():
  if lo is None:
   assert R['scans'][t][k]['status']=='UNSUPPORTED_COMPLETE_COHORT'
   continue
  z=R['scans'][t][k]['bounds']; assert float(F(z['exact_lower']))<=lo+1e-8 and float(F(z['exact_upper']))>=hi-1e-8
# This is a numerical independent cross-check only, not source certificate.
print(json.dumps(result,indent=2));(args.output/'lp_crosscheck.json').write_text(json.dumps(result,indent=2)+'\n')
# Independently verify exact nominal witness against all explicit inequalities.
w=[None]*N
for prefix,cal in [('9',D['calibrations']['fig9_ticks']),('8',D['calibrations']['fig8_ticks'])]:w[ix['a'+prefix]]=F(cal['nominal_alpha']);w[ix['b'+prefix]]=F(cal['nominal_beta'])
for row in D['observations']:
 for f in ['center','lower_endpoint','upper_endpoint']:
  if row[f]['support']=='SUPPORTED':w[ix[row['observation_id']+f]]=w[ix['a9']]*F(row[f]['nominal_px'])+w[ix['b9']]
w[ix['epi']]=F(0)
# Original A entries are half-integer/integer, exactly recoverable from float string.
assert all(sum(F(str(coef))*wi for coef,wi in zip(ar,w)) <= F(str(b)) for ar,b in zip(A,bb))
print('Exact nominal witness satisfies all',len(A),'explicit global constraints.')
# Match source actual native figures independently.
import pymupdf
pdf=args.pdf;doc=pymupdf.open(pdf)
imgs={}
for page in doc:
 for im in page.get_images(full=True):
  raw=doc.extract_image(im[0]); sha=hashlib.sha256(raw['image']).hexdigest()
  for name,r in D['images'].items():
   if sha==r['sha256']:imgs[name]=sha
assert set(imgs)=={'fig6','fig7','fig8','fig9'}
print('Native source images independently match',imgs)
