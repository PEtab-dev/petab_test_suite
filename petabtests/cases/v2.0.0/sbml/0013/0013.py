from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import PetabV2TestCase, analytical_a, antimony_to_sbml_str
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests parametric initial concentrations in the condition table.

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
  B = 1;
  a0 = 1;
  k1 = 0;
  k2 = 0;
end
"""
model_file = Path(__file__).parent / "_model.xml"
model_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()

problem.add_condition("c0", B="par")
problem.add_experiment("e1", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_measurement("obs_a", "e1", 0, 0.7)
problem.add_measurement("obs_a", "e1", 10, 0.1)

problem.add_parameter(
    "k1", lb=0, ub=10, nominal_value=0.8, estimate=1, scale=LIN
)
problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, estimate=1, scale=LIN
)
problem.add_parameter(
    "par", lb=0, ub=10, nominal_value=7, estimate=1, scale=LIN
)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 7, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabV2TestCase.from_problem(
    id=13,
    brief="Simulation. Species with InitialAssignment overridden by "
    "parameter.",
    description=DESCRIPTION,
    model=model_file,
    problem=problem,
    simulation_df=simulation_df,
)
