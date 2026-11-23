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

This case tests species changes to estimated parameter-dependent values in
and after pre-equilibration.

* `e_preeq_b`: For pre-equilibration, `B` is initialized with `4 * p`,
  with the estimated parameter `p`. The main period starts at `t=0` without
  changes, i.e., from the steady state.
* `e_main_a`: After pre-equilibration without changes, `A` is set to
  `4 * p` at the start of the main period at `t=0`. `B` keeps its
  steady-state value.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
""")

# problem --------------------------------------------------------------------

a0 = 1
b0 = 1
k1 = 0.8
k2 = 0.6
p = 0.5

problem = Problem()

problem.add_condition("c_b", B_c="4 * p")
problem.add_condition("c_a", A_c="4 * p")
problem.add_experiment("e_preeq_b", TIME_PREEQUILIBRATION, "c_b", 0, "")
problem.add_experiment("e_main_a", TIME_PREEQUILIBRATION, "", 0, "c_a")

problem.add_observable("obs_a", "A", noise_formula=0.5)
problem.add_observable("obs_b", "B", noise_formula=0.5)

ts = [0, 10]
for experiment_id in ("e_preeq_b", "e_main_a"):
    for observable_id in ("obs_a", "obs_b"):
        for t in ts:
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

# e_preeq_b: steady state for A(0) = a0, B(0) = 4 * p
total = a0 + 4 * p
a_ss_b = k2 * total / (k1 + k2)
b_ss_b = k1 * total / (k1 + k2)
# e_main_a: steady state for A(0) = a0, B(0) = b0, then A = 4 * p
b_ss = k1 * (a0 + b0) / (k1 + k2)
a_new = 4 * p

simulation_df[SIMULATION] = [
    # e_preeq_b
    a_ss_b,
    a_ss_b,
    b_ss_b,
    b_ss_b,
    # e_main_a
    *(analytical_a(t, a_new, b_ss, k1, k2) for t in ts),
    *(analytical_b(t, a_new, b_ss, k1, k2) for t in ts),
]

case = PetabV2TestCase.from_problem(
    id=43,
    brief="Simulation. Preequilibration. Estimated parameter-dependent "
    "species changes in and after preequilibration.",
    description=DESCRIPTION,
    model=DEFAULT_PYSB_FILE,
    problem=problem,
    simulation_df=simulation_df,
)
