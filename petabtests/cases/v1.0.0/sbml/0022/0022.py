from inspect import cleandoc
from pathlib import Path

import pandas as pd
from petab.v1.C import *

from petabtests import (
    PetabV1TestCase,
    analytical_a,
    analytical_b,
    antimony_to_sbml_str,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests the interaction of parameter table entries and
`InitialAssignment`s to model parameters.
The PEtab v1 specification does not explicitly address this interaction.
The expected behavior follows the PEtab v2 initialization semantics, where
parameter table values are applied before model initialization and replace
`InitialAssignment`s to the respective parameters.

* `k2` has the `InitialAssignment` `k2 = 2 * k1`, and is listed in the
  parameter table (estimated). The parameter table value (`0.6`) replaces the
  `InitialAssignment`.
* `a0` has the numeric `InitialAssignment` `a0 = 2 * 3`, and is listed in the
  parameter table (not estimated). The parameter table value (`1`) replaces
  the `InitialAssignment`.
* `b0` has the `InitialAssignment` `b0 = k1 / 4`, and is not listed in the
  parameter table. The `InitialAssignment` is kept, and is evaluated with the
  parameter table value of `k1` (`0.8`), i.e., `b0 = 0.2`.
* `s` is set to `k2` in the condition table, and `k2` is used as observable
  parameter override in the measurement table. Both refer to the parameter
  table value of `k2`, i.e., the same value that is used in the model.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics, with initial concentrations `a0` and `b0`.
""")

# problem --------------------------------------------------------------------

sbml_file = Path(__file__).parent / "model.xml"

ant_model = """
model petab_test_0022
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

condition_df = pd.DataFrame(
    data={
        CONDITION_ID: ["c0"],
        "s": ["k2"],
    }
).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: [
            "obs_a",
            "obs_a",
            "obs_b",
            "obs_b",
            "obs_s",
            "obs_scaled_a",
            "obs_scaled_a",
        ],
        SIMULATION_CONDITION_ID: ["c0"] * 7,
        TIME: [0, 10, 0, 10, 0, 0, 10],
        MEASUREMENT: [0.7, 0.1, 0.3, 0.9, 0.5, 0.5, 0.1],
        OBSERVABLE_PARAMETERS: [""] * 5 + ["k2"] * 2,
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_b", "obs_s", "obs_scaled_a"],
        OBSERVABLE_FORMULA: [
            "A",
            "B",
            "s",
            "observableParameter1_obs_scaled_a * A",
        ],
        NOISE_FORMULA: [0.5] * 4,
    }
).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(
    data={
        PARAMETER_ID: ["k1", "k2", "a0"],
        PARAMETER_SCALE: [LIN] * 3,
        LOWER_BOUND: [0] * 3,
        UPPER_BOUND: [10] * 3,
        NOMINAL_VALUE: [0.8, 0.6, 1],
        ESTIMATE: [1, 1, 0],
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

k1 = 0.8
k2 = 0.6
a0 = 1
b0 = k1 / 4

simulation_df = measurement_df.copy(deep=True).rename(
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

case = PetabV1TestCase(
    id=22,
    brief="Simulation. Parameter table entries replace InitialAssignments "
    "to parameters.",
    description=DESCRIPTION,
    model=sbml_file,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
