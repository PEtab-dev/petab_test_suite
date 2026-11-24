from inspect import cleandoc

from petab.v2 import Problem
from petab.v2.C import *

from petabtests import (
    DEFAULT_PYSB_FILE,
    PetabV2TestCase,
    analytical_a,
    analytical_b,
)

DESCRIPTION = cleandoc("""
## Objective

This case tests support for time-point specific overrides in the measurement
table.

The model is to be simulated for a single experimental condition. The
noise parameters differ between timepoints for both model outputs:

* `obs_a` is scaled by a different numeric value at each timepoint. Its
  noise formula is not just the noise parameter placeholder, so the numeric
  override must be substituted into the noise formula, not used as standard
  deviation directly.
* `obs_b` has a noise formula that consists only of the noise parameter
  placeholder, so the numeric override is the standard deviation.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------
problem = Problem()

problem.add_observable(
    "obs_a",
    "observableParameter1_obs_a * A",
    noise_formula="2 * noiseParameter1_obs_a",
    observable_placeholders=["observableParameter1_obs_a"],
    noise_placeholders=["noiseParameter1_obs_a"],
)

problem.add_measurement(
    "obs_a",
    time=0,
    measurement=0.7,
    observable_parameters=(10,),
    noise_parameters=(0.5,),
)
problem.add_measurement(
    "obs_a",
    time=10,
    measurement=0.1,
    observable_parameters=(15,),
    noise_parameters=(2,),
)

problem.add_observable(
    "obs_b",
    "B",
    noise_formula="noiseParameter1_obs_b",
    noise_placeholders=["noiseParameter1_obs_b"],
)

problem.add_measurement(
    "obs_b",
    time=0,
    measurement=0.2,
    noise_parameters=(0.3,),
)
problem.add_measurement(
    "obs_b",
    time=10,
    measurement=1.0,
    noise_parameters=(1.5,),
)

problem.add_parameter("a0", lb=0, ub=10, nominal_value=1, estimate=True)
problem.add_parameter("b0", lb=0, ub=10, nominal_value=0, estimate=True)
problem.add_parameter("k1", lb=0, ub=10, nominal_value=0.8, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=0.6, estimate=True)
# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    10 * analytical_a(0, 1, 0, 0.8, 0.6),
    15 * analytical_a(10, 1, 0, 0.8, 0.6),
    analytical_b(0, 1, 0, 0.8, 0.6),
    analytical_b(10, 1, 0, 0.8, 0.6),
]

case = PetabV2TestCase(
    id=6,
    brief="Simulation. Time-point specific numeric observable and noise "
    "parameter overrides, with and without scaling in the noise formula.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    condition_dfs=[problem.condition_df],
    observable_dfs=[problem.observable_df],
    measurement_dfs=[problem.measurement_df],
    simulation_dfs=[simulation_df],
    parameter_df=problem.parameter_df,
)
