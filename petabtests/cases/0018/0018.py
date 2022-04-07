from inspect import cleandoc

import pandas as pd
from petab.C import *
from pathlib import Path
from petabtests import PetabTestCase, analytical_a, analytical_b

DESCRIPTION = cleandoc("""
## Objective

This case tests support for RateRules and partial preequilibration with `NaN`'s
in the condition file.

The model is to be simulated for a preequilibration condition and a
simulation condition.
For preequilibration, species `B` is initialized with `0`. For simulation,
`B` is set to `NaN`, meaning that it is initialized with the result from
preequilibration.
`A` is reinitialized to the value in the condition table after
preequilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics. Dynamics of are specified as `RateRule`s targeting a
parameter and a species.
""")

# problem --------------------------------------------------------------------

model = str(Path(__file__).parent / "model.xml")


def get_model():
    import simplesbml
    model = simplesbml.SbmlModel()
    model.addParameter("a0", 1)
    model.addParameter("b0", 1)
    model.addParameter("k1", 0)
    model.addParameter("k2", 0)
    model.addCompartment(comp_id="compartment")
    model.addSpecies("[A]", 0, comp="compartment")
    model.addParameter("B", 0)
    model.addInitialAssignment("A", "a0")
    model.addInitialAssignment("B", "b0")
    model.addRateRule("A", "k2 * B - k1 * A")
    model.addRateRule("B", "- compartment * k2 * B + compartment * k1 * A")
    return model


with open(model, "w") as f:
    f.write(get_model().toSBML())


condition_df = pd.DataFrame(data={
    CONDITION_ID: ['preeq_c0', 'c0'],
    'k1': [0.3, 0.8],
    'B': [2.0, 'NaN'],
    'A': [0, 1],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'] * 3 + ['obs_b'],
    PREEQUILIBRATION_CONDITION_ID: ['preeq_c0'] * 4,
    SIMULATION_CONDITION_ID: ['c0'] * 4,
    TIME: [0, 1, 10, 0],
    MEASUREMENT: [0.1, 0.7, 0.1, 0.1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_b'],
    OBSERVABLE_FORMULA: ['A', 'B'],
    NOISE_FORMULA: [0.5, 0.2]
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
simulation_df.iloc[:3, simulation_df.columns.get_loc(SIMULATION)] = [
    analytical_a(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME]][:3]
simulation_df.iloc[3:, simulation_df.columns.get_loc(SIMULATION)] = [
    analytical_b(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME]][3:]


case = PetabTestCase(
    id=18,
    brief="Simulation. Preequilibration and RateRules. One state "
          "reinitialized, one not (NaN in condition table). InitialAssignment "
          "to species overridden.",
    description=DESCRIPTION,
    model=model,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
