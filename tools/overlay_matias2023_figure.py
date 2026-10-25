#!/usr/bin/env python3
"""Optional source overlay; PDF raster is derived CC BY 4.0, Matias et al. 2023."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path


def main():
    import pymupdf
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import numpy as np
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--figure',type=Path,required=True)
    p.add_argument('--geometry',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();g=json.loads(args.geometry.read_text())
    doc=pymupdf.open(args.figure);page=doc[0];pix=page.get_pixmap(matrix=pymupdf.Matrix(4,4),alpha=False)
    pixels=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
    fig,axes=plt.subplots(1,3,figsize=(13,5),gridspec_kw={'width_ratios':[2.5,1,1]})
    for ax in axes:
        ax.imshow(pixels,extent=(0,float(page.rect.width),float(page.rect.height),0))
        for s in g['observations']:
            x,y,w,h=map(lambda v:float(F(v)),s['marker_rectangle_tokens'])
            ax.add_patch(Rectangle((x,y),w,h,facecolor='none',edgecolor='#E69F00',lw=.8))
            ax.plot(x+w/2,y+h/2,'+',color='#D55E00',ms=4,mew=.8)
            v=list(map(float,s['vertical_tokens']));hh=list(map(float,s['horizontal_tokens']))
            ax.plot([v[0],v[2]],[v[1],v[3]],color='#CC79A7',lw=.8)
            ax.plot([hh[0],hh[2]],[hh[1],hh[3]],color='#009E73',lw=.8)
        ax.axvline(227.114,color='#D55E00',ls='--',lw=.6)
        ax.set_aspect('equal')
    axes[0].set(xlim=(0,238.8),ylim=(166.5,0),title='Source render + recovered geometry (native points)')
    axes[1].set(xlim=(70,81),ylim=(41,29),title='F02: covered SE endpoints')
    axes[2].set(xlim=(220,234),ylim=(116,101),title='F10: stored geometry past clip')
    fig.text(.5,.03,'Orange: complete square outline; red +: center; magenta: vertical endpoints; green: horizontal segment (semantics unresolved).\n'
             'Dashed red: right clip. Overlays show recovered centerlines, including covered/clipped geometry; no inferred SE.\n'
             'CC BY 4.0 · derived/annotated from Matias et al. (2023), arXiv:2304.03161v2 Fig. 3 · source recovery, not physical validation.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.15,1,1))
    fig.savefig(args.output,dpi=150,bbox_inches='tight',metadata={'Software':'Puckworks Matias source geometry overlay'})
    plt.close(fig)


if __name__=='__main__':main()
