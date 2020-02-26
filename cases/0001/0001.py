from petabtests import *
from petab.C import *

import pandas as pd


# problem --------------------------------------------------------------------

test_id = 1

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0'],
    'a0': [1],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    SIMULATION_CONDITION_ID: ['c0', 'c1'],
    TIME: [0, 10],
    MEASUREMENT: [0, 1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_b'],
    OBSERVABLE_FORMULA: ['A', 'B'],
    NOISE_FORMULA: [1, 1]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['b0', 'k1', 'k2'],
    PARAMETER_SCALE: [LIN] * 3,
    LOWER_BOUND: [0] * 3,
    UPPER_BOUND: [10] * 3,
    NOMINAL_VALUE: [0, 0.8, 0.6],
    ESTIMATE: [1] * 3,
})

# write files

write_problem(test_id=test_id,
              parameter_df=parameter_df,
              condition_dfs=[condition_df],
              observable_dfs=[observable_df],
              measurement_dfs=[measurement_df])

# results --------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
simulation_df[SIMULATION] = [analytical_b(t, 1, 0, 0.8, 0.6) \
                             for t in simulation_df[TIME]]


# write files

write_solution(test_id=test_id,
               llh=None,
               chi2=None,
               simulation_dfs=[simulation_df])
