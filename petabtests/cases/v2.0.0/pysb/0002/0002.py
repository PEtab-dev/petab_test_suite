from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for multiple simulation conditions

The model is to be simulated for two different experimental conditions
(here: different initial concentrations).

For `b0`, `nan` is used in the condition table, indicating that the default
model values for `b0` should be used for either condition.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("c0", a0=(VT_INITIAL, 0.8))
problem.add_condition("c1", a0=(VT_INITIAL, 0.9))

problem.add_experiment("e0", 0, "c0")
problem.add_experiment("e1", 0, "c1")

problem.add_observable("obs_a", "A", noise_formula=1)

problem.add_measurement("obs_a", "e0", time=0, measurement=0.7)
problem.add_measurement("obs_a", "e0", time=10, measurement=0.1)
problem.add_measurement("obs_a", "e1", time=0, measurement=0.8)
problem.add_measurement("obs_a", "e1", time=10, measurement=0.2)

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
    *[analytical_a(t, 0.8, 1, 0.8, 0.6) for t in [0, 10]],
    *[analytical_a(t, 0.9, 1, 0.8, 0.6) for t in [0, 10]],
]
case = PetabTestCase(
    id=2,
    brief="Simulation. Two conditions. Numeric parameter override.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    experiment_dfs=[problem.experiment_df],
    parameter_df=problem.parameter_df,
)
