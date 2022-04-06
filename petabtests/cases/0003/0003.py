from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import DEFAULT_SBML_FILE, PetabTestCase, analytical_a


DESCRIPTION = cleandoc("""
## Objective 

This case tests support for numeric observable parameter overrides in
measurement tables

Simulated data describes measurements with different offset and scaling
parameters for a single observable. These respective numeric
`observableParameters`
from the measurement table have to be applied to the placeholders in
observableFormula.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0'],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [0, 10],
    MEASUREMENT: [0.7, 0.1],
    OBSERVABLE_PARAMETERS: ['0.5;2', '0.5;2']
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['observableParameter1_obs_a * A + '
                         'observableParameter2_obs_a'],
    NOISE_FORMULA: [0.5]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['a0', 'b0', 'k1', 'k2'],
    PARAMETER_SCALE: [LIN] * 4,
    LOWER_BOUND: [0] * 4,
    UPPER_BOUND: [10] * 4,
    NOMINAL_VALUE: [1, 0, 0.8, 0.6],
    ESTIMATE: [1] * 4,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [0.5 * analytical_a(t, 1, 0, 0.8, 0.6) + 2
                             for t in simulation_df[TIME]]


case = PetabTestCase(
    id=3,
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df = parameter_df,
)
