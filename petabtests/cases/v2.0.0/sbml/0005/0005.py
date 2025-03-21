from inspect import cleandoc
from pathlib import Path

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import PetabV2TestCase, analytical_a, antimony_to_sbml_str

DESCRIPTION = cleandoc("""
## Objective

This case tests support for parametric overrides from condition table.

The model is to be simulated for two different experimental conditions
(here: different initial concentrations). The observable is offsetted by
a parametric override in the condition table (i.e. the actual value has
to be taken from the parameter table).

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
ant_model = """
model *petab_test_0011()
  compartment compartment_ = 1;
  species A in compartment_, B in compartment_;

  fwd: A => B; compartment_ * k1 * A;
  rev: B => A; compartment_ * k2 * B;

  A = a0;
  B = b0;
  offset_A = 0;
  a0 = 1;
  b0 = 0;
  k1 = 0;
  k2 = 0;
end
"""
model_file = Path(__file__).parent / "_model.xml"
model_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
problem.add_condition("c0", offset_A="offset_A_c0")
problem.add_condition("c1", offset_A="offset_A_c1")

problem.add_experiment("e1", 0, "c0")
problem.add_experiment("e2", 0, "c1")

problem.add_observable("obs_a", "A + offset_A", noise_formula="1")

problem.add_measurement("obs_a", "e1", 10, 2.1)
problem.add_measurement("obs_a", "e2", 10, 3.2)

problem.add_parameter(
    "a0", lb=0, ub=10, nominal_value=1, estimate=1, scale=LIN
)
problem.add_parameter(
    "b0", lb=0, ub=10, nominal_value=0, estimate=1, scale=LIN
)
problem.add_parameter(
    "k1", lb=0, ub=10, nominal_value=0.8, estimate=1, scale=LIN
)
problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, estimate=1, scale=LIN
)
problem.add_parameter(
    "offset_A_c0", lb=0, ub=10, nominal_value=2, estimate=1, scale=LIN
)
problem.add_parameter(
    "offset_A_c1", lb=0, ub=10, nominal_value=3, estimate=1, scale=LIN
)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(10, 1, 0, 0.8, 0.6) + offset for offset in [2, 3]
]

case = PetabV2TestCase.from_problem(
    id=5,
    brief="Simulation. Condition-specific parameters only defined in "
    "parameter table.",
    description=DESCRIPTION,
    model=model_file,
    problem=problem,
    simulation_df=simulation_df,
)
