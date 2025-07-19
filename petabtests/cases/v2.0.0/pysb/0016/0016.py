from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests parameters in mapping table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()
problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_measurement("obs_a", "", time=0, measurement=0.7)
problem.add_measurement("obs_a", "", time=10, measurement=0.1)
problem.add_parameter(
    "maps_to_a0", lb=0, ub=10, nominal_value=1, estimate=True
)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0, estimate=True)
problem.add_parameter(
    "maps_to_k1", lb=0, ub=10, nominal_value=0.8, estimate=True
)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)

problem.add_mapping("maps_to_a0", "a0")
problem.add_mapping("maps_to_b0", "b0")
problem.add_mapping("maps_to_k1", "k1")
problem.add_mapping("maps_to_k2", "k2")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=16,
    brief="Parameters in mapping table.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    mapping_df=problem.mapping_df,
)
