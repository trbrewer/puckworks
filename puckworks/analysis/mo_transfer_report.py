"""Reproducible audit and predictor-only checks; never fits the Mo responses."""
import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from puckworks import data
from .mo_transfer import Bed, simulate, populations, radial_geometry, particle_derivative

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT/'docs/analysis/sci_md_mo_transfer_001'


def write_json(path, value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def audit(out):
    rows=data.mo2_yield_strength()
    source=ROOT/'puckworks/data/mo2023_2/figs6_9_yield_strength.csv'
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    register=[]
    for i,r in enumerate(rows,1):
        p,q,m=r['powder'],int(r['q_mL_s']),r['M_c_g']
        register.append(dict(row_id=f'mo2-{p}-q{q}-r{i:02}',condition_id=f'{p}-q{q}',
            source_csv=str(source.relative_to(ROOT)),source_row=i,source_sha256=sha,
            source_figure={'E':7,'M':8,'F':9}[p],source_pdf_page=30 if p=='F' else 29,
            powder=p,flow_mL_s=q,mass_g=m,support='measured tabulated coordinate; no extrapolation',
            ey_unit='percent (denominator unresolved)',strength_unit='cumulative mass percent',
            ey_bar_status='digitized SD' if r['yield_err_pct'] else 'zero digitized entry; uncertainty unknown',
            strength_bar_status='digitized SD' if r['strength_err_pct'] else 'zero digitized entry; uncertainty unknown',
            rounding='mass integer g, response .001 percentage point; digitization bound not established',
            inclusion='SOURCE_AUDIT_ONLY',exclusion_reason='BLOCKED_SOURCE_CONTRACT',
            identity_residual_7p5g_ey_pp=r['yield_pct']-r['strength_pct']*m/7.5,
            identity_residual_15g_ey_pp=r['yield_pct']-r['strength_pct']*m/15))
    with (out/'observation_register.csv').open('w') as f:
        w=csv.DictWriter(f,register[0].keys(),lineterminator='\n');w.writeheader();w.writerows(register)
    return register


def verification(out):
    # Explicit hypothetical half-collection observer. It is NOT source qualification.
    bed=Bed(.015,.029,.0135,.17,1000,.5)
    table={r['powder']:r for r in data.mo2_granulometry()}
    coordinates=data.mo2_yield_strength()
    # Three predictor-only representative/extreme cases fixed before execution.
    cases=[('E',2,.1,'slow'),('M',3,.8,'middle'),('F',4,2.,'fast')]
    kinetics={'S0':[1e-5,.05,1e3],'S2':[1e-5,.05,1e3],'D2':[1e-13,1e-10,2e-9]}
    resolutions=[(24,12,1e-7,1e-10),(48,24,1e-7,1e-10),
                 (96,48,1e-7,1e-10),(96,48,1e-9,1e-12)]
    records=[]; differences=[]
    for candidate in ['S0','S2','D2']:
        for ci,(powder,flow,partition,label) in enumerate(cases):
            masses=np.array([r['M_c_g']/1000 for r in coordinates
                             if r['powder']==powder and r['q_mL_s']==flow])
            wi,ri=populations(table[powder])
            previous=[]
            for nz,nr,rtol,atol in resolutions:
                rec=dict(candidate=candidate,case=label,powder=powder,flow_mL_s=flow,
                         inventory_fraction=1,kinetic=kinetics[candidate][ci],partition=partition,
                         nz=nz,nr=nr,rtol=rtol,atol=atol,mass_g=(1000*masses).tolist())
                print(f'verify {candidate} {label} {nz}/{nr} rtol={rtol}',flush=True)
                try:
                    r=simulate(candidate,bed,wi,ri,flow*1e-6,1,kinetics[candidate][ci],
                               partition,masses,nz=nz,nr=nr,rtol=rtol,atol=atol)
                    for k in ['ey_pct','strength_pct','solute_balance_relative','water_balance_relative',
                              'min_state_inventory_fraction','positivity_tolerance_inventory_fraction',
                              'solver_calls','nfev','njev','nlu']:
                        rec[k]=r[k].tolist() if isinstance(r[k],np.ndarray) else r[k]
                    rec['prebreakthrough_solute_kg']=float(np.max(r['trajectory_delivered_kg'][r['trajectory_cup_m3']==0]))
                    rec['status']='COMPLETED'
                    previous.append(np.array(rec['ey_pct']))
                except (ValueError,RuntimeError,FloatingPointError) as exc:
                    rec.update(status='NUMERICAL_FAILURE',reason=str(exc))
                    if str(exc) in ('negative mass or delivered-solute regression','solute balance failure'):
                        rec['solver_calls']=nz+1
                        rec['solver_calls_provenance']='reconstructed from post-loop rejection after all nz+1 phase solves; not a new execution'
                        rec['failure_extrema_status']='not retained by original exception; no retry'
                    previous.append(None)
                records.append(rec)
                write_json(out/'numerical_records.json',records)
            if all(p is not None for p in previous):
                # Empirical estimate only; no assumed asymptotic order.
                delta=np.abs(previous[1]-previous[2])+np.abs(previous[2]-previous[3])
                differences.append(dict(candidate=candidate,case=label,mass_g=(1000*masses).tolist(),
                    coarse_medium_max_ey_pp=float(np.max(abs(previous[0]-previous[1]))),
                    medium_fine_max_ey_pp=float(np.max(abs(previous[1]-previous[2]))),
                    tolerance_max_ey_pp=float(np.max(abs(previous[2]-previous[3]))),
                    allowance_by_mass_ey_pp=delta.tolist(),max_allowance_ey_pp=float(delta.max()),
                    derived_strength_allowance_pct=(delta*.0075/masses).tolist(),
                    ceiling_pass=bool(delta.max()<=.1)))
    radial=[]
    t=np.array([.01,.03,.1,.3]); n=np.arange(1,500)
    exact=6/np.pi**2*np.sum(np.exp(-np.pi**2*t[:,None]*n*n)/(n*n),axis=1)
    for nr in [24,48,96]:
        w,_,_=radial_geometry(nr)
        def rhs(t,s):
            return particle_derivative(s.reshape(1,1,nr),np.ones((1,1)),np.ones(1),
                                       np.zeros(1),1,1,'D2')[0].ravel()
        r=solve_ivp(rhs,(0,t[-1]),w,t_eval=t,method='BDF',rtol=1e-9,atol=1e-12)
        radial.append(dict(nr=nr,max_remaining_fraction_error=float(abs(r.y.sum(axis=0)-exact).max()),
                           solver_calls=1,nfev=r.nfev,completed=bool(r.success)))
    write_json(out/'numerical_summary.json',dict(scope='synthetic assumed observer; not fitted resolution qualification',
        hypothetical_bed=asdict(bed),trajectories_launched=len(records),
        trajectories_completed=sum(r['status']=='COMPLETED' for r in records),
        failed_trajectories=[r for r in records if r['status']!='COMPLETED'],
        solver_calls_completed_trajectories=sum(r.get('solver_calls',0) for r in records if r['status']=='COMPLETED'),
        total_bed_solver_calls=sum(r.get('solver_calls',0) for r in records),
        rejected_trajectory_solver_calls_reconstructed=sum(r.get('solver_calls',0) for r in records if r['status']!='COMPLETED'),
        status='NUMERICALLY_UNRESOLVED' if any(r['status']!='COMPLETED' for r in records) or any(not d['ceiling_pass'] for d in differences) else 'SYNTHETIC_CASES_PASS',
        reason='four post-solve positivity/monotonicity rejections and empirical refinement allowances over0.10 EY pp',
        radial_reference_trajectories=radial,comparisons=differences,
        no_response_values_used=True, fitting_resolution_selected=False))


def legacy(out):
    from puckworks.models.mo2023_2.coupled_bed import simulate_bed, yield_strength_curve
    a=simulate_bed('M',3,dose_g=7.5,t_end=15,N_z=8,M=8,n_save=240,filling_front=True)
    b=simulate_bed('M',3,dose_g=15,t_end=15,N_z=8,M=8,n_save=240,filling_front=True)
    lo=yield_strength_curve('M',3,[10],20,N_z=8,M=8,filling_front=True)
    hi=yield_strength_curve('M',3,[10],40,N_z=8,M=8,filling_front=True)
    write_json(out/'legacy_diagnostic.json',dict(scope='historical implementation diagnostic only; gates unchanged',
        trajectories_launched=4,trajectories_completed=4,solver_calls=4,
        prebreakthrough_eluted_fraction=float(a['eluted_frac'][a['beverage_g']==0].max()),
        max_balance_deviation=float(abs(a['mass_balance']-1).max()),
        dose_argument_changes_output=not np.array_equal(a['yield_frac'],b['yield_frac']),
        inventory_scale_ratio_ey=hi[10][0]/lo[10][0],inventory_scale_ratio_strength=hi[10][1]/lo[10][1],
        support_policy='np.interp endpoint clamps in legacy; new observer rejects out-of-support requests',
        reduced_implementation='Inspected extraction.py: separate fine/coarse lumped calls share Q but not one axial liquid field; historical swelling contrast preserved'))


def figures(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=data.mo2_yield_strength()
    for powder in 'EMF':
        for q in [2,3,4]:
            rr=[r for r in rows if r['powder']==powder and r['q_mL_s']==q]
            fig,ax=plt.subplots(figsize=(5,3))
            ax.plot([r['M_c_g'] for r in rr],[r['yield_pct'] for r in rr],'o',label='retained digitized means')
            known=[r for r in rr if r['yield_err_pct']>0]
            ax.errorbar([r['M_c_g'] for r in known],[r['yield_pct'] for r in known],
                        yerr=[r['yield_err_pct'] for r in known],fmt='none',label='nonzero digitized SD')
            ax.set(xlabel='Collected mass (g; mapping unresolved)',ylabel='Published yield (%)',
                   title=f'{powder}, {q} mL/s — source audit only')
            ax.text(.98,.03,'Predictions withheld: source contract blocked\nZero bars: unknown uncertainty',
                    transform=ax.transAxes,ha='right',fontsize=7)
            ax.legend(fontsize=7);fig.tight_layout();fig.savefig(out/f'observations_{powder}_q{q}.png',dpi=110);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3))
    for powder in 'EMF':
        rr=[r for r in rows if r['powder']==powder]
        for ax,dose in zip(axes,[7.5,15]):
            ax.scatter([r['M_c_g'] for r in rr],
                       [r['yield_pct']-r['strength_pct']*r['M_c_g']/dose for r in rr],s=15,label=powder)
            ax.axhline(0,color='gray',lw=.6)
            ax.set(title=f'Explicit source alternative: {dose:g} g',xlabel='Collected mass (g)',ylabel='EY identity residual (pp)')
    axes[0].legend();fig.suptitle('Dimensional audit only — not dose inference or fit');fig.tight_layout()
    fig.savefig(out/'strength_consistency.png',dpi=110);plt.close(fig)
    summary=json.loads((out/'numerical_summary.json').read_text())
    rec=json.loads((out/'numerical_records.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(12,3.3))
    for candidate in ['S0','S2','D2']:
        rr=[r for r in summary['comparisons'] if r['candidate']==candidate]
        axes[0].plot([r['case'] for r in rr],[r['max_allowance_ey_pp'] for r in rr],'o-',label=candidate)
    axes[0].axhline(.1,color='red',ls='--');axes[0].set(ylabel='Empirical EY allowance (pp)',title='Hypothetical observer, inventory=1')
    for k,field,limit in [(1,'solute_balance_relative',1e-6),(2,'water_balance_relative',1e-8)]:
        vals=[max(r[field],1e-18) for r in rec if r['status']=='COMPLETED']
        axes[k].semilogy(vals,'.');axes[k].axhline(limit,color='red',ls='--');axes[k].set(title=field,xlabel='Trajectory index')
    axes[0].legend();fig.tight_layout();fig.savefig(out/'numerical_checks.png',dpi=110);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['audit','verify','legacy','figures'])
    parser.add_argument('--output',type=Path,default=BUNDLE)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    {'audit':audit,'verify':verification,'legacy':legacy,'figures':figures}[args.action](args.output)


if __name__=='__main__':
    main()
