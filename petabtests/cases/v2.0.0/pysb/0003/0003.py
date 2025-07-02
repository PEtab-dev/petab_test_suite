from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

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
problem = Problem()

problem.add_observable(
    "obs_a",
    "obs_a_scale * A + obs_a_offset",
    noise_formula=0.5,
    observable_placeholders=["obs_a_scale", "obs_a_offset"],
)

problem.add_measurement(
    "obs_a", "", time=0, measurement=0.7, observable_parameters=(0.5, 2)
)
problem.add_measurement(
    "obs_a", "", time=10, measurement=0.1, observable_parameters=(0.5, 2)
)

problem.add_parameter("a0", lb=0, ub=10, nominal_value=1)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0)
problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    0.5 * analytical_a(t, 1, 0, 0.8, 0.6) + 2 for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=3,
    brief="Simulation. Numeric observable parameter overrides in measurement "
    "table.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
