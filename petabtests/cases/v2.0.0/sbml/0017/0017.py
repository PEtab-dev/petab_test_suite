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

This case tests support for pre-equilibration with reinitialization of a
species.

The model is to be simulated for a pre-equilibration condition and a
simulation condition.
For pre-equilibration, species `B` is initialized with `2`. For simulation,
`A` is reinitialized to the value in the condition table after
pre-equilibration. `B` is not updated, meaning that it keeps the state from
pre-equilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("preeq_c0", k1=0.3, B=2.0, A=0)
problem.add_condition("c0", k1=0.8, A=1)

problem.add_experiment("e0", "-inf", "preeq_c0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_observable("obs_b", "B", noise_formula="0.5")

problem.add_measurement("obs_a", "e0", 0, 0.7)
problem.add_measurement("obs_a", "e0", 1, 0.7)
problem.add_measurement("obs_a", "e0", 10, 0.1)
problem.add_measurement("obs_b", "e0", 0, 2.0)

problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, estimate=True, scale=LIN
)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# simulate for far time point as steady state
steady_state_b = analytical_b(1000, 0, 2.0, 0.3, 0.6)
# use steady state as initial state
simulation_df[SIMULATION] = [
    analytical_a(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME][:-1]
] + [
    analytical_b(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME][-1:]
]

case = PetabV2TestCase.from_problem(
    id=17,
    brief="Simulation. Pre-equilibration. One species reinitialized, one not."
    "InitialAssignment to species overridden.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
