from inspect import cleandoc

import pandas as pd
from petab.C import *

from petabtests import DEFAULT_SBML_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

Test different model entities inside the mapping table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
# TODO use mapping here
condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0'],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [0, 10],
    MEASUREMENT: [0.7, 0.1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['maps_to_A'],
    NOISE_FORMULA: [0.5]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['a0', 'maps_to_b0', 'k1', 'maps_to_k2'],
    PARAMETER_SCALE: [LIN] * 4,
    LOWER_BOUND: [0] * 4,
    UPPER_BOUND: [10] * 4,
    NOMINAL_VALUE: [1, 0, 0.8, 0.6],
    ESTIMATE: [1] * 4,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [analytical_a(t, 1, 0, 0.8, 0.6)
                             for t in simulation_df[TIME]]

mapping_df = pd.DataFrame(data={
    PETAB_ENTITY_ID:
        ['maps_to_a0', 'maps_to_b0', 'maps_to_k1',
         'maps_to_k2', 'maps_to_A', 'maps_to_B'],
    MODEL_ENTITY_ID:
        ['a0', 'b0', 'k1', 'k2', 'A', 'B'],
}).set_index(PETAB_ENTITY_ID)

case = PetabTestCase(
    id=19,
    brief="Mapping table.",
    description=DESCRIPTION,
    # TODO add local parameter and use in mapping table
    model=DEFAULT_SBML_FILE,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
    mapping_df=mapping_df,
)
