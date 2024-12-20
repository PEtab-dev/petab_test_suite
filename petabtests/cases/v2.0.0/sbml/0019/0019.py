from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import DEFAULT_SBML_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

Test different model entities inside the mapping table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()
# TODO use mapping here
problem.add_measurement("obs_a", "", 0, 0.7)
problem.add_measurement("obs_a", "", 10, 0.1)
problem.add_observable("obs_a", "maps_to_A", 0.5)
problem.add_parameter("a0", lb=0, ub=10, nominal_value=1, scale=LIN)
problem.add_parameter("maps_to_b0", lb=0, ub=10, nominal_value=0, scale=LIN)
problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, scale=LIN)
problem.add_parameter("maps_to_k2", lb=0, ub=10, nominal_value=0.6, scale=LIN)
problem.add_mapping("maps_to_a0", "a0")
problem.add_mapping("maps_to_b0", "b0")
problem.add_mapping("maps_to_k1", "k1")
problem.add_mapping("maps_to_k2", "k2")
problem.add_mapping("maps_to_A", "A")
problem.add_mapping("maps_to_B", "B")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]
case = PetabTestCase(
    id=19,
    brief="Mapping table.",
    description=DESCRIPTION,
    # TODO add local parameter and use in mapping table
    model=DEFAULT_SBML_FILE,
    condition_dfs=[],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    mapping_df=problem.mapping_df,
)
