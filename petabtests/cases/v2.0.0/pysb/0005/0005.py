from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for parametric overrides from condition table.

The model is to be simulated for two different experimental conditions
(here: different initial concentrations). The observable is offsetted by
a parametric override in the condition table (i.e. the actual value has
to be taken from the parameter table).

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0', 'c1'],
    'offset_A': ['offset_A_c0', 'offset_A_c1'],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c1'],
    TIME: [10, 10],
    MEASUREMENT: [2.1, 3.2]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['A + offset_A'],
    NOISE_FORMULA: [1]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['a0', 'b0', 'k1', 'k2', 'offset_A_c0', 'offset_A_c1'],
    PARAMETER_SCALE: [LIN] * 6,
    LOWER_BOUND: [0] * 6,
    UPPER_BOUND: [10] * 6,
    NOMINAL_VALUE: [1, 0, 0.8, 0.6, 2, 3],
    ESTIMATE: [1] * 6,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [analytical_a(10, 1, 0, 0.8, 0.6) + offset
                             for offset in [2, 3]]

case = PetabTestCase(
    id=5,
    brief="Simulation. Condition-specific parameters only defined in "
          "parameter table.",
    description=DESCRIPTION,
    model='conversion_modified_pysb.py',
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
