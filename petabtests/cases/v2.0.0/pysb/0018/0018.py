from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import (
    DEFAULT_PYSB_FILE,
    PetabV2TestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for a non-zero simulation start time after
pre-equilibration.

The model is to be simulated for a preequilibration condition and a
simulation condition starting at `t=10`.
For preequilibration, `k1` is set to `0.3`, `A` is initialized with `0`,
and `B` with `2`.
For simulation, `k1` is set to `0.8`, `A` is reinitialized to the value in
the condition table after preequilibration, `B` is not updated.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_condition("preeq_c0", k1=0.3, B_c=2.0, A_c=0)
problem.add_condition("c0", k1=0.8, A_c=1)

problem.add_experiment("e0", TIME_PREEQUILIBRATION, "preeq_c0", 10, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.2)

problem.add_measurement("obs_a", experiment_id="e0", time=10, measurement=0.1)
problem.add_measurement("obs_a", experiment_id="e0", time=11, measurement=0.7)
problem.add_measurement("obs_a", experiment_id="e0", time=20, measurement=0.1)
problem.add_measurement("obs_b", experiment_id="e0", time=10, measurement=0.1)

problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)

problem.add_mapping("A_c", "A_() ** compartment")
problem.add_mapping("B_c", "B_() ** compartment")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# simulate for far time point as steady state
steady_state_b = analytical_b(1000, 0, 2.0, 0.3, 0.6)
# use steady state as initial state, shifted by the start time t=10
simulation_df[SIMULATION] = [
    analytical_a(0, 1, steady_state_b, 0.8, 0.6),
    analytical_a(1, 1, steady_state_b, 0.8, 0.6),
    analytical_a(10, 1, steady_state_b, 0.8, 0.6),
    analytical_b(0, 1, steady_state_b, 0.8, 0.6),
]

case = PetabV2TestCase.from_problem(
    id=18,
    brief="Simulation. Preequilibration. Non-zero simulation start time.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
