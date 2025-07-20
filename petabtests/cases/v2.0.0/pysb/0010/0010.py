from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for partial preequilibration.

The model is to be simulated for a preequilibration condition and a
simulation condition.
Species `B` is to be reinitialized after preequilibration.
For `A` the preequilibration result is to be used.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("preeq_c0", k1=0.3, B=0)
problem.add_condition("c0", k1=0.8, B=1)

problem.add_experiment("e0", TIME_PREEQUILIBRATION, "preeq_c0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)

problem.add_measurement("obs_a", "e0", time=1, measurement=0.7)
problem.add_measurement("obs_a", "e0", time=10, measurement=0.1)

problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)
problem.add_mapping("A", "A_() ** compartment")
problem.add_mapping("B", "B_() ** compartment")


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# simulate for far time point as steady state
steady_state_a = analytical_a(1000, 1, 0, 0.3, 0.6)
# use steady state as initial state
simulation_df[SIMULATION] = [
    analytical_a(t, steady_state_a, 1, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase(
    id=10,
    brief="Simulation. Preequilibration. One species reinitialized, one not. "
    "InitialAssignment to species overridden.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
    mapping_df=problem.mapping_df,
    experiment_dfs=[problem.experiment_df],
)
