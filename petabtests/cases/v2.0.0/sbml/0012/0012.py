from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem

from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests initial compartment sizes in the condition table.

Note that this change will preserve the initial state of the model in terms
of amounts. I.e., the change of the compartment size via the conditions table,
will change the concentrations of all contained species.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

problem = Problem()

problem.add_condition("c0", compartment=4)

problem.add_experiment("e0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")

problem.add_measurement("obs_a", "e0", 0, 0.7)
problem.add_measurement("obs_a", "e0", 10, 0.1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# changing the compartent volume from 1 to 4 will change the initial
#  concentration to 1 * (1/4)
simulation_df[SIMULATION] = [
    analytical_a(t, 0.25, 0.25, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase.from_problem(
    id=12,
    brief="Simulation. Initial compartment size in condition table.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
