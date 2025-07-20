from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import (
    DEFAULT_SBML_FILE,
    PetabV2TestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for preequilibration.

The model is to be simulated for a preequilibration condition and a
simulation condition.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

problem = Problem()
problem.add_condition("preeq_c0", k1=0.3)
problem.add_condition("c0", k1=0.8)

problem.add_experiment("e0", "-inf", "preeq_c0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")

problem.add_measurement("obs_a", "e0", 1, 0.7)
problem.add_measurement("obs_a", "e0", 10, 0.1)

problem.add_parameter("a0", lb=0, ub=10, nominal_value=1, estimate=True)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# simulate for far time point as steady state
steady_state_a = analytical_a(1000, 1, 0, 0.3, 0.6)
steady_state_b = analytical_b(1000, 1, 0, 0.3, 0.6)
# use steady state as initial state
simulation_df[SIMULATION] = [
    analytical_a(t, steady_state_a, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME]
]

case = PetabV2TestCase.from_problem(
    id=9,
    brief="Simulation. Preequilibration.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
