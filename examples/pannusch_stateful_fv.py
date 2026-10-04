"""Offline N4 API illustration (five small integrations; not qualification).

Pannusch et al., 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0 source-derived
output, separately from first-party code licensing.
"""
import numpy as np

from puckworks.models.pannusch2024.flow_temperature_history_fv import (
    simulate_flow_temperature_history_fv,
)
from puckworks.models.pannusch2024.stateful_fv import (
    FVChemicalState, FVPlan, FVSettings, FlowHistory, TemperatureHistory,
    branch_stateful_fv, simulate_stateful_fv,
)


def describe(label, result):
    p = result.primary
    print(f"{label}: {result.mode}, {result.status}")
    print(f"  clocks [s]: root={result.root_time_s:g}, local start={result.continuation_start_s:g}, current={result.actual_end_s:g}")
    print(f"  remaining bed inventory [kg]: {p.remaining_inventory_kg[-1]:.12g}")
    print(f"  outlet solute [kg]: local={p.segment_outlet_solute_kg[-1]:.12g}, origin={p.origin_outlet_solute_kg[-1]:.12g}")
    print(f"  collected volume [m^3]: local={p.segment_volume_m3[-1]:.12g}, origin={p.origin_volume_m3[-1]:.12g}")


def main():
    print("G2 / NUMERICAL_METHOD_CHANGE; RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED")
    print("Runtime accuracy NOT_ASSESSED. Synthetic states; no measured wetting-state claim.")
    settings = FVSettings(cells=4)
    T = TemperatureHistory.constant_celsius([0,.03,.11],[80,98])
    Q = FlowHistory([0,.05,.11],[1e-6,2.7e-6],'constant')
    plan = FVPlan(T,Q,(0,.11),settings)
    equilibrium = FVChemicalState.source_equilibrium(T,time_s=0,solute='caffeine',cells=4)
    explicit = simulate_stateful_fv(plan=plan,initial_state=equilibrium,observation_times_s=[0,.11])
    implicit = simulate_flow_temperature_history_fv(T,flow_history=Q,t_span_s=(0,.11),
        solute='caffeine',observation_times_s=[0,.11],fraction_bounds_s=[0,.11],settings=settings)
    error = np.max(abs(explicit.observations.liquid_cell_average_kg_m3-implicit.observations.liquid_cell_average_kg_m3))
    print(f"Equilibrium compatibility, maximum liquid difference [kg/m^3]: {error:.9g}")
    describe('Explicit equilibrium',explicit)

    x = equilibrium.edges_m/equilibrium.edges_m[-1]
    left,right = x[:-1],x[1:]
    C0 = equilibrium.fine_cell_average_kg_m3[0]
    state = FVChemicalState.from_cell_averages(solute='caffeine',time_s=0,
        edges_m=equilibrium.edges_m,
        liquid_kg_m3=C0*(.15+.25*(left+right)/2),
        fine_kg_m3=C0*(.85-.55*(left+right)/2),
        coarse_kg_m3=C0*(.10+.45*(left*left+left*right+right*right)/3))
    tc = float(plan.primary_times_s[2])
    prefix = simulate_stateful_fv(plan=plan,initial_state=state,stop_time_s=tc,
                                  observation_times_s=[0,tc],fraction_windows_s=[(0,tc)])
    checkpoint = prefix.checkpoint(tc)
    resumed = simulate_stateful_fv(checkpoint=checkpoint,observation_times_s=[tc,.11],
                                   fraction_windows_s=[(tc,.11)])
    future = FVPlan(TemperatureHistory.constant_celsius([tc,.11],[93]),
                    FlowHistory([tc,.11],[2.2e-6],'constant'),(tc,.11),settings)
    branch = branch_stateful_fv(checkpoint,plan=future,observation_times_s=[tc,.11],
                                fraction_windows_s=[(tc,.11)])
    for label,result in [('Nonequilibrium planned prefix',prefix),('Original schedule resume',resumed),('New future branch',branch)]:
        describe(label,result)
    print('Concentrations are cell averages [kg/m^3] on separate liquid/fine/coarse source bases.')
    print('Same immutable checkpoint reused; a forcing jump changes coefficients, preserving chemical state.')


if __name__ == '__main__':
    main()
