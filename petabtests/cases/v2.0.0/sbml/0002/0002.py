from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests support for multiple simulation conditions

The model is to be simulated for two different experimental conditions
(here: different initial concentrations).

Some values are overridden in the parameter table by numeric values.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0_c0 = 0.8
a0_c1 = 0.9
b0 = 0
k1 = 0.8
k2 = 0.6

problem = Problem()
problem.add_condition("c0", A=a0_c0)
problem.add_condition("c1", A=a0_c1)

problem.add_experiment("e1", 0, "c0")
problem.add_experiment("e2", 0, "c1")

problem.add_observable("obs_a", "A", noise_formula="1")

problem.add_measurement("obs_a", "e1", 0, 0.7)
problem.add_measurement("obs_a", "e1", 10, 0.1)
problem.add_measurement("obs_a", "e2", 0, 0.8)
problem.add_measurement("obs_a", "e2", 10, 0.2)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    *[analytical_a(t=t, a0=a0_c0, b0=b0, k1=k1, k2=k2) for t in [0, 10]],
    *[analytical_a(t=t, a0=a0_c1, b0=b0, k1=k1, k2=k2) for t in [0, 10]],
]

case = PetabV2TestCase.from_problem(
    id=2,
    brief="Simulation. Two conditions. Numeric parameter override.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
