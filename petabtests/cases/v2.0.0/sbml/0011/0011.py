from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem

from petabtests import PetabV2TestCase, analytical_a, antimony_to_sbml_str
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests initial concentrations in the condition table.
For species `B`, the initial concentration is specified in the condition
table, while for `A` it is given via an initial assignment in the SBML model.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
a0 = 1
b0 = 2
k1 = 0.8
k2 = 0.6

ant_model = f"""
model *petab_test_0011()
  compartment compartment_ = 1;
  species A in compartment_, B in compartment_;

  fwd: A => B; compartment_ * k1 * A;
  rev: B => A; compartment_ * k2 * B;

  A = a0;
  B = 1;  # overridden via condition table
  a0 = {a0};
  k1 = 0; # overridden via parameter table
  k2 = 0; # overridden via parameter table
end
"""
model_file = Path(__file__).parent / "_model.xml"
model_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()

problem.add_condition("c0", B=b0)

problem.add_experiment("e1", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")

problem.add_measurement("obs_a", experiment_id="e1", time=0, measurement=0.7)
problem.add_measurement("obs_a", experiment_id="e1", time=10, measurement=0.1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, a0=a0, b0=b0, k1=k1, k2=k2) for t in simulation_df[TIME]
]

case = PetabV2TestCase.from_problem(
    id=11,
    brief="Simulation. InitialAssignment to species overridden.",
    description=DESCRIPTION,
    model=model_file,
    problem=problem,
    simulation_df=simulation_df,
)
