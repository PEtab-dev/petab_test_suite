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

This case tests changing a rate parameter at a non-initial time point
to the value of an estimated parameter.

At `t=0`, `k1` is set to `0.8`. At `t=10`, `k1` is set to the estimated
parameter `k1_new`.
The species are not reinitialized at `t=10`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0 = 1
b0 = 1
k1 = 0.8
k1_new = 0.2
k2 = 0.6
problem = Problem()

problem.add_condition("c0", k1=k1)
problem.add_condition("c1", k1="k1_new")
problem.add_experiment("e0", 0, "c0", 10, "c1")

problem.add_observable("obs_a", "A", noise_formula=0.5)
for t, m in [(0, 0.7), (10, 0.5), (15, 0.6)]:
    problem.add_measurement("obs_a", experiment_id="e0", time=t, measurement=m)

problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)
problem.add_parameter(
    "k1_new", lb=0, ub=10, nominal_value=k1_new, estimate=True
)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
a10 = analytical_a(10.0, a0=a0, b0=b0, k1=k1, k2=k2)
b10 = analytical_b(10.0, a0=a0, b0=b0, k1=k1, k2=k2)
simulation_df[SIMULATION] = [
    a0,
    a10,
    analytical_a(5.0, a0=a10, b0=b10, k1=k1_new, k2=k2),
]

case = PetabV2TestCase.from_problem(
    id=34,
    brief="Simulation. Rate parameter changed to an estimated parameter at "
    "a non-initial time point.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
