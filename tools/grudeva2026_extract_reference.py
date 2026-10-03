"""Offline raster-coordinate extraction from the CC-BY EJAM PDF, never solver output."""
from PIL import Image
import numpy as np,json,pathlib,hashlib
import argparse, tempfile, shutil
import pymupdf
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--article-pdf',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
temporary=tempfile.TemporaryDirectory(prefix='grudeva-reference-')
p=pathlib.Path(temporary.name)
shutil.copyfile(args.article_pdf,p/'article.pdf')
document=pymupdf.open(args.article_pdf)
for page_number in (18,19):
    for index,metadata in enumerate(document[page_number].get_images()):
        asset=document.extract_image(metadata[0])
        (p/f"figure-page{page_number+1}-{index}.{asset['ext']}").write_bytes(asset['image'])
f4=p/'figure-page20-0.png';im=np.array(Image.open(f4).convert('RGB'))
mask=(np.ptp(im.astype(float),axis=2)<5)&(im.mean(axis=2)>95)&(im.mean(axis=2)<170)
rows=[]
for t in [6.42,6.45,6.5,6.55,6.6,6.65,6.7,6.8]:
 x=round(95+(t-4)*798/4);ys=np.where(mask[180:565,x])[0]+180
 rows.append({'t':4+(x-95)*4/798,'c':(571-float(np.median(ys)))/476,'pixel_x':x,'pixel_y':float(np.median(ys)),'c_uncertainty':float((ys.max()-ys.min()+2)/2/476),'t_uncertainty':2*4/798})
f3=p/'figure-page19-0.jpeg';im=np.array(Image.open(f3).convert('RGB'))
mask=(np.ptp(im.astype(float),axis=2)<8)&(im.mean(axis=2)>90)&(im.mean(axis=2)<165)
r3=[]
# Unoccluded gray curve segments: omit overlapping colored curves, captions, grid and jump.
for t,xs,low in [(.4,[128,129,130],442),(3.2,[405,410,415,420,423],450),(4.8,[570,575,580,585,590],490),(6.4,[735,740,745,750,755,760],495)]:
 for x in xs:
  ys=np.where(mask[low:625,x])[0]+low
  if len(ys):r3.append({'t':t,'z':(x-88)/677,'c':(641-float(np.median(ys)))/526,'pixel_x':x,'pixel_y':float(np.median(ys)),'c_uncertainty':float((ys.max()-ys.min()+4)/2/526),'z_uncertainty':2/677})
d={'source':{'doi':'10.1017/S095679252500018X','authors':'Grudeva, Moroney and Foster','license':'CC-BY-4.0','article_sha256':hashlib.sha256((p/'article.pdf').read_bytes()).hexdigest(),'figure3_sha256':hashlib.sha256(f3.read_bytes()).hexdigest(),'figure4_sha256':hashlib.sha256(f4.read_bytes()).hexdigest(),'method':'PDF embedded raster extraction; grayscale isolation in declared unoccluded columns; median centerline, pixel-width uncertainty; manual axis calibration','curve_identity':'epsilon -> 0, asymptotic, gray','axes':'dimensionless z,t,c_l; linear','calibration':{'figure3':{'z0_x':88,'z1_x':765,'c0_y':641,'c1_y':115},'figure4':{'t4_x':95,'t8_x':893,'c0_y':571,'c1_y':95}},'limitations':'Raster resolution, JPEG artifacts and curve occlusion; selected supported samples only; not author arrays or original MSE grid'},'figure3':r3,'figure3_fronts':[{'t':t,'z':(x-88)/677,'z_uncertainty':2/677} for t,x in [(.4,133),(3.2,429),(4.8,598)]],'figure4':rows,'figure4_event':{'t':4+(570.5-95)*4/798,'t_uncertainty':2*4/798},'figure5':{'status':'FIG5_REFERENCE_INCOMPLETE','times':[.4,3.2,4.8,6.4],'epsilon_labels':[.01,.0075,.005,.0025],'reason':'No qualified full-model spatial arrays, exact diffusivity coefficient or author observation grid. Raster Figure 5 errors alone cannot verify the implementation.'}}
(p/'publication_reference.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'fig3_samples':len(r3),'fig4_samples':len(rows),'event':d['figure4_event']}))

args.output.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(p/'publication_reference.json',args.output)
temporary.cleanup()
