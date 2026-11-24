from inspect import cleandoc

import pandas as pd
from petab.v1.C import *

from petabtests import (
    DEFAULT_SBML_FILE,
    PetabV1TestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for time-point specific overrides in the measurement
table.

The model is to be simulated for a single experimental condition. The
noise parameters differ between timepoints for both model outputs:

* `obs_a` is scaled by a different numeric value at each timepoint. Its
  noise formula is not just the noise parameter placeholder, so the numeric
  override must be substituted into the noise formula, not used as standard
  deviation directly.
* `obs_b` has a noise formula that consists only of the noise parameter
  placeholder, so the numeric override is the standard deviation.

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
        OBSERVABLE_ID: ["obs_a", "obs_a", "obs_b", "obs_b"],
        SIMULATION_CONDITION_ID: ["c0"] * 4,
        TIME: [0, 10, 0, 10],
        MEASUREMENT: [0.7, 0.1, 0.2, 1.0],
        OBSERVABLE_PARAMETERS: [10, 15, "", ""],
        NOISE_PARAMETERS: [0.5, 2, 0.3, 1.5],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b"],
        OBSERVABLE_FORMULA: ["observableParameter1_obs_a * A", "B"],
        NOISE_FORMULA: ["2 * noiseParameter1_obs_a", "noiseParameter1_obs_b"],
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
    10 * analytical_a(0, 1, 0, 0.8, 0.6),
    15 * analytical_a(10, 1, 0, 0.8, 0.6),
    analytical_b(0, 1, 0, 0.8, 0.6),
    analytical_b(10, 1, 0, 0.8, 0.6),
]

case = PetabV1TestCase(
    id=6,
    brief="Simulation. Time-point specific numeric observable and noise "
    "parameter overrides, with and without scaling in the noise formula.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
