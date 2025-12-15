from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem

from petabtests import (
    PetabV2TestCase,
    analytical_a,
    analytical_b,
    antimony_to_sbml_str,
)
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests the handling of initial concentrations that are specified
via mathematical expressions (rather than a single value or parameter) in
the conditions table. For species `A`, the initial concentration is given
by an expression containing both parameters to be estimated and parameters
that are not estimated. For species `B`, the initial concentration is
specified via an expression involving only parameters that are not
estimated.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
ant_model = """
model *petab_test_0026()
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

problem.add_condition("c0", A="initial_A1 + initial_A2", B="initial_B1 / initial_B2")
problem.add_experiment("e1", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_observable("obs_b", "B", noise_formula="0.5")
problem.add_measurement("obs_a", experiment_id="e1", time=0, measurement=0.7)
problem.add_measurement("obs_a", experiment_id="e1", time=10, measurement=0.1)
problem.add_measurement("obs_b", experiment_id="e1", time=0, measurement=0.7)
problem.add_measurement("obs_b", experiment_id="e1", time=10, measurement=0.1)

problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)
problem.add_parameter("initial_A1", lb=1, ub=10, nominal_value=0.5, estimate=True)
problem.add_parameter("initial_A2", lb=1, ub=10, nominal_value=1.5, estimate=False)
problem.add_parameter("initial_B1", lb=0, ub=10, nominal_value=9, estimate=False)
problem.add_parameter("initial_B2", lb=0, ub=10, nominal_value=3, estimate=False)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    *(analytical_a(t, 2, 3, 0.8, 0.6) for t in (0, 10)),
    *(analytical_b(t, 2, 3, 0.8, 0.6) for t in (0, 10)),
]

case = PetabV2TestCase.from_problem(
    id=26,
    brief="Simulation. Estimated initial value via math expressions in conditions table.",
    description=DESCRIPTION,
    model=model_file,
    problem=problem,
    simulation_df=simulation_df,
)
