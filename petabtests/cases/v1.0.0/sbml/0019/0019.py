from inspect import cleandoc

import pandas as pd
from petab.v1.C import *

from petabtests import PetabV1TestCase, analytical_a, antimony_to_sbml_str
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests handling of initial concentrations that are specified
in the conditions table. For species `A`, the initial concentration is
estimated. For species `B`, the initial concentration is specified in the
parameters table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
ant_model = """
model *petab_test_0019()
  compartment compartment_ = 1;
  species A in compartment_, B in compartment_;

  fwd: A => B; compartment_ * k1 * A;
  rev: B => A; compartment_ * k2 * B;

  A = a0;
  B = 1;
  a0 = 1;
  k1 = 0;
  k2 = 0;
end
"""
model_file = Path(__file__).parent / "_model.xml"
model_file.write_text(antimony_to_sbml_str(ant_model))

condition_df = pd.DataFrame(
    data={
        CONDITION_ID: ["c0"],
        "A": ["initial_A"],
        "B": ["initial_B"],
    }
).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_a"],
        SIMULATION_CONDITION_ID: ["c0", "c0"],
        TIME: [0, 10],
        MEASUREMENT: [0.7, 0.1],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a"],
        OBSERVABLE_FORMULA: ["A"],
        NOISE_FORMULA: [0.5],
    }
).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(
    data={
        PARAMETER_ID: ["k1", "k2", "initial_A", "initial_B"],
        PARAMETER_SCALE: [LIN, LIN, LOG10, LIN],
        LOWER_BOUND: [0, 0, 1, 0],
        UPPER_BOUND: [10] * 4,
        NOMINAL_VALUE: [0.8, 0.6, 2, 3],
        ESTIMATE: [1] * 3 + [0],
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 2, 3, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV1TestCase(
    id=19,
    brief="Simulation. Estimated initial value via conditions table.",
    description=DESCRIPTION,
    model=model_file,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
