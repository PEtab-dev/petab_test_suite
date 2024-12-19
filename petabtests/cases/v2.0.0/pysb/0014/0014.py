from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests numeric noise parameter overrides in the measurement table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()
problem.add_observable(
    "obs_a", "A", noise_formula="noiseParameter1_obs_a + noiseParameter2_obs_a"
)
problem.add_measurement(
    "obs_a", "", time=0, measurement=0.7, noise_parameters=(0.5, 2)
)
problem.add_measurement(
    "obs_a", "", time=10, measurement=0.1, noise_parameters=(0.5, 2)
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
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabTestCase(
    id=14,
    brief="Simulation. Multiple numeric noise parameter overrides.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
