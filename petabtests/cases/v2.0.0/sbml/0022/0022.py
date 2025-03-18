from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import (
    PetabV2TestCase,
    analytical_a,
    antimony_to_sbml_str,
    analytical_b,
)
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests simultaneous re-initialization of compartment size and
contained species.

## Model

Two simple conversion reactions `A <=> B`, `a <=> b` in a single compartment,
following mass action kinetics.

`A` and `B` are species defined in terms of concentrations, `a` and `b` are
`hasOnlySubstanceUnits=True` species defined in terms of amounts.

The compartment size and the species amounts/concentrations are re-initialized
at time 10. The assigned values are independent of the model state.

At time 10, the conditions table changes:
* The compartment size from 2 to 4.
* The concentration of `A` to `5`. This implies that the amount of
  `A` is changed to `5 * 2 = 10` (concentration * compartment size).
* The amount of `a` to `10`.

This leads to the following model state at time 10:
* The concentration of `A` is `10 / 4 = 2.5`
  (new amount divided by new volume).
* The amount of `a` is `10`, unaffected by the compartment size change.
* The concentration of `B` is `(2 * 2) / 4 = 1`
  (previous amount / new volume
  = previous concentration * previous volume / new volume).
* The amount of `b` remains at `4`, unaffected by the compartment size change.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "model.xml"

# kinetic parameters
k1 = 2
k2 = 1
# Initial values
# [A], [B], compartment volume
a_c0 = 2
b_c0 = 1
vol0 = 2
# Condition table values
a_update = 5
vol_update = 4
# Values after re-initialization
# [A], [B], compartment volume
a_c10 = 2.5
b_c10 = 1
vol_10 = vol_update

ant_model = f"""
model petab_test_0022
    compartment default_compartment = {vol0}
    initial_conc_A = {a_c0}
    initial_conc_B = {b_c0}

    species A in default_compartment = initial_conc_A
    substanceOnly species a in default_compartment = initial_conc_A * default_compartment

    species B in default_compartment = initial_conc_B
    substanceOnly species b in default_compartment = initial_conc_B * default_compartment

    k1 = {k1}
    k2 = {k2}

    A' = k2 * B - k1 * A
    B' = - k2 * B + k1 * A
    a' = k2 * b - k1 * a
    b' = - k2 * b + k1 * a

    # the result of the PEtab reinitialization should be the same as with
    #  the following event and no reinitialization:
    #
    #  at time >= 10: A = {a_update}, a = {a_update} * default_compartment, default_compartment = {vol_10}
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))


problem = Problem()
problem.add_observable("obs_a", "a", noise_formula="1")
problem.add_observable("obs_A", "A", noise_formula="1")
problem.add_observable("obs_b", "b", noise_formula="1")
problem.add_observable("obs_B", "B", noise_formula="1")

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, scale=LIN)
problem.add_experiment("experiment1", 0, "", 10, "condition2")
problem.add_condition(
    "condition2",
    "condition2",
    a=a_update * vol0,
    A=a_update,
    default_compartment=vol_10,
)


ts = [0, 5, 10, 15]
for t in ts:
    problem.add_measurement("obs_a", "", t, 2)
    problem.add_measurement("obs_A", "", t, 2)
    problem.add_measurement("obs_b", "", t, 1)
    problem.add_measurement("obs_B", "", t, 1)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    # a, A, b, B
    # t=0
    a_c0 * vol0,
    a_c0,
    b_c0 * vol0,
    b_c0,
    # t=5
    analytical_a(5, a_c0, b_c0, k1, k2) * vol0,
    analytical_a(5, a_c0, b_c0, k1, k2),
    analytical_b(5, a_c0, b_c0, k1, k2) * vol0,
    analytical_b(5, a_c0, b_c0, k1, k2),
    # t=10, re-initialize compartment size and contained species
    a_c10 * vol_10,
    a_c10,
    b_c10 * vol_10,
    b_c10,
    # t=15 (5s after re-initialization)
    analytical_a(5, a_c10, b_c10, k1, k2) * vol_10,
    analytical_a(5, a_c10, b_c10, k1, k2),
    analytical_b(5, a_c10, b_c10, k1, k2) * vol_10,
    analytical_b(5, a_c10, b_c10, k1, k2),
]

case = PetabV2TestCase.from_problem(
    id=22,
    brief="Simultaneous re-initialization of compartment size and contained species.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
