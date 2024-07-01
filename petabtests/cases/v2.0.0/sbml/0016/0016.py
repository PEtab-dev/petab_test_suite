from inspect import cleandoc

import pandas as pd
from petab.v2.C import *

from petabtests import (
    DEFAULT_SBML_FILE,
    PetabTestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for observable transformations to log scale.

The model is to be simulated for a single experimental condition. Measurements
for observable `obs_a` are to be used as is, measurements for `obs_b` are to
be transformed to log scale for computing chi2 and likelihood.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")
# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(
    data={
        CONDITION_ID: ["c0"],
    }
).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b"],
        SIMULATION_CONDITION_ID: ["c0", "c0"],
        TIME: [10, 10],
        MEASUREMENT: [0.2, 0.8],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b"],
        OBSERVABLE_FORMULA: ["A", "B"],
        OBSERVABLE_TRANSFORMATION: [LIN, LOG],
        NOISE_FORMULA: [0.5, 0.7],
    }
).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(
    data={
        PARAMETER_ID: ["a0", "b0", "k1", "k2"],
        PARAMETER_SCALE: [LIN] * 4,
        LOWER_BOUND: [0] * 4,
        UPPER_BOUND: [10] * 4,
        NOMINAL_VALUE: [1, 0, 0.8, 0.6],
        ESTIMATE: [1] * 4,
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(10, 1, 0, 0.8, 0.6),
    analytical_b(10, 1, 0, 0.8, 0.6),
]

case = PetabTestCase(
    id=16,
    brief="Simulation. Observable transformation log.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
