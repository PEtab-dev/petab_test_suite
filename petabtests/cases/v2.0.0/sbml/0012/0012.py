from inspect import cleandoc

import pandas as pd
from petab.v1.C import *
from petab.v2.C import *

from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests initial compartment sizes in the condition table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(
    data={
        CONDITION_ID: ["c0"],
        TARGET_ID: ["compartment"],
        TARGET_VALUE: [3],
    }
)

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
        PARAMETER_ID: ["k1", "k2"],
        PARAMETER_SCALE: [LIN] * 2,
        LOWER_BOUND: [0] * 2,
        UPPER_BOUND: [10] * 2,
        NOMINAL_VALUE: [0.8, 0.6],
        ESTIMATE: [1] * 2,
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 1, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=12,
    brief="Simulation. Initial compartment size in condition table.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
