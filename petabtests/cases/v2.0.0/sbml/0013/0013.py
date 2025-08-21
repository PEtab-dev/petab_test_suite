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
a0 = 1
b0 = 7
k1 = 0.8
k2 = 0.6

ant_model = f"""
model *petab_test_0013()
  compartment compartment_ = 1;
  species A in compartment_, B in compartment_;

  fwd: A => B; compartment_ * k1 * A;
  rev: B => A; compartment_ * k2 * B;

  A = a0;
  B = 1;  # overridden by condition/parameter table
  a0 = {a0};
  k1 = 0;  # overridden by parameter table
  k2 = 0;  # overridden by parameter table
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

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)
problem.add_parameter("par", lb=0, ub=10, nominal_value=b0, estimate=True)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [
    analytical_a(t, a0=a0, b0=b0, k1=k1, k2=k2) for t in simulation_df[TIME]
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
