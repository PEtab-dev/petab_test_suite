from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem

from petabtests import DEFAULT_SBML_FILE, PetabV2TestCase, analytical_a

DESCRIPTION = cleandoc("""
## Objective

This case tests initial compartment sizes in the condition table.

Note that changing the compartment size will only change the compartment size
itself. It will not change the concentration of concentration-based species
therein.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
k1 = 0.8
k2 = 0.6
# initial concentrations in the SBML model
a0_model = 1
b0_model = 1
# size of `compartment` in the SBML model and new value from petab condition
size_model = 1
size_new = 4

problem = Problem()

problem.add_condition("c0", compartment=size_new)

problem.add_experiment("e0", 0, "c0")

problem.add_observable("conc_a", "A", noise_formula="0.5")
problem.add_observable("amount_a", "A * compartment", noise_formula="0.5")

problem.add_measurement("conc_a", experiment_id="e0", time=0, measurement=0.7)
problem.add_measurement("conc_a", experiment_id="e0", time=10, measurement=0.1)
problem.add_measurement(
    "amount_a", experiment_id="e0", time=0, measurement=0.7
)
problem.add_measurement(
    "amount_a", experiment_id="e0", time=10, measurement=0.1
)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    # changing the compartment size does not change the concentration
    *(
        analytical_a(t, a0=a0_model, b0=b0_model, k1=k1, k2=k2)
        for t in simulation_df.query("observableId == 'conc_a'")[TIME]
    ),
    # but does change the amount
    *(
        analytical_a(t, a0=a0_model, b0=b0_model, k1=k1, k2=k2) * size_new
        for t in simulation_df.query("observableId == 'amount_a'")[TIME]
    ),
]

case = PetabV2TestCase.from_problem(
    id=12,
    brief="Simulation. Initial compartment size in condition table.",
    description=DESCRIPTION,
    model=DEFAULT_SBML_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
