from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import PetabV2TestCase, analytical_a, analytical_b, DEFAULT_SBML_FILE

DESCRIPTION = cleandoc("""
## Objective

This case tests applying two PEtab conditions simultaneously, at a time
point that also has measurement values.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0 = 1
b0 = 1
k1 = 0.8
k2 = 0.6
problem = Problem()

problem.add_condition(
    "condition1",
    A="A + 5.0",
)
problem.add_condition(
    "condition2",
    B="B + 3.0",
)
problem.add_experiment("experiment1",
                       0, "",
                       10, "condition1",
                       10, "condition2")

problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_observable("obs_b", "B", noise_formula="0.1")
problem.add_measurement("obs_a", experiment_id="experiment1", time=0, measurement=0.7)
problem.add_measurement("obs_b", experiment_id="experiment1", time=0, measurement=1.0)
problem.add_measurement("obs_a", experiment_id="experiment1", time=10, measurement=0.1)
problem.add_measurement("obs_b", experiment_id="experiment1", time=10, measurement=0.4)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    a0,
    b0,
    analytical_a(10.0, a0=a0, b0=b0, k1=k1, k2=k2) + 5.0,
    analytical_b(10.0, a0=a0, b0=b0, k1=k1, k2=k2) + 3.0,
]

case = PetabV2TestCase.from_problem(
    id=31,
    brief="Simulation. Two PEtab conditions applied at the same "
    "time point.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
