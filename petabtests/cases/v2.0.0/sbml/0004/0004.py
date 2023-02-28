from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import DEFAULT_SBML_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for parametric observable parameter overrides in
measurement tables

Simulated data describes measurements with different offset and scaling
parameters for a single observable. These values of the respective
(non-estimated) parameters referenced in `observableParameters` need to be
looked up in the parameter table to replace the placeholders in
`observableFormula`.

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
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['scaling_A * A + offset_A'],
    NOISE_FORMULA: [1]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['a0', 'b0', 'k1', 'k2', 'scaling_A', 'offset_A'],
    PARAMETER_SCALE: [LIN] * 6,
    LOWER_BOUND: [0] * 6,
    UPPER_BOUND: [10] * 6,
    NOMINAL_VALUE: [1, 0, 0.8, 0.6, 0.5, 2],
    ESTIMATE: [1] * 6,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [0.5 * analytical_a(t, 1, 0, 0.8, 0.6) + 2
                             for t in simulation_df[TIME]]

case = PetabTestCase(
    id=4,
    brief="Simulation. Observable parameters only defined in parameter table.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
