from inspect import cleandoc

import pandas as pd
from petab.v2.C import *

from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests a single numeric noise parameter override in the measurement
table, with a noise formula that is not just the noise parameter placeholder.
The numeric override must be substituted into the noise formula, not used as
standard deviation directly.
The noise formula depends on the observable value, so it has to be evaluated
for each timepoint.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_a"],
        EXPERIMENT_ID: ["", ""],
        TIME: [0, 10],
        MEASUREMENT: [0.7, 0.1],
        NOISE_PARAMETERS: [0.5, 0.5],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a"],
        OBSERVABLE_FORMULA: ["A"],
        NOISE_FORMULA: ["noiseParameter1_obs_a * (obs_a + 1)"],
        NOISE_PLACEHOLDERS: ["noiseParameter1_obs_a"],
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
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=33,
    brief="Simulation. Single numeric noise parameter override in "
    "non-trivial noise formula.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
