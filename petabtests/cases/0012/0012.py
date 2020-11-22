from petabtests import *
from petab.C import *
import petab

import pandas as pd


test_id = 12

# problem --------------------------------------------------------------------

model = DEFAULT_SBML_FILE

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0'],
    'compartment': [3],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [0, 10],
    MEASUREMENT: [0.7, 0.1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['A'],
    NOISE_FORMULA: [0.5]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['k1', 'k2'],
    PARAMETER_SCALE: [LIN] * 2,
    LOWER_BOUND: [0] * 2,
    UPPER_BOUND: [10] * 2,
    NOMINAL_VALUE: [0.8, 0.6],
    ESTIMATE: [1] * 2,
}).set_index(PARAMETER_ID)

# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
# in the model, concentrations are used, which do not depend on the
#  compartment size, so that the species values should stay the same
simulation_df[SIMULATION] = [analytical_a(t, 1, 1, 0.8, 0.6)
                             for t in simulation_df[TIME]]

chi2 = petab.calculate_chi2(
    measurement_df, simulation_df, observable_df, parameter_df)

llh = petab.calculate_llh(
    measurement_df, simulation_df, observable_df, parameter_df)
print(llh)
