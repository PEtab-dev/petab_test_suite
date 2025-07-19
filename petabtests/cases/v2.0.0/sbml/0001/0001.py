from inspect import cleandoc

from petab.v2.C import *
from petab.v2.core import *
from petab.v2 import Problem
from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case features a simple test with two data points and no particular
features.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

problem = Problem()
problem += Observable(id="obs_a", formula="A", noise_formula=0.5)
problem += Measurement(observable_id="obs_a", time=0, measurement=0.7)
problem += Measurement(observable_id="obs_a", time=10, measurement=0.1)
problem += Parameter(id="a0", lb=0, ub=10, nominal_value=1)
problem += Parameter(id="b0", lb=0, ub=10, nominal_value=0)
problem += Parameter(id="k1", lb=0, ub=10, nominal_value=0.8)
problem += Parameter(id="k2", lb=0, ub=10, nominal_value=0.6)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 0, 0.8, 0.6) for t in simulation_df[TIME]
]


case = PetabV2TestCase.from_problem(
    id=1,
    problem=problem,
    brief="Simulation. Nothing special.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    simulation_df=simulation_df,
)
