from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabTestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests initial compartment sizes in the condition table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("c0", compartment=(OT_CUR_VAL, 3))
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

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 1, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabTestCase(
    id=12,
    brief="Simulation. Initial compartment size in condition table.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    experiment_dfs=[problem.experiment_df],
)
