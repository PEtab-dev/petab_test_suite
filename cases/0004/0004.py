from petabtests import *
from petab.C import *
import petab

import pandas as pd


test_id = 4

# problem --------------------------------------------------------------------

model = DEFAULT_SBML_FILE

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0'],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [0, 10],
    MEASUREMENT: [0.7, 0.1],
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['scaling_A * A + offset_A'],
    NOISE_FORMULA: [1]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['a0', 'b0', 'k1', 'k2', 'scaling_A', 'offset_A'],
    PARAMETER_SCALE: [LIN] * 6,
    LOWER_BOUND: [0] * 6,
    UPPER_BOUND: [10] * 6,
    NOMINAL_VALUE: [1, 0, 0.8, 0.6, 0.5, 2],
    ESTIMATE: [1] * 6,
}).set_index(PARAMETER_ID)


# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [0.5 * analytical_a(t, 1, 0, 0.8, 0.6) + 2
                             for t in simulation_df[TIME]]

chi2 = petab.calculate_chi2(
    measurement_df, simulation_df, observable_df, parameter_df)

llh = petab.calculate_llh(
    measurement_df, simulation_df, observable_df, parameter_df)
print(llh)
