from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import DEFAULT_SBML_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for multiple simulation conditions

The model is to be simulated for two different experimental conditions
(here: different initial concentrations).

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0', 'c1'],
    'a0': [0.8, 0.9]
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'] * 4,
    SIMULATION_CONDITION_ID: ['c0', 'c0', 'c1', 'c1'],
    TIME: [0, 10, 0, 10],
    MEASUREMENT: [0.7, 0.1, 0.8, 0.2]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['A'],
    NOISE_FORMULA: [1]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['b0', 'k1', 'k2'],
    PARAMETER_SCALE: [LIN] * 3,
    LOWER_BOUND: [0] * 3,
    UPPER_BOUND: [10] * 3,
    NOMINAL_VALUE: [0, 0.8, 0.6],
    ESTIMATE: [1] * 3,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [*[analytical_a(t, 0.8, 0, 0.8, 0.6)
                               for t in [0, 10]],
                             *[analytical_a(t, 0.9, 0, 0.8, 0.6)
                               for t in [0, 10]]]

case = PetabTestCase(
    id=2,
    brief="Simulation. Two conditions. Numeric parameter override.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
