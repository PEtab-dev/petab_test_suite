from inspect import cleandoc
from pathlib import Path

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import (
    PetabV2TestCase,
    analytical_a,
    analytical_b,
    antimony_to_sbml_str,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests the interaction of parameter table entries and
`InitialAssignment`s to model parameters.

* `k2` has the `InitialAssignment` `k2 = 2 * k1`, and is listed in the
  parameter table (estimated). The parameter table value (`0.6`) replaces the
  `InitialAssignment`.
* `a0` has the numeric `InitialAssignment` `a0 = 2 * 3`, and is listed in the
  parameter table (not estimated). The parameter table value (`1`) replaces
  the `InitialAssignment`.
* `b0` has the `InitialAssignment` `b0 = k1 / 4`, and is not listed in the
  parameter table. The `InitialAssignment` is kept, and is evaluated with the
  parameter table value of `k1` (`0.8`), i.e., `b0 = 0.2`.
* `s` is set to `k2` in the condition table at the start of the experiment,
  and `k2` is used as observable parameter override in the measurement table.
  Both refer to the parameter table value of `k2`, i.e., the same value that
  is used in the model.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics, with initial concentrations `a0` and `b0`.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "model.xml"

ant_model = """
model petab_test_0044
    k1 = 0.1
    k2 = 2 * k1
    a0 = 2 * 3
    b0 = k1 / 4
    s = 1
    compartment default_compartment = 1
    species A in default_compartment = a0
    species B in default_compartment = b0
    fwd: A => B; default_compartment * k1 * A
    rev: B => A; default_compartment * k2 * B
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
problem.add_condition("c0", s="k2")
problem.add_experiment("e1", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)
problem.add_observable("obs_s", "s", noise_formula=0.5)
problem.add_observable(
    "obs_scaled_a",
    "scale * A",
    noise_formula=0.5,
    observable_placeholders=["scale"],
)

for obs_id, t, m in [
    ("obs_a", 0, 0.7),
    ("obs_a", 10, 0.1),
    ("obs_b", 0, 0.3),
    ("obs_b", 10, 0.9),
    ("obs_s", 0, 0.5),
]:
    problem.add_measurement(obs_id, experiment_id="e1", time=t, measurement=m)
for t, m in [(0, 0.5), (10, 0.1)]:
    problem.add_measurement(
        "obs_scaled_a",
        experiment_id="e1",
        time=t,
        measurement=m,
        observable_parameters=["k2"],
    )

problem.add_parameter("k1", estimate=True, nominal_value=0.8, lb=0, ub=10)
problem.add_parameter("k2", estimate=True, nominal_value=0.6, lb=0, ub=10)
problem.add_parameter("a0", estimate=False, nominal_value=1, lb=0, ub=10)

# solutions ------------------------------------------------------------------

k1 = 0.8
k2 = 0.6
a0 = 1
b0 = k1 / 4

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(0, a0, b0, k1, k2),
    analytical_a(10, a0, b0, k1, k2),
    analytical_b(0, a0, b0, k1, k2),
    analytical_b(10, a0, b0, k1, k2),
    k2,
    k2 * analytical_a(0, a0, b0, k1, k2),
    k2 * analytical_a(10, a0, b0, k1, k2),
]

case = PetabV2TestCase.from_problem(
    id=44,
    brief="Simulation. Parameter table entries replace InitialAssignments "
    "to parameters.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
