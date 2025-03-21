from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests observable-dependent parametric noise parameter overrides in
the measurement table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

problem = Problem()
problem.add_measurement("obs_a", "", 0, 0.7, noise_parameters=["noise"])
problem.add_measurement("obs_a", "", 10, 0.1, noise_parameters=["noise"])
problem.add_observable(
    "obs_a", "A", noise_formula="noiseParameter1_obs_a * obs_a"
)
problem.add_parameter("a0", lb=0, ub=10, nominal_value=1, scale=LIN)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0, scale=LIN)
problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, scale=LIN)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, scale=LIN)
problem.add_parameter("noise", lb=0, ub=10, nominal_value=5, scale=LIN)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]


case = PetabV2TestCase(
    id=21,
    brief="Observable-dependent noise formula.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    condition_dfs=[],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
