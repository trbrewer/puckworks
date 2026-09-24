"""Consume frozen endpoint predictions; no refitting or within-shot trajectories."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from puckworks.analysis.smrke2024_transfer import DOC, LEVELS, Fitted, Covariate

COLORS = ['black', '#6b63ed', '#c85ba7', '#fa5c85']


def render(root: Path = DOC):
    source = json.loads((root/'observations.json').read_text())
    fig, ax = plt.subplots(figsize=(9, 6))
    for level, color in zip(LEVELS, COLORS):
        rows = [r for r in source if r['covariate']['level'] == level]
        for ambiguous in (False, True):
            rs = [r for r in rows if bool(r['markers_in_blob'] > 1 or r['note']) == ambiguous]
            ax.scatter([r['covariate']['time_s'] for r in rs], [r['yield_pp'] for r in rs],
                       c=color, marker='x' if ambiguous else 'o',
                       label=f'{LEVELS[level]:g} g'+(' ambiguous' if ambiguous else ' primary'))
    if (root/'predictions.json').exists():
        bundle = json.loads((root/'predictions.json').read_text())
        for model, style in [('M0', '-'), ('B0', '--')]:
            raw = bundle['primary:central']['standard']['A']['1g_fines'][model]['fit']
            fitted = Fitted(**raw)
            ts = np.linspace(*fitted.time_support, 200)
            pp = fitted.predict([Covariate(str(i),float(t),'no_added_fines') for i,t in enumerate(ts)])
            ax.plot(ts,[p['prediction_pp'] for p in pp],style,label=f'{model}, 0 g training support')
    ax.set(xlabel='Machine-reported extraction time (s)', ylabel='Final source-basis yield (pp)',
           title='Across-shot endpoints: source markers and common responses')
    ax.legend(fontsize=8,ncol=2); fig.tight_layout(); fig.savefig(root/'endpoints.png',dpi=160); plt.close(fig)
    if not (root/'residuals.json').exists():
        return
    residuals = json.loads((root/'residuals.json').read_text())
    fig, axs = plt.subplots(1,2,figsize=(12,4),sharey=True)
    for ax, protocol in zip(axs, ('A','B')):
        for j,model in enumerate(('M0','M1','B0','B1')):
            rows = [r for r in residuals if r['treatment']=='primary:central' and r['precision']=='standard'
                    and r['protocol']==protocol and r['model']==model]
            for supported, marker in [(True,'o'),(False,'x')]:
                rs=[r for r in rows if r['time_supported']==supported]
                ax.scatter([LEVELS[r['level']]+.065*(j-1.5) for r in rs], [r['residual_pp'] for r in rs],
                           marker=marker,s=22,label=model+(' supported' if supported else ' time extrap.'))
        ax.axhline(0,color='gray',linewidth=1); ax.set(xlabel='Added fines (g)',title=f'Protocol {protocol}: out-of-fit endpoint residuals',xticks=[0,1,2,4])
        ax.legend(fontsize=6,ncol=2)
    axs[0].set_ylabel('Prediction − source yield (pp)'); fig.tight_layout(); fig.savefig(root/'residuals.png',dpi=160); plt.close(fig)
    reports=json.loads((root/'metrics.json').read_text())['standard']
    fig, axs=plt.subplots(1,2,figsize=(11,4),sharey=True)
    for ax, family in zip(axs,('M','B')):
        for j, inclusion in enumerate(('primary','all')):
            for i,level in enumerate(LEVELS):
                for correction, marker in [('0','o'),('1','s')]:
                    vals=[v['B'][level][family+correction]['supported']['rmse'] for k,v in reports.items() if k.startswith(inclusion+':')]
                    central=reports[inclusion+':central']['B'][level][family+correction]['supported']['rmse']
                    x=i+.12*(j*2+int(correction)-1.5)
                    ax.plot([x,x],[min(vals),max(vals)],color=COLORS[j+int(correction)])
                    ax.scatter([x],[central],marker=marker,color=COLORS[j+int(correction)],label=f'{inclusion} {family+correction}' if i==0 else None)
        ax.set(xticks=range(4),xticklabels=['0','1','2','4'],xlabel='Held-out added fines (g)',title=f'{family} family: tested digitization sensitivities')
        ax.legend(fontsize=8)
    axs[0].set_ylabel('Supported endpoint RMSE (pp)'); fig.tight_layout(); fig.savefig(root/'errors.png',dpi=160); plt.close(fig)


if __name__ == '__main__':
    render()
