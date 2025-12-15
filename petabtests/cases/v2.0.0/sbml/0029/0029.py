from inspect import cleandoc

from petab.v2.C import *
from petab.v2.core import *
from petab.v2 import Problem
from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case features a simple test with two data points with a non-zero
simulation start time.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0 = 1.0
b0 = 1.0
k1 = 0.8
k2 = 0.6

problem = Problem()
problem.add_experiment("e1", 5.0, "")

problem.add_observable("obs_a", "A", noise_formula="1")

problem.add_measurement("obs_a", experiment_id="e1", time=5, measurement=0.01)
problem.add_measurement("obs_a", experiment_id="e1", time=10, measurement=0.1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t=(t - 5.0), a0=a0, b0=b0, k1=k1, k2=k2) for t in simulation_df[TIME]
]


case = PetabV2TestCase.from_problem(
    id=29,
    problem=problem,
    brief="Simulation. Non-zero simulation start time",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    simulation_df=simulation_df,
)
