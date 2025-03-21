from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from pathlib import Path
from petabtests import (
    PetabV2TestCase,
    analytical_a,
    analytical_b,
    antimony_to_sbml_str,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for RateRules and partial preequilibration with `NaN`'s
in the condition file.

The model is to be simulated for a preequilibration condition and a
simulation condition.
For preequilibration, species `B` is initialized with `0`. For simulation,
`B` is set to `NaN`, meaning that it is initialized with the result from
preequilibration.
`A` is reinitialized to the value in the condition table after
preequilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics. Dynamics of are specified as `RateRule`s targeting a
parameter and a species.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "model.xml"

ant_model = """
model petab_test_0018
    a0 = 1
    b0 = 1
    k1 = 0
    k2 = 0
    compartment default_compartment
    species A in default_compartment = a0
    B = b0
    A' = k2 * B - k1 * A
    B' = - default_compartment * k2 * B + default_compartment * k1 * A
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()

problem.add_condition("preeq_c0", k1=0.3, B=2.0, A=0)
problem.add_condition("c0", k1=0.8, A=1)

problem.add_experiment("e0", "-inf", "preeq_c0", 0, "c0")

problem.add_observable("obs_a", "A", noise_formula="0.5")
problem.add_observable("obs_b", "B", noise_formula="0.2")

problem.add_measurement("obs_a", "e0", 0, 0.1)
problem.add_measurement("obs_a", "e0", 1, 0.7)
problem.add_measurement("obs_a", "e0", 10, 0.1)
problem.add_measurement("obs_b", "e0", 0, 0.1)

problem.add_parameter(
    "k2", lb=0, ub=10, nominal_value=0.6, estimate=1, scale=LIN
)


# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
# simulate for far time point as steady state
steady_state_b = analytical_b(1000, 0, 2.0, 0.3, 0.6)
# use steady state as initial state
simulation_df.iloc[:3, simulation_df.columns.get_loc(SIMULATION)] = [
    analytical_a(t, 1, steady_state_b, 0.8, 0.6) for t in simulation_df[TIME]
][:3]
simulation_df.iloc[3:, simulation_df.columns.get_loc(SIMULATION)] = [
    analytical_b(t, 1, steady_state_b, 0.8, 0.6) for t in simulation_df[TIME]
][3:]


case = PetabV2TestCase.from_problem(
    id=18,
    brief="Simulation. Preequilibration and RateRules. One state "
    "reinitialized, one not (NaN in condition table). InitialAssignment "
    "to species overridden.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
