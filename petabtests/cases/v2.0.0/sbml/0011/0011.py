from inspect import cleandoc

import pandas as pd
from petab.v1.C import *

from petabtests import PetabTestCase, analytical_a, antimony_to_sbml_str
from pathlib import Path

DESCRIPTION = cleandoc("""
## Objective

This case tests initial concentrations in the condition table.
For species `B`, the initial concentration is specified in the condition
table, while for `A` it is given via an assignment rule in the SBML model.

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

condition_df = pd.DataFrame(data={CONDITION_ID: ["c0"], "B": [2]}).set_index(
    [CONDITION_ID]
)

measurement_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a", "obs_a"],
        SIMULATION_CONDITION_ID: ["c0", "c0"],
        TIME: [0, 10],
        MEASUREMENT: [0.7, 0.1],
    }
)

observable_df = pd.DataFrame(
    data={
        OBSERVABLE_ID: ["obs_a"],
        OBSERVABLE_FORMULA: ["A"],
        NOISE_FORMULA: [0.5],
    }
).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(
    data={
        PARAMETER_ID: ["k1", "k2"],
        PARAMETER_SCALE: [LIN] * 2,
        LOWER_BOUND: [0] * 2,
        UPPER_BOUND: [10] * 2,
        NOMINAL_VALUE: [0.8, 0.6],
        ESTIMATE: [1] * 2,
    }
).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    analytical_a(t, 1, 2, 0.8, 0.6) for t in simulation_df[TIME]
]

case = PetabTestCase(
    id=11,
    brief="Simulation. InitialAssignment to species overridden.",
    description=DESCRIPTION,
    model=model_file,
    condition_dfs=[condition_df],
    observable_dfs=[observable_df],
    measurement_dfs=[measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=parameter_df,
)
