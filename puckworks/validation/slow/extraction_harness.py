"""P1 extraction-harness full report — NOT run in CI (re-runs the pannusch PDE).

The quick gate (gate_extraction_harness) checks the c_sat surfacing, the §5.6
discriminator, and the grudeva total. This ladder prints the full
extraction-vs-dataset comparison (including the pannusch fit MAPEs, ~13 s) plus
the P1 normalization-hazard table — the numbers for the CHAT workup (item 2.3).

Run:  python -m puckworks.validation.slow.extraction_harness
"""
from puckworks import harness as h


def report():
    print("== P1 normalization hazards (never silently merged) ==")
    for model, hz in h.P1_HAZARDS.items():
        print(f"  {model:16} c_sat={str(hz['c_sat_kg_m3']):>6}  "
              f"inv={hz['inventory']}")
    print(f"  distinct c_sat values: {h.csat_values()}")

    print("\n== extraction vs dataset (validation-strength tagged) ==")
    for key, r in h.extraction_comparison().items():
        print(f"  {key}:")
        for k, v in r.items():
            print(f"      {k}: {v}")

    print("\n== §5.6 dissolution-speed discriminator ==")
    for k, v in h.dissolution_speed_test().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    report()
