from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

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

problem = Problem()

problem.add_condition("c0", offset_A=(VT_CONSTANT, "offset_A_c0"))
problem.add_condition("c1", offset_A=(VT_CONSTANT, "offset_A_c1"))

problem.add_experiment("e0", 0, "c0")
problem.add_experiment("e1", 0, "c1")

problem.add_observable(
    "obs_a",
    "A + offset_A",
    noise_formula=1,
)

problem.add_measurement(
    "obs_a",
    "e0",
    time=10,
    measurement=2.1,
)
problem.add_measurement(
    "obs_a",
    "e1",
    time=10,
    measurement=3.2,
)

problem.add_parameter(
    "a0",
    lb=0,
    ub=10,
    nominal_value=1,
    scale=LIN,
    estimate=True,
)
problem.add_parameter(
    "b0",
    lb=0,
    ub=10,
    nominal_value=0,
    scale=LIN,
    estimate=True,
)
problem.add_parameter(
    "k1",
    lb=0,
    ub=10,
    nominal_value=0.8,
    scale=LIN,
    estimate=True,
)
problem.add_parameter(
    "k2",
    lb=0,
    ub=10,
    nominal_value=0.6,
    scale=LIN,
    estimate=True,
)
problem.add_parameter(
    "offset_A_c0",
    lb=0,
    ub=10,
    nominal_value=2,
    scale=LIN,
    estimate=False,
)
problem.add_parameter(
    "offset_A_c1",
    lb=0,
    ub=10,
    nominal_value=3,
    scale=LIN,
    estimate=False,
)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(10, 1, 0, 0.8, 0.6) + offset for offset in [2, 3]
]

case = PetabTestCase(
    id=5,
    brief="Simulation. Condition-specific parameters only defined in "
    "parameter table.",
    description=DESCRIPTION,
    model="conversion_modified_pysb.py",
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    experiment_dfs=[problem.experiment_df],
)
