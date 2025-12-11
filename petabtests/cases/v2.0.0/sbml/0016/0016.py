from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import (
    PetabV2TestCase,
    antimony_to_sbml_str,
)
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests simultaneous re-initialization of compartment size and
contained species with state-dependent expressions.

## Model

A species `S`, defined in terms of concentrations, with `dS/dt = p = 1`,
in a compartment `C`. `S` and `C` are changed via the condition table.

There is a PEtab condition triggered at `t=10` which triggers an SBML
event that re-initializes the compartment size that must be executed
after the condition table is applied.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "model.xml"

vol0 = 4
conc0 = 2
conc10 = 8
dSdt = 1
vol10 = (conc0 + 10 * dSdt) + vol0  # = 16

ant_model = f"""
model petab_test_0016
    compartment C = {vol0}

    species S in C = 3 # this is overwritten by the condition table

    p = {dSdt}
    S' = p

    at S >= 14, fromTrigger=false: C = C * 2 # this is triggered by the PEtab condition
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
problem.add_observable("obs_C", "C", noise_formula="1")
problem.add_observable("obs_amount_S", "S * C", noise_formula="1")
problem.add_observable("obs_conc_S", "S", noise_formula="1")

problem.add_parameter("p", lb=0, ub=10, nominal_value=1)

problem.add_experiment("experiment1", 0, "condition1", 10, "condition2")
# at t=0
problem.add_condition(
    "condition1",
    "condition1",
    S=conc0,
)
# t=10
problem.add_condition(
    "condition2",
    "condition2",
    S="S + C",
    C=conc10,
)

ts = [0, 5, 10, 15]
for t in ts:
    for obs in ["obs_C", "obs_amount_S", "obs_conc_S"]:
        problem.add_measurement(
            obs, experiment_id="experiment1", time=t, measurement=t
        )

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    # vol, amount, conc
    # --- t=0 ---
    vol0,
    conc0 * vol0,
    conc0,
    # --- t=5 ---
    vol0,
    (conc0 + 5 * dSdt) * vol0,
    (conc0 + 5 * dSdt),
    # --- t=10 ---
    # condition table:
    # 8, 16 * 8 = 128 , 12 + 4 = 16
    # event (triggered by condition table)
    # volume is changed by event, amount is preserved, conc changes
    # C = 8 * 2 = 16, 128, 8
    vol10,
    conc10 * vol10,
    conc10,
    # --- t=15 ---
    vol10,
    (conc10 + 5 * dSdt) * vol10,
    (conc10 + 5 * dSdt)
]

case = PetabV2TestCase.from_problem(
    id=16,
    brief="Simultaneous state-dependent re-initialization of compartment size and contained species followed by event.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
