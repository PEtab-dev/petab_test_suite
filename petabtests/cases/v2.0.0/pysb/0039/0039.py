from inspect import cleandoc
from pathlib import Path

import numpy as np
from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabV2TestCase

DESCRIPTION = cleandoc("""
## Objective

This case tests changes at a non-initial time point whose target values
depend on estimated parameters, targeting a parameter and a species.

* `e_a0`: At `t=10`, the parameter `a0` is set to the estimated parameter
  `a0_new`. `a0` is used both as synthesis rate and in the `Initial` of
  `A`. The synthesis rate changes from `t=10` on, but `A` is not
  reinitialized.
* `e_add`: At `t=10`, the amount of `A` is increased by the estimated
  parameter `p_add`.

## Model

Synthesis and degradation of `A`, without compartments:
`dA/dt = a0 - kdeg * A`, with initial amount `A(0) = a0`.
""")

# problem --------------------------------------------------------------------

pysb_file = Path(__file__).parent / "model.py"

a0 = 1
kdeg = 0.5
a0_new = 3
p_add = 2


def synthesis_degradation_a(t, a_init, a0, kdeg):
    """Amount of `A` for `dA/dt = a0 - kdeg * A`."""
    return a0 / kdeg + (a_init - a0 / kdeg) * np.exp(-kdeg * t)


problem = Problem()

problem.add_condition("c_a0", a0="a0_new")
problem.add_condition("c_add", A_c="A_c + p_add")
problem.add_experiment("e_a0", 0, "", 10, "c_a0")
problem.add_experiment("e_add", 0, "", 10, "c_add")

problem.add_observable("obs_a", "A", noise_formula=0.5)
ts = [0, 10, 15]
for experiment_id in ("e_a0", "e_add"):
    for t in ts:
        problem.add_measurement(
            "obs_a", experiment_id=experiment_id, time=t, measurement=1
        )

problem.add_parameter("kdeg", lb=0, ub=10, nominal_value=kdeg, estimate=True)
problem.add_parameter(
    "a0_new", lb=0, ub=10, nominal_value=a0_new, estimate=True
)
problem.add_parameter("p_add", lb=0, ub=10, nominal_value=p_add, estimate=True)

problem.add_mapping("A_c", "A_()")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
a10 = synthesis_degradation_a(10, a0, a0, kdeg)
simulation_df[SIMULATION] = [
    # e_a0
    a0,
    a10,
    synthesis_degradation_a(5, a10, a0_new, kdeg),
    # e_add
    a0,
    a10 + p_add,
    synthesis_degradation_a(5, a10 + p_add, a0, kdeg),
]

case = PetabV2TestCase.from_problem(
    id=39,
    brief="Simulation. Parameter and species changed to estimated "
    "parameter-dependent values at a non-initial time point.",
    description=DESCRIPTION,
    model=pysb_file,
    problem=problem,
    simulation_df=simulation_df,
)
