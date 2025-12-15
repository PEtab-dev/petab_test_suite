from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import PetabV2TestCase, analytical_a, analytical_b, antimony_to_sbml_str
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests applies a PEtab condition at a non-initial time point,
where the condition is triggered at a time point that does not have any
measurements.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0 = 1
b0 = 1
k1 = 0.8
k2 = 0.6

ant_model = f"""
model *petab_test_0028()
  compartment compartment_ = 1;
  species A in compartment_, B in compartment_;

  fwd: A => B; compartment_ * k1 * A;
  rev: B => A; compartment_ * k2 * B;

  A = 1;
  B = 1;
  k1 = 0;  # overridden by parameter table
  k2 = 0;  # overridden by parameter table
end
"""
model_file = Path(__file__).parent / "_model.xml"
model_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()

problem.add_condition(
    "condition1",
    "condition1",
    A="A + 5.0",
)
problem.add_experiment("experiment1", 0, "", 7, "condition1")


problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_measurement("obs_a", experiment_id="experiment1", time=0, measurement=0.7)
problem.add_measurement("obs_a", experiment_id="experiment1", time=10, measurement=0.1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
a7 = analytical_a(7.0, a0=a0, b0=b0, k1=k1, k2=k2)
b7 = analytical_b(7.0, a0=a0, b0=b0, k1=k1, k2=k2)
simulation_df[SIMULATION] = [
    a0,
    analytical_a(3.0, a0=(a7 + 5.0), b0=b7, k1=k1, k2=k2)
]

case = PetabV2TestCase.from_problem(
    id=28,
    brief="Simulation. None t0 condition applied at time-point "
    "without measurements.",
    description=DESCRIPTION,
    model=model_file,
    problem=problem,
    simulation_df=simulation_df,
)
