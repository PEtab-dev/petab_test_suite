from inspect import cleandoc
from pathlib import Path

import numpy as np
from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabV2TestCase

DESCRIPTION = cleandoc("""
## Objective

This case tests a species change at a non-initial time point in a model
with conservation laws.

The model conserves the total amounts of `A` (`A + AB`) and `B`
(`B + AB`). At `t=10`, the amount of free `A` is increased by `1`, which
increases the total amount of `A` by `1`. The total amount of `B` is not
changed.

## Model

A reversible binding reaction `A + B <=> AB` with mass action kinetics,
without compartments, where `A` is free `A_(b=None)`, `B` is free
`B_(a=None)`, and `AB` is the complex `A_(b=1) % B_(a=1)`:
`dAB/dt = kf * A * B - kr * AB`.
""")

# problem --------------------------------------------------------------------

pysb_file = Path(__file__).parent / "model.py"

a0 = 1
b0 = 0.5
kf = 1
kr = 0.5
a_increment = 1


def binding_ab(t, ab_init, total_a, total_b, kf, kr):
    """Amount of `AB` for `A + B <=> AB` with total amounts of `A`, `B`.

    `dAB/dt = kf * (AB - r1) * (AB - r2)`, with `r1`, `r2` the roots of
    `kf * x^2 - (kf * (total_a + total_b) + kr) * x + kf * total_a * total_b`.
    """
    p = kf * (total_a + total_b) + kr
    disc = np.sqrt(p**2 - 4 * kf**2 * total_a * total_b)
    r1 = (p - disc) / (2 * kf)
    r2 = (p + disc) / (2 * kf)
    ratio = (ab_init - r1) / (ab_init - r2) * np.exp(kf * (r1 - r2) * t)
    return (r1 - r2 * ratio) / (1 - ratio)


problem = Problem()

problem.add_condition("c1", A_c=f"A_c + {a_increment}")
problem.add_experiment("e0", 0, "", 10, "c1")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)
problem.add_observable("obs_ab", "AB", noise_formula=0.5)
ts = [0, 5, 10, 15]
for t in ts:
    for obs_id in ("obs_a", "obs_b", "obs_ab"):
        problem.add_measurement(
            obs_id, experiment_id="e0", time=t, measurement=1
        )

problem.add_parameter("kf", lb=0, ub=10, nominal_value=kf, estimate=True)
problem.add_parameter("kr", lb=0, ub=10, nominal_value=kr, estimate=True)

problem.add_mapping("A_c", "A_(b=None)")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulations = []
# before the change at t=10
total_a, total_b = a0, b0
for t in [0, 5]:
    ab = binding_ab(t, 0, total_a, total_b, kf, kr)
    simulations.extend([total_a - ab, total_b - ab, ab])
# after the change at t=10
ab10 = binding_ab(10, 0, total_a, total_b, kf, kr)
total_a += a_increment
for t in [10, 15]:
    ab = binding_ab(t - 10, ab10, total_a, total_b, kf, kr)
    simulations.extend([total_a - ab, total_b - ab, ab])
simulation_df[SIMULATION] = simulations

case = PetabV2TestCase.from_problem(
    id=40,
    brief="Simulation. Species change at a non-initial time point in a "
    "model with conservation laws.",
    description=DESCRIPTION,
    model=pysb_file,
    problem=problem,
    simulation_df=simulation_df,
)
