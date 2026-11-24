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

This case tests species changes after the first period whose target value
depends on an estimated parameter, `time`, and another species via the
mapping table.

`A` is set to `p * time / 10 + B_c`, with the estimated parameter `p`,
where `B_c` is mapped to `B`:

* `e_t10`: The experiment starts at `t=0` without changes. At `t=10`,
  `A` is set to `p + B(10)`.
* `e_preeq`: After pre-equilibration without changes, the main period
  starts at `t=5`, where `A` is set to `p / 2 + B_ss`, with `B_ss` the
  steady-state value of `B`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

a0 = 1
b0 = 1
k1 = 0.8
k2 = 0.6
p = 3

problem = Problem()

problem.add_condition("c_expr", A_c="p * time / 10 + B_c")
problem.add_experiment("e_t10", 0, "", 10, "c_expr")
problem.add_experiment("e_preeq", TIME_PREEQUILIBRATION, "", 5, "c_expr")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)

ts = {"e_t10": [0, 10, 15], "e_preeq": [5, 10]}
for experiment_id, exp_ts in ts.items():
    for observable_id in ("obs_a", "obs_b"):
        for t in exp_ts:
            problem.add_measurement(
                observable_id,
                experiment_id=experiment_id,
                time=t,
                measurement=1,
            )

problem.add_parameter("k1", lb=0, ub=10, nominal_value=k1, estimate=True)
problem.add_parameter("k2", lb=0, ub=10, nominal_value=k2, estimate=True)
problem.add_parameter("p", lb=0, ub=10, nominal_value=p, estimate=True)

problem.add_mapping("A_c", "A_() ** compartment")
problem.add_mapping("B_c", "B_() ** compartment")

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)

# e_t10
b10 = analytical_b(10, a0, b0, k1, k2)
a10_new = p * 10 / 10 + b10
# e_preeq
b_ss = k1 * (a0 + b0) / (k1 + k2)
a5_new = p * 5 / 10 + b_ss

simulation_df[SIMULATION] = [
    # e_t10, obs_a
    a0,
    a10_new,
    analytical_a(5, a10_new, b10, k1, k2),
    # e_t10, obs_b
    b0,
    b10,
    analytical_b(5, a10_new, b10, k1, k2),
    # e_preeq, obs_a
    a5_new,
    analytical_a(5, a5_new, b_ss, k1, k2),
    # e_preeq, obs_b
    b_ss,
    analytical_b(5, a5_new, b_ss, k1, k2),
]

case = PetabV2TestCase.from_problem(
    id=42,
    brief="Simulation. Preequilibration. Non-zero simulation start time. "
    "Species change after the first period with `time`, an estimated "
    "parameter, and a mapped species in the target value.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
