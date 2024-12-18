from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests initial concentrations in the condition table.
For species `B`, the initial concentration is specified in the condition
table, while for `A` it is given via an assignment rule in the SBML model.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("c0", B=(VT_INITIAL, 2))

problem.add_experiment("e0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)

problem.add_measurement("obs_a", "e0", time=0, measurement=0.7)
problem.add_measurement("obs_a", "e0", time=10, measurement=0.1)

problem.add_parameter(
    "k1", lb=0, ub=10, nominal_value=0.8, scale=LIN, estimate=True
)
problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, scale=LIN, estimate=True
)

problem.add_mapping("A", "A_() ** compartment")
problem.add_mapping("B", "B_() ** compartment")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 2, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabTestCase(
    id=11,
    brief="Simulation. InitialAssignment to species overridden.",
    description=DESCRIPTION,
    model="conversion_modified_pysb.py",
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    mapping_df=problem.mapping_df,
    experiment_dfs=[problem.experiment_df],
)
