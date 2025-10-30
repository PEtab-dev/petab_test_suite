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

A parameter `p` is target of an event assignment that is executed at t = 490,
which is also the time point when the steady state is reached.
The event increases `p` by 1000, which is also the value of the observable.
The event must not be executed again after pre-equilibration
(the trigger state is not reinitialized).
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "_model.xml"

ant_model = """
model petab_test_0023
    p0 = 2
    p = p0
    dpdt = 1
    p' = piecewise(dpdt, p <= 500, 0)
    at p >= 500, t0=false, fromTrigger=false: p = p + 1000
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
problem.add_parameter("p0", estimate=True, lb=0, ub=10, nominal_value=10)
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
    # pre-equilibration starts with p=10, steady state is reached at
    #  t=490 with p=500, but the event must still be executed.
    # Then the observable is evaluated for the t=0 measurement
    1500,
    # Nothing happens during the "main" simulation until the
    #  observable is evaluated for the t=inf measurement.
    1500,
]

case = PetabV2TestCase.from_problem(
    id=23,
    brief="Events during steady-state simulations.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
