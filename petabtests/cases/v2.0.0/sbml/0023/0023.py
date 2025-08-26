from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import (
    PetabV2TestCase,
    antimony_to_sbml_str,
)
from pathlib import Path

DESCRIPTION = cleandoc(r"""
## Objective

This case tests events occurring during steady-state simulations.

## Model

A parameter `p` is target of an event assignment that is executed at t = 1000.
Although the model starts with $\dot{x} = 0$, the simulation must still run
until $\dot{x}$ *remains* 0, i.e., the event must still be executed.
This is applies to both the pre-simulation and the simulation for the
steady state measurement.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "_model.xml"

ant_model = """
model petab_test_0023
    p0 = 2
    p = p0

    at time >= 1000: p = p + 1
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
problem.add_parameter("p", estimate=True, lb=0, ub=10, nominal_value=1)
problem.add_observable("obs_p", "p", noise_formula="1")
problem.add_experiment("experiment1", float("-inf"), None)

problem.add_measurement(
    "obs_p", experiment_id="experiment1", time=0, measurement=2
)
problem.add_measurement(
    "obs_p", experiment_id="experiment1", time=float("inf"), measurement=3
)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    # pre-simulation starts with p=1, then p is increased by 1 at t=1000
    # then the observable is evaluated for the t=0 measurement
    2,
    # then the steady state simulation is run,
    #  where p is increased by 1 at t=1000,
    #  and the observable is evaluated for the t=inf measurement
    3,
]

case = PetabV2TestCase.from_problem(
    id=23,
    brief="Events during steady-state simulations.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
