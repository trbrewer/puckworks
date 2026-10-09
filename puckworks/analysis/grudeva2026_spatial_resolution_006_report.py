"""One complete charged 006 reduction; pairwise gates and common support stay distinct."""
from __future__ import annotations

from pathlib import Path
import numpy as np

from . import grudeva2026_spatial_resolution_006 as task
from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_report as inherited
from . import grudeva2026_baseline_observation_005_diagnosis as diagnosis
from . import grudeva2026_baseline_observation_005_attribution as attribution


def disposition(screen_passed, integrity, gates, comparison):
    if not screen_passed:
        return 'B'
    required_gates = {'complete_status','solver_segments','horizon','events','activation_support','required_times',
        'conservation','aqueous_bounds','grain_bounds','phase_bounds','front_support','cup_quadrature',
        'cup_state_integral','independent_inventory_sums','public_inventory_algebra','public_profile_reconstruction',
        'public_cup_outlet_reconstruction','diagnostic_inlet','tail_weights_rates','diagnostic_liquid_profile_bounds',
        'diagnostic_grain_profile_bounds','diagnostic_grain_history_bounds'}
    if not integrity or set(gates) != required_gates or set(comparison) != set(inherited.BUDGETS):
        return 'C'
    return 'A' if all(gates.values()) and all(r['passed'] and r['included'] > 0 and r['unavailable'] == 0
                                             for r in comparison.values()) else 'C'


def extrema(values, allowance):
    """Finite explicitly supported scalar residuals; locations are caller-supplied."""
    available = [(float(v), loc) for v,loc in values if np.isfinite(v)]
    if not available:
        return dict(requested=len(values), included=0, excluded=0, unavailable=len(values),
                    maximum=None, location=None, allowance=allowance, passed=False, reason='no finite support')
    maximum, location = max(available, key=lambda r:abs(r[0]))
    return dict(requested=len(values), included=len(available), excluded=0,
                unavailable=len(values)-len(available), maximum=abs(maximum), signed_at_maximum=maximum,
                location=location, allowance=allowance,
                passed=len(available)==len(values) and abs(maximum)<=allowance)


def individual_details(tr, observed):
    """Locations and support for inherited booleans; no alternative acceptance rule."""
    a = observed['audits']
    values = {k:[] for k in ('conservation','aqueous_bounds','grain_bounds','phase_bounds',
                            'front_support','independent_inventory_sums')}
    for si,s in enumerate(tr.segments):
        rows = [(float(t),y,'accepted') for t,y in zip(s.t,s.y.T)]
        rows += [(float(t),y,f'event:{ci}') for ci,(ts,ys) in enumerate(s.events) for t,y in zip(ts,ys)]
        for t,y,provenance in rows:
            front,c,m = obs.state_fields(y,tr.n,tr.m)
            phase,amount = obs.inventory(t,y,tr.n,tr.weights,tr.faces)
            loc = dict(t=t,segment=si,provenance=provenance)
            grain = tr.weights@m
            liquid = np.r_[c,obs.production_trace(c,tr.faces)]
            q = int(np.argmax(np.maximum(-liquid,liquid-1)))
            values['conservation'].append((amount['normalized_residual'],loc))
            values['aqueous_bounds'].append((max(0.,-liquid[q],liquid[q]-1),dict(loc,cell=q if q<tr.n else None,trace=q==tr.n)))
            q = int(np.argmin(grain))
            values['grain_bounds'].append((max(0.,-grain[q]),dict(loc,cell=q)))
            q = int(np.argmin(phase))
            values['phase_bounds'].append((max(0.,-phase[q]),dict(loc,phase=q)))
            values['front_support'].append((max(0.,front-min(t,1.)),loc))
            values['independent_inventory_sums'].append((amount['sum_error']/amount['sum_allowance'],loc))
        values['front_support'] += [(max(0.,float(s.y[0,k]-s.y[0,k+1])),dict(t=float(s.t[k+1]),segment=si,provenance='accepted_decrease'))
                                    for k in range(len(s.t)-1)]
    budgets = dict(conservation=1e-6,aqueous_bounds=1e-8,grain_bounds=1e-8,phase_bounds=1e-8,
                   front_support=1e-10,independent_inventory_sums=1.)
    details = {key:extrema(rows,budgets[key]) for key,rows in values.items()}
    request = tr.meta['requests']
    inlet = []
    for t in request['diagnostic_times']:
        y,_=tr.evaluate(t)
        _,grain,_=obs.profiles(t,y,tr.n,tr.weights,tr.faces,np.array([0.,1.]),tr.arrival)
        exact=float(tr.weights@(obs.INITIAL*np.exp(-tr.rates*t)))
        inlet.append((grain[0]-exact,dict(t=t,z=0.)))
    details['diagnostic_inlet']=extrema(inlet,2e-5)
    public=tr.meta['public_result']
    inventory,profiles,traces=[],[],[]
    z=np.asarray(public['profile_z'])
    for i,t in enumerate(public['time']):
        y,_=tr.evaluate(t,side='left')
        phases,_=obs.inventory(t,y,tr.n,tr.weights,tr.faces)
        expected=np.array([public['inventories'][key][i] for key in ('external_liquid','fines','boulders_including_pores')])
        allowance=obs.ALGEBRA*(obs.INITIAL_MASS+np.sum(abs(phases))+np.sum(abs(expected)))
        inventory += [(float(v/allowance),dict(t=t,phase=j)) for j,v in enumerate(phases-expected)]
        cp,bp,_=obs.profiles(t,y,tr.n,tr.weights,tr.faces,z,tr.arrival,public=True)
        for name,delta in [('liquid',cp-public['liquid_profiles'][i]),('grain',bp-public['boulder_mean_profiles'][i])]:
            profiles += [(float(v),dict(t=t,z=float(z[j]),field=name)) for j,v in enumerate(delta)]
        traces += [(float(y[-1]-public['cumulative_discharged_solute'][i]),dict(t=t,field='cup')),
                   (obs.outlet(t,y,tr.n,tr.faces,tr.arrival)-public['outlet_concentration'][i],dict(t=t,z=1.,field='outlet'))]
    details['public_inventory_algebra']=extrema(inventory,1.)
    details['public_profile_reconstruction']=extrema(profiles,obs.ALGEBRA*4)
    details['public_cup_outlet_reconstruction']=extrema(traces,obs.ALGEBRA*4)
    cup_times=sorted(set([r['t'] for r in observed['accepted']]+[r[0] for r in observed['records']]+public['time']))
    coarse,fine=obs.cup_integral(tr,cup_times,4),obs.cup_integral(tr,cup_times,8)
    evolved=np.array([tr.evaluate(t)[0][-1] for t in cup_times])
    details['cup_quadrature']=extrema([(v,dict(t=t)) for t,v in zip(cup_times,coarse-fine)],1e-10)
    details['cup_state_integral']=extrema([(v,dict(t=t)) for t,v in zip(cup_times,fine-evolved)],5e-5)
    details['cup_state_integral']['separate_quadrature_maximum']=details['cup_quadrature']['maximum']
    details['cup_state_integral']['gate_sum_of_component_maxima']=a['cup_state_integral_max']+a['cup_quadrature_refinement_max']
    details['cup_state_integral']['passed']=details['cup_state_integral']['gate_sum_of_component_maxima']<=5e-5
    for field in ('liquid_profile','grain_profile','grain_history'):
        bound=a['diagnostic_bounds'][field]
        details['diagnostic_'+field+'_bounds']=dict(bound,allowance=1e-8,
            passed=bound['included']>0 and bound['unavailable']==0 and bound['minimum']>=-1e-8
            and (field!='liquid_profile' or bound['maximum']<=1+1e-8))
    spectral=a['spectrum']
    indices=np.arange(1,tr.m,dtype=float)
    resolved_weight=abs(tr.weights[:-1]-6/(np.pi*indices)**2)
    resolved_rate=abs(tr.rates[:-1]/(np.pi*indices)**2-1)
    weight_mode=tr.m-1 if spectral['weight_error']>max(resolved_weight) else int(np.argmax(resolved_weight))
    rate_mode=tr.m-1 if spectral['rate_relative_error']>max(resolved_rate) else int(np.argmax(resolved_rate))
    details['tail_weights_rates']=dict(requested=tr.m,included=tr.m,excluded=0,unavailable=0,
        maximum=max(spectral['weight_error'],spectral['rate_relative_error']),allowance=obs.ALGEBRA,
        location={'weight_mode_index':weight_mode,'rate_mode_index':rate_mode,'tail_index':tr.m-1},audit=spectral,
        passed=max(spectral['weight_error'],spectral['rate_relative_error'])<=obs.ALGEBRA)
    gates=inherited.numeric_gates(observed,tr.meta)
    counts=dict(complete_status=1,solver_segments=len(tr.segments),horizon=1,events=2,
                activation_support=len(observed['activation'])+len(observed['grain_history_activation']),
                required_times=len(observed['records'])+len(observed['unavailable_times']))
    for key,count in counts.items():
        details[key]=dict(requested=count,included=count if gates[key] else 0,excluded=0,
            unavailable=0 if gates[key] else count,maximum=0 if gates[key] else None,
            allowance=0,location=None,passed=gates[key],
            meaning='categorical completeness check; no physical maximum',
            reason=None if gates[key] else 'inherited completeness requirement failed')
    for key,passed in gates.items():
        task.require(details[key]['passed']==passed,'detailed/inherited audit disagreement: '+key)
    return details


def three_grid(trajectories,t,z,origins):
    records={name:attribution.point(tr,t,z) for name,tr in trajectories.items()}
    points={name:r[0] for name,r in records.items()}
    values={name:r['grain_mean'] for name,r in points.items()}
    d1=values['256']-values['128'];d2=values['512']-values['256']
    result=dict(t=t,z=z,origins=origins,values=values,points=points,
        sign_convention='refined minus coarse',delta_128_256=d1,delta_256_512=d2,
        monotone=bool(d1*d2>=0),reversal=bool(d1*d2<0),cancellation=bool(d1*d2<0),
        same_point_absolute_difference_reduced=bool(abs(d2)<abs(d1)),
        order_estimate='UNSUPPORTED_NOT_ESTIMATED',pair_masks={},decompositions={})
    for coarse,fine in [('128','256'),('256','512')]:
        a,fa,ma=records[coarse];b,fb,mb=records[fine]
        age=a['grain_age'] is not None and b['grain_age'] is not None and min(a['grain_age'],b['grain_age'])>=.02
        lo,hi=sorted((a['front'],b['front']))
        exited=t>=max(trajectories[coarse].arrival,trajectories[fine].arrival)
        spatial=(z<lo-.008 or z>hi+.008 or exited) and (t>=1 or abs(z-min(t,1))>.008)
        result['pair_masks'][coarse+'/'+fine]=dict(grain_profile=bool(age and spatial),grain_history=bool(age))
        entry=dict(supported=False,reason='complete common physical stencil unavailable')
        if a['point_reconstruction_supported'] and b['point_reconstruction_supported']:
            poly=diagnosis.moment_polynomial(fa,ma,z);ids=poly['indices']
            if fa[ids[0]]>=fb[0] and fa[ids[-1]+1]<=fb[-1]:
                av,pieces=zip(*(attribution.project_cell(fb,mb,fa[j],fa[j+1]) for j in ids))
                av=np.array(av);common=float(av@poly['weights']);base=float(poly['value'])
                reference=float(diagnosis.moment_polynomial(fb,mb,z)['value'])
                stored=common-base;readout=reference-common
                entry=dict(supported=True,reference='finite numerical representation, not continuum truth',
                    coarse_cells=ids,coarse_physical_faces=fa[ids[0]:ids[-1]+2],coarse_averages=ma[ids],
                    projected_averages=av,weights=poly['weights'],stored_field=stored,readout=readout,
                    closure=(reference-base)-stored-readout,
                    point_grouping_residual=(b['grain_mean']-a['grain_mean'])-(reference-base),overlap_pieces=pieces)
        result['decompositions'][coarse+'/'+fine]=entry
    # One physical 128-cell stencil for a genuinely common three-grid representation.
    normal,faces,means=records['128']
    common=dict(supported=False,reason='all three fields must cover the complete 128 physical stencil')
    if normal['point_reconstruction_supported']:
        poly=diagnosis.moment_polynomial(faces,means,z);ids=poly['indices']
        projected={'128':means[ids]};pieces={}
        for grid in ('256','512'):
            row,fine_faces,fine_means=records[grid]
            if (row['point_reconstruction_supported'] and faces[ids[0]]>=fine_faces[0]
                    and faces[ids[-1]+1]<=fine_faces[-1]):
                av,overlaps=zip(*(attribution.project_cell(fine_faces,fine_means,faces[j],faces[j+1]) for j in ids))
                projected[grid]=np.array(av);pieces[grid]=overlaps
        if len(projected)==3:
            common_values={grid:float(av@poly['weights']) for grid,av in projected.items()}
            components={}
            for coarse,fine in [('128','256'),('256','512')]:
                direct=values[fine]-values[coarse]
                stored=common_values[fine]-common_values[coarse]
                readout=(values[fine]-common_values[fine])-(values[coarse]-common_values[coarse])
                components[coarse+'/'+fine]=dict(direct=direct,stored_field=stored,readout=readout,
                                                closure=direct-stored-readout)
            common=dict(supported=True,reference='same 128 physical cells; no continuum reference',
                cells=ids,physical_faces=faces[ids[0]:ids[-1]+2],weights=poly['weights'],
                projected_averages=projected,common_values=common_values,components=components,overlap_pieces=pieces)
    result['common_three_grid']=common
    result['common_three_grid_stencil_supported']=common['supported']
    return diagnosis.array_json(result)


def same_point_panel(observed, comparisons):
    """Every pairwise maximum, evaluated as the same observable on each grid."""
    panel = []
    columns = dict(front=1,outlet=2,cup=3,liquid_inventory=4,fines_inventory=5,boulder_inventory=6)
    fields = dict(liquid_profiles='liquid_profile',grain_profiles='grain_profile',grain_histories='grain_history')
    for origin,comparison in comparisons.items():
        for quantity,metric in comparison.items():
            location=metric['location'];values={};support={}
            for grid,row in observed.items():
                try:
                    if quantity=='arrival':
                        value=row['arrival']
                    elif quantity=='activation':
                        j=row['z'].index(location['z']);value=row['activation'][j]
                    else:
                        i=[r[0] for r in row['records']].index(location['t'])
                        if quantity in columns:
                            value=row['records'][i][columns[quantity]]
                        else:
                            coords=row['grain_history_z'] if quantity=='grain_histories' else row['z']
                            j=coords.index(location['z']);value=row['observations'][i][fields[quantity]][j]
                    task.require(value is not None and np.isfinite(value),'missing finite value')
                    values[grid]=float(value);support[grid]=True
                except (ValueError,KeyError,IndexError):
                    values[grid]=None;support[grid]=False
            entry=dict(origin=origin,quantity=quantity,location=location,values=values,available=support,
                       sign_convention='refined minus coarse',common_supported=all(support.values()))
            if all(support.values()):
                d1=values['256']-values['128'];d2=values['512']-values['256']
                entry.update(delta_128_256=d1,delta_256_512=d2,monotone=d1*d2>=0,reversal=d1*d2<0,
                    cancellation=d1*d2<0,same_point_absolute_difference_reduced=abs(d2)<abs(d1))
            else:
                entry['reason']='one or more grids lacks the identical saved observation'
            entry['pair_masks']={}
            for coarse,fine in [('128','256'),('256','512')]:
                a,b=observed[coarse],observed[fine]
                included=bool(support[coarse] and support[fine])
                if included and quantity not in ('arrival','activation'):
                    t=location['t'];lo,hi=sorted((a['arrival'],b['arrival']))
                    smooth=((t<lo-.025) or (t>hi+.025)) and abs(t-1)>.025
                    if quantity=='outlet':included=bool(smooth)
                    elif quantity in fields:
                        z=location['z'];ia=[r[0] for r in a['records']].index(t);ib=[r[0] for r in b['records']].index(t)
                        front_low,front_high=sorted((a['records'][ia][1],b['records'][ib][1]))
                        spatial=(z<front_low-.008 or z>front_high+.008 or t>=hi) and (t>=1 or abs(z-min(t,1))>.008)
                        if quantity=='liquid_profiles':included=bool(spatial and (z!=1. or smooth))
                        else:
                            coords=a['grain_history_z'] if quantity=='grain_histories' else a['z']
                            field='grain_history_activation' if quantity=='grain_histories' else 'activation'
                            j=coords.index(z);aged=t-max(a[field][j],b[field][j])>=.02
                            included=bool(aged and (quantity=='grain_histories' or spatial))
                entry['pair_masks'][coarse+'/'+fine]=included
            entry['common_acceptance_eligible']=all(entry['pair_masks'].values())
            # These are diagnostics; pair acceptance remains the complete original panels.
            entry['acceptance_support']='native pair-specific panels retained separately'
            entry['order_estimate']='UNSUPPORTED_NOT_ESTIMATED'
            panel.append(entry)
    return panel


def reduce(folder,historical,plan,audit):
    folder,historical=Path(folder),Path(historical)
    output=folder/(task.ATTEMPTS[2]+'.json')
    previous=obs.read_json(task.OLD_DOCS/'ATTRIBUTION.json')
    result=dict(task=task.TASK,physical_validation='NOT_ESTABLISHED',conclusion='C',
        disposition='EXECUTED_UNQUALIFIED',resources_preliminary=audit,
        accounting_note='own pending start is retained; controller completion supplies accounting-only closure',
        historical_128_256=previous['qualification']['refinements']['bed_fine'],
        historical_individual={name:previous['qualification']['runs'][name] for name in ('normal','bed_fine')},
        comparison_256_512=inherited.unavailable_metrics('candidate reduction incomplete'),
        candidate_gates={},individual_details={},three_grid=[],integrity_reasons=[])
    task.write_new(output,result)
    trajectories={}
    try:
        metas=task.historical_inputs(historical,plan)
        observed={}
        for name in ('normal','bed_fine'):
            binding=plan['observations'][name]
            task.require(obs.sha(historical/binding['file'])==binding['sha256'],'saved observations mismatch')
            observed[name]=obs.read_json(historical/binding['file'])
            task.require(inherited.numeric_gates(observed[name],metas[name])==previous['qualification']['runs'][name]['gates'],
                         'reused historical gates differ')
        path=folder/(task.ATTEMPTS[1]+'.json')
        meta=obs.read_json(path)
        task.require(meta['task']==task.TASK and meta['row']==task.ROW and meta['attempt']==task.ATTEMPTS[1],
                     'candidate execution identity mismatch')
        reasons=inherited.check_run(meta,task.CANDIDATE,obs.sha(task.DOCS/'PLAN.json'))
        task.require(not reasons,'; '.join(reasons))
        for segment in meta['segments']:
            task.require(obs.sha(folder/segment['receipt_file'])==segment['receipt_sha256'],'candidate receipt mismatch')
        public=meta['public_checkpoint']
        task.require(obs.sha(folder/public['file'])==public['sha256'] and obs.read_json(folder/public['file'])==meta['public_result'],
                     'candidate public checkpoint mismatch')
        saved=path.with_name(path.stem+'-observations.json')
        task.require(obs.sha(saved)==audit['ends'][task.ATTEMPTS[1]]['observations_sha256'],'candidate observation mismatch')
        observed['512']=obs.read_json(saved)
        result['candidate_gates']=inherited.numeric_gates(observed['512'],meta)
        result['candidate_audits']=observed['512']['audits']
        result['comparison_256_512']=inherited.refinement(observed['bed_fine'],observed['512'])
        result['comparison_sign_convention']='coarse minus refined, inherited acceptance semantics'
        result['same_point_observables']=same_point_panel(
            {'128':observed['normal'],'256':observed['bed_fine'],'512':observed['512']},
            {'historical_128_256':result['historical_128_256'],'new_256_512':result['comparison_256_512']})
        task.checkpoint(output,result)
        for name,key in [('normal','128'),('bed_fine','256')]:
            trajectories[key]=obs.Trajectory(historical/plan['captures'][name]['metadata_file'])
        trajectories['512']=obs.Trajectory(path)
        result['individual_details']=individual_details(trajectories['512'],observed['512'])
        points={(p['t'],p['z']):[p['name']] for p in obs.read_json(task.OLD_DOCS/'ATTRIBUTION_PLAN.json')['attribution']['points']}
        for label,comparison in [('historical_128_256',result['historical_128_256']),('new_256_512',result['comparison_256_512'])]:
            for name,row in comparison.items():
                loc=row.get('location') or {}
                if 't' in loc and 'z' in loc:
                    points.setdefault((loc['t'],loc['z']),[]).append(label+':'+name)
                elif 't' in loc and name=='outlet':
                    points.setdefault((loc['t'],1.),[]).append(label+':outlet')
        for (t,z),origins in sorted(points.items()):
            result['three_grid'].append(three_grid(trajectories,t,z,origins))
            task.checkpoint(output,result)
        result['conclusion']=disposition(True,True,result['candidate_gates'],result['comparison_256_512'])
        result['disposition']={'A':'FINER_RESOLUTION_PROMISING_FOR_SEPARATELY_AUTHORIZED_QUALIFICATION',
                               'C':'NEW_SPATIAL_COMPARISON_INADEQUATE_MIXED_OR_INCONCLUSIVE'}[result['conclusion']]
    except Exception as exc:
        result['integrity_reasons'].append(type(exc).__name__+': '+str(exc))
        result['conclusion']='D' if isinstance(exc,MemoryError) else 'C'
        result['disposition']='FIXED_RESOURCE_MEMORY_EXHAUSTED' if isinstance(exc,MemoryError) else 'EXECUTION_OR_OBSERVATION_INCOMPLETE'
    finally:
        for tr in trajectories.values():tr.close()
        task.checkpoint(output,result)
    return result
