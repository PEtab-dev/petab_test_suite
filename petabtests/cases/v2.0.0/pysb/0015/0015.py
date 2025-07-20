from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests parametric noise parameter overrides in the measurement table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()
problem.add_observable(
    "obs_a",
    "A",
    noise_formula="noiseParameter1_obs_a",
    noise_placeholders=["noiseParameter1_obs_a"],
)
problem.add_measurement(
    "obs_a", "", time=0, measurement=0.7, noise_parameters=("noise",)
)
problem.add_measurement(
    "obs_a", "", time=10, measurement=0.1, noise_parameters=("noise",)
)
problem.add_parameter("a0", lb=0, ub=10, nominal_value=1, estimate=True)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0, estimate=True)
problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)
problem.add_parameter("noise", lb=0, ub=10, nominal_value=5, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=15,
    brief="Simulation. Single parametric noise parameter override.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
