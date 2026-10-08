"""Small offline old/new finite-fraction example, N4, synthetic prescribed Q/T.

RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED; accuracy NOT_ASSESSED.
Source-derived output: Pannusch et al., 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
Run from the repository root: python -m examples.pannusch_flow_consistent_observer
"""
import json

from puckworks.models.pannusch2024 import stateful_fv as sf
from puckworks.models.pannusch2024.flow_consistent_observer import observe_flow_consistent_fv


def main():
    temperature=sf.TemperatureHistory.linear_celsius((0,.1),(80,95))
    plan=sf.FVPlan(temperature,sf.FlowHistory((0,.1),(1.2e-6,2.8e-6),'linear'),
                   (0,.1),sf.FVSettings(cells=4))
    state=sf.FVChemicalState.source_equilibrium(temperature,time_s=0,solute='caffeine',cells=4)
    windows=((.077,.079),)
    old=sf.simulate_stateful_fv(plan=plan,initial_state=state,observation_times_s=(0,.078,.1),
                               fraction_windows_s=windows)
    new=observe_flow_consistent_fv(old,observation_times_s=(0,.078,.1),fraction_windows_s=windows)
    print(json.dumps(dict(method=new.method,window_s=windows[0],
        old_fraction_kg_m3=old.fractions[0].concentration_kg_m3,
        new_fraction_kg_m3=new.fractions[0].concentration_kg_m3,
        actual_volume_m3=new.fractions[0].volume_m3,
        original_primary_result_sha256=old.identity_sha256,
        request_support=new.request_support,accuracy='NOT_ASSESSED',PHYSICAL_VALIDATION='NOT_ESTABLISHED'),
        indent=2,allow_nan=False))


if __name__=='__main__':main()
