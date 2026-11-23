from inspect import cleandoc
from pathlib import Path

import numpy as np
from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabV2TestCase

DESCRIPTION = cleandoc("""
## Objective

This case tests first-period species changes that differ between
experiments, including a change of a species without an `Initial`.

* `e_a3`: `A` is set to `3` at `t=0`.
* `e_a5`: `A` is set to `5` at `t=0`.
* `e_ref`: no changes.
* `e_c2`: `C` is set to `2` at `t=0`. The model has no `Initial` for `C`,
  i.e., its default initial amount is `0`.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics, without compartments.
`dA/dt = dB/dt = -k1 * A * B`, `dC/dt = k1 * A * B`.
`A` and `B` have `Initial`s with amounts `1`, `C` has no `Initial`.
""")

# problem --------------------------------------------------------------------

pysb_file = Path(__file__).parent / "model.py"

a0 = 1
b0 = 1
k1 = 0.5


def bimolecular_a(t, a0, b0, k):
    """Amount of `A` for `dA/dt = -k * A * B` with `B - A` constant."""
    d = b0 - a0
    if d == 0:
        return a0 / (1 + k * a0 * t)
    return d * a0 / (b0 * np.exp(k * d * t) - a0)


problem = Problem()

problem.add_condition("c_a3", A_c=3)
problem.add_condition("c_a5", A_c=5)
problem.add_condition("c_c2", C_c=2)
# experiment ID, initial amounts of A and C
experiments = [
    ("e_a3", 3, 0),
    ("e_a5", 5, 0),
    ("e_ref", a0, 0),
    ("e_c2", a0, 2),
]
problem.add_experiment("e_a3", 0, "c_a3")
problem.add_experiment("e_a5", 0, "c_a5")
problem.add_experiment("e_ref", 0, "")
problem.add_experiment("e_c2", 0, "c_c2")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_c", "C", noise_formula=0.5)
ts = [0, 2, 5]
for experiment_id, *_ in experiments:
    for t in ts:
        for obs_id in ("obs_a", "obs_c"):
            problem.add_measurement(
                obs_id, experiment_id=experiment_id, time=t, measurement=1
            )

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)

problem.add_mapping("A_c", "A_()")
problem.add_mapping("C_c", "C_()")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulations = []
for _, a_init, c_init in experiments:
    for t in ts:
        a = bimolecular_a(t, a_init, b0, k1)
        # A, C
        simulations.extend([a, c_init + a_init - a])
simulation_df[SIMULATION] = simulations

case = PetabV2TestCase.from_problem(
    id=38,
    brief="Simulation. First-period species changes differing between "
    "experiments. Species without Initial changed.",
    description=DESCRIPTION,
    model=pysb_file,
    problem=problem,
    simulation_df=simulation_df,
)
