from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import (DEFAULT_SBML_FILE, PetabTestCase, analytical_a,
                        analytical_b)

DESCRIPTION = cleandoc("""
## Objective 

This case tests support for partial preequilibration with `NaN`'s in the 
condition file.

The model is to be simulated for a preequilibration condition and a
simulation condition.
For preequilibration, species `B` is initialized with `0`. For simulation,
`B` is set to `NaN`, meaning that it is initialized with the result from
preequilibration.
`A` is reinitialized to the value in the condition table after 
preequilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------


condition_df = pd.DataFrame(data={
    CONDITION_ID: ['preeq_c0', 'c0'],
    'k1': [0.3, 0.8],
    'B': [2.0, 'NaN'],
    'A': [0, 1],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    PREEQUILIBRATION_CONDITION_ID: ['preeq_c0', 'preeq_c0'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [1, 10],
    MEASUREMENT: [0.7, 0.1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['A'],
    NOISE_FORMULA: [0.5]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['k2'],
    PARAMETER_SCALE: [LIN],
    LOWER_BOUND: [0],
    UPPER_BOUND: [10],
    NOMINAL_VALUE: [0.6],
    ESTIMATE: [1],
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
# simulate for far time point as steady state
steady_state_b = analytical_b(1000, 0, 2.0, 0.3, 0.6)
# use steady state as initial state
simulation_df[SIMULATION] = [
    analytical_a(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME]]

case = PetabTestCase(
    id=17,
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
