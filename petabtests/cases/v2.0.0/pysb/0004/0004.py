from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

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
problem = Problem()

problem.add_observable(
    "obs_a",
    "scaling_A * A + offset_A",
    noise_formula=1,
)

problem.add_measurement(
    "obs_a",
    time=0,
    measurement=0.7,
)
problem.add_measurement(
    "obs_a",
    time=10,
    measurement=0.1,
)

problem.add_parameter(
    "scaling_A",
    lb=0,
    ub=10,
    nominal_value=0.5,
    estimate=False,
)
problem.add_parameter(
    "offset_A",
    lb=0,
    ub=10,
    nominal_value=2,
    estimate=False,
)
problem.add_parameter(
    "a0",
    lb=0,
    ub=10,
    nominal_value=1,
    estimate=True,
)
problem.add_parameter(
    "b0",
    lb=0,
    ub=10,
    nominal_value=0,
    estimate=True,
)
problem.add_parameter(
    "k1",
    lb=0,
    ub=10,
    nominal_value=0.8,
    estimate=True,
)
problem.add_parameter(
    "k2",
    lb=0,
    ub=10,
    nominal_value=0.6,
    estimate=True,
)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    0.5 * analytical_a(t, 1, 0, 0.8, 0.6) + 2 for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=4,
    brief="Simulation. Observable parameters only defined in parameter table.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
