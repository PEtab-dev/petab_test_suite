from inspect import cleandoc
from pathlib import Path

import numpy as np
from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabV2TestCase

DESCRIPTION = cleandoc("""
## Objective

This case tests a compartment size change at a non-initial time point,
together with a state-dependent change of a species in that compartment.

At `t=10`, the compartment size parameter `vol` is changed from `2` to `4`,
and the amount of `B` is increased by `2`.
Changing `vol` changes the size of `cell`. PySB species are amounts,
which are not changed by this. Therefore, the amount of `A` is not changed
at `t=10`, and only the volume-dependent reaction rate changes.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics in a compartment `cell` with size `vol = 2`.
Following BioNetGen's volume scaling, and with PySB species being amounts,
`dA/dt = -k1 / vol * A * B`.
""")

# problem --------------------------------------------------------------------

pysb_file = Path(__file__).parent / "model.py"

vol = 2
vol_new = 4
a0 = 2
b0 = 1
b_increment = 2
k1 = 0.5


def bimolecular_a(t, a0, b0, k):
    """Amount of `A` for `dA/dt = -k * A * B` with `B - A` constant."""
    d = b0 - a0
    return d * a0 / (b0 * np.exp(k * d * t) - a0)


def bimolecular_b(t, a0, b0, k):
    """Amount of `B` for `dA/dt = -k * A * B` with `B - A` constant."""
    return bimolecular_a(t, a0, b0, k) + b0 - a0


problem = Problem()

problem.add_condition("c1", vol=vol_new, B_c=f"B_c + {b_increment}")
problem.add_experiment("e0", 0, "", 10, "c1")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)
ts = [0, 5, 10, 15]
for t in ts:
    for obs_id in ("obs_a", "obs_b"):
        problem.add_measurement(
            obs_id, experiment_id="e0", time=t, measurement=1
        )

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)

problem.add_mapping("B_c", "B_() ** cell")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# state after the changes at t=10
a10 = bimolecular_a(10, a0, b0, k1 / vol)
b10 = bimolecular_b(10, a0, b0, k1 / vol) + b_increment
simulation_df[SIMULATION] = [
    # A, B
    # t=0
    a0,
    b0,
    # t=5
    bimolecular_a(5, a0, b0, k1 / vol),
    bimolecular_b(5, a0, b0, k1 / vol),
    # t=10, after the changes
    a10,
    b10,
    # t=15
    bimolecular_a(5, a10, b10, k1 / vol_new),
    bimolecular_b(5, a10, b10, k1 / vol_new),
]

case = PetabV2TestCase.from_problem(
    id=37,
    brief="Simulation. Compartment size and species changed at a "
    "non-initial time point.",
    description=DESCRIPTION,
    model=pysb_file,
    problem=problem,
    simulation_df=simulation_df,
)
