from inspect import cleandoc
from pathlib import Path

import numpy as np
from petab.v2 import Problem
from petab.v2.C import *

from petabtests import PetabV2TestCase

DESCRIPTION = cleandoc("""
## Objective

This case tests a compartment size change in the first period, for a model
where the compartment size affects the dynamics.

The compartment size is changed by targeting the compartment ID `cell`.
Experiment `e0` changes the size of `cell` from `2` to `4` at `t=0`.
The species amounts are not changed.
Experiment `e_ref` uses the default compartment size.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics in a compartment `cell` with size `vol = 2`.
Following BioNetGen's volume scaling, and with PySB species being amounts,
`dA/dt = -k1 / size(cell) * A * B`.
""")

# problem --------------------------------------------------------------------

pysb_file = Path(__file__).parent / "model.py"

vol = 2
vol_new = 4
a0 = 2
b0 = 1
k1 = 0.5


def bimolecular_a(t, a0, b0, k):
    """Amount of `A` for `dA/dt = -k * A * B` with `B - A` constant."""
    d = b0 - a0
    return d * a0 / (b0 * np.exp(k * d * t) - a0)


problem = Problem()

problem.add_condition("c0", cell=vol_new)
problem.add_experiment("e_ref", 0, "")
problem.add_experiment("e0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)
ts = [0, 2, 5]
for t in ts:
    problem.add_measurement(
        "obs_a", experiment_id="e_ref", time=t, measurement=1
    )
for t in ts:
    problem.add_measurement("obs_a", experiment_id="e0", time=t, measurement=1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    bimolecular_a(t, a0, b0, k1 / vol) for t in ts
] + [bimolecular_a(t, a0, b0, k1 / vol_new) for t in ts]

case = PetabV2TestCase.from_problem(
    id=36,
    brief="Simulation. Compartment size in the condition table, "
    "with volume-dependent dynamics.",
    description=DESCRIPTION,
    model=pysb_file,
    problem=problem,
    simulation_df=simulation_df,
)
