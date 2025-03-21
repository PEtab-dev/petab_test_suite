from inspect import cleandoc

import pandas as pd
from petab.v1.C import *

from petabtests import PetabV1TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests parametric initial concentrations in the condition table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(
    data={
        CONDITION_ID: ["c0"],
        "B": ["par"],
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
        PARAMETER_ID: ["k1", "k2", "par"],
        PARAMETER_SCALE: [LIN] * 3,
        LOWER_BOUND: [0] * 3,
        UPPER_BOUND: [10] * 3,
        NOMINAL_VALUE: [0.8, 0.6, 7],
        ESTIMATE: [1] * 3,
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 7, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV1TestCase(
    id=13,
    brief="Simulation. Species with InitialAssignment overridden by "
    "parameter.",
    description=DESCRIPTION,
    model="conversion_modified.xml",
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
