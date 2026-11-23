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

This case tests `time` in the target value of a species change in the first
period of an experiment with a non-zero start time.

The experiment starts at `t=5`, where `A` is set to `time + p`, with the
estimated parameter `p`, i.e., `A(5) = 5 + p`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

a0 = 1
b0 = 1
k1 = 0.8
k2 = 0.6
p = 3

problem = Problem()

problem.add_condition("c0", A_c="time + p")
problem.add_experiment("e0", 5, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)

ts = [5, 6, 15]
for observable_id in ("obs_a", "obs_b"):
    for t in ts:
        problem.add_measurement(
            observable_id, experiment_id="e0", time=t, measurement=1
        )

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)
problem.add_parameter("p", lb=0, ub=10, nominal_value=p, estimate=True)

problem.add_mapping("A_c", "A_() ** compartment")
problem.add_mapping("B_c", "B_() ** compartment")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
a5 = 5 + p
simulation_df[SIMULATION] = [
    *(analytical_a(t - 5, a5, b0, k1, k2) for t in ts),
    *(analytical_b(t - 5, a5, b0, k1, k2) for t in ts),
]

case = PetabV2TestCase.from_problem(
    id=41,
    brief="Simulation. Non-zero simulation start time. `time` in the target "
    "value of a species change in the first period.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
