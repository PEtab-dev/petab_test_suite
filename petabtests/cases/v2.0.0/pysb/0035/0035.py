from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import DEFAULT_PYSB_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests changing a parameter that is used in an `Initial`, in the
first and in a later period.

At `t=0`, `a0` is set to `2`. This is applied before model initialization,
so the initial amount of `A` is `2`.
At `t=10`, `a0` is set to `5`. Since species are not reinitialized
according to their `Initial`s, this does not affect `A`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
`a0` is a `pysb.Parameter` that defines the initial amount of `A`.
""")

# problem --------------------------------------------------------------------
a0 = 2
b0 = 1
k1 = 0.8
k2 = 0.6
problem = Problem()

problem.add_condition("c0", a0=a0)
problem.add_condition("c1", a0=5)
problem.add_experiment("e0", 0, "c0", 10, "c1")

problem.add_observable("obs_a", "A", noise_formula=0.5)
for t, m in [(0, 0.7), (10, 0.5), (15, 0.6)]:
    problem.add_measurement("obs_a", experiment_id="e0", time=t, measurement=m)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, a0=a0, b0=b0, k1=k1, k2=k2) for t in simulation_df[TIME]
]

case = PetabV2TestCase.from_problem(
    id=35,
    brief="Simulation. Parameter used in an Initial changed in the first "
    "and in a later period.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
