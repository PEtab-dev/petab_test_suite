from inspect import cleandoc

from petab.v1.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabTestCase, analytical_a
from petab.v2 import Problem
from petab.v2.C import *

DESCRIPTION = cleandoc("""
## Objective

This case tests support for time-point specific overrides in the measurement
table.

The model is to be simulated for a single experimental condition. The single
model output is scaled by a different parameter at each timepoint.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_observable(
    "obs_a", "observableParameter1_obs_a * A", noise_formula=1
)

problem.add_measurement(
    "obs_a", "", time=0, measurement=0.7, observable_parameters=(10,)
)
problem.add_measurement(
    "obs_a", "", time=10, measurement=0.1, observable_parameters=(15,)
)

problem.add_parameter(
    "a0", lb=0, ub=10, nominal_value=1, scale=LIN, estimate=True
)
problem.add_parameter(
    "b0", lb=0, ub=10, nominal_value=0, scale=LIN, estimate=True
)
problem.add_parameter(
    "k1", lb=0, ub=10, nominal_value=0.8, scale=LIN, estimate=True
)
problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, scale=LIN, estimate=True
)
# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    10 * analytical_a(0, 1, 0, 0.8, 0.6),
    15 * analytical_a(10, 1, 0, 0.8, 0.6),
]

case = PetabTestCase(
    id=6,
    brief="Simulation. Time-point specific numeric observable parameter "
    "overrides.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
