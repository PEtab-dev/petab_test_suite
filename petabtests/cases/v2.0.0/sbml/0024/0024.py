from inspect import cleandoc

from petab.v2.C import *
from petab.v2 import Problem
from petabtests import (
    PetabV2TestCase,
    antimony_to_sbml_str,
)
from pathlib import Path
from petab.v2 import PriorDistribution

DESCRIPTION = cleandoc(r"""
## Objective

This case tests different prior distributions, their truncation, as well as
implicit uniform priors and fixed parameters.

## Model

A simple model with all constant parameters.
""")

# problem --------------------------------------------------------------------

priors = [
    (PriorDistribution.UNIFORM, (2, 8)),
    (PriorDistribution.NORMAL, (4, 2)),
    (PriorDistribution.LOG_NORMAL, (5, 2)),
    (PriorDistribution.CAUCHY, (3, 5)),
    (PriorDistribution.CHI_SQUARED, (4)),
    (PriorDistribution.EXPONENTIAL, (3)),
    (PriorDistribution.GAMMA, (3, 5)),
    (PriorDistribution.LAPLACE, (3, 5)),
    (PriorDistribution.LOG_LAPLACE, (3, 5)),
    (PriorDistribution.LOG_UNIFORM, (3, 5)),
    (PriorDistribution.RAYLEIGH, (3)),
]

tested_prior_distrs = {pd for pd, _ in priors}
untested_distrs = [
    pd.value for pd in PriorDistribution if pd not in tested_prior_distrs
]
if untested_distrs:
    print("Untested prior distributions:", untested_distrs)

sbml_file = Path(__file__).parent / "_model.xml"

parameters = "\n".join(
    f"p_{prior_type.value.replace('-', '_')} = 5;" for prior_type, _ in priors
)
ant_model = f"""
model petab_test_0024
    {parameters}
end
"""
sbml_file.write_text(antimony_to_sbml_str(ant_model))

problem = Problem()
for prior_type, prior_pars in priors:
    problem.add_parameter(
        f"p_{prior_type.value.replace('-', '_')}",
        estimate=True,
        lb=0,
        ub=10,
        nominal_value=5,
        prior_distribution=prior_type,
        prior_parameters=prior_pars,
    )
# implicit uniform prior
problem.add_parameter("p1", estimate=True, nominal_value=1, lb=0, ub=2)
# fixed, i.e., no prior
problem.add_parameter("p_fixed", estimate=False, nominal_value=1)
# we need some observable and measurement
problem.add_observable("obs_p1", "p1", noise_formula="p_fixed")
problem.add_measurement("obs_p1", experiment_id="", time=0, measurement=1)

# solutions ------------------------------------------------------------------

simulation_df = problem.measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION}
)
simulation_df[SIMULATION] = [
    3,
]

case = PetabV2TestCase.from_problem(
    id=24,
    brief="Prior distributions.",
    description=DESCRIPTION,
    model=sbml_file,
    problem=problem,
    simulation_df=simulation_df,
)
