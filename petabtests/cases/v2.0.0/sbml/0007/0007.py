from inspect import cleandoc

import pandas as pd
from petab.v2.C import *

from petabtests import (
    DEFAULT_SBML_FILE,
    PetabV2TestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests log-normal noise.

The model is to be simulated for a single experimental condition.
Observables `obs_a` and `obs_b` are the same except for the noise distribution.
The noise distributions need to be accounted for when computing chi2 and
likelihood.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b"],
        EXPERIMENT_ID: ["", ""],
        TIME: [10, 10],
        MEASUREMENT: [0.2, 0.8],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b"],
        OBSERVABLE_FORMULA: ["A", "B"],
        NOISE_DISTRIBUTION: [NORMAL, LOG_NORMAL],
        NOISE_FORMULA: [0.5, 0.6],
    }
).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(
    data={
        PARAMETER_ID: ["a0", "b0", "k1", "k2"],
        LOWER_BOUND: [0] * 4,
        UPPER_BOUND: [10] * 4,
        NOMINAL_VALUE: [1, 0, 0.8, 0.6],
        ESTIMATE: ["true"] * 4,
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

case = PetabV2TestCase(
    id=7,
    brief="Simulation. Log-normal noise.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
