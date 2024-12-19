from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import (
    DEFAULT_PYSB_FILE,
    PetabTestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for observable transformations to log scale.

The model is to be simulated for a single experimental condition. Measurements
for observable `obs_a` are to be used as is, measurements for `obs_b` are to
be transformed to log scale for computing chi2 and likelihood.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")
# problem --------------------------------------------------------------------
problem = Problem()
problem.add_observable("obs_a", "A", noise_formula=0.5, transform=LIN)
problem.add_observable("obs_b", "B", noise_formula=0.7, transform=LOG)
problem.add_measurement("obs_a", "", time=10, measurement=0.2)
problem.add_measurement("obs_b", "", time=10, measurement=0.8)
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
    analytical_a(10, 1, 0, 0.8, 0.6),
    analytical_b(10, 1, 0, 0.8, 0.6),
]

case = PetabTestCase(
    id=16,
    brief="Simulation. Observable transformation log.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
