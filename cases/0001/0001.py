from petabtests import *
from petab.C import *
import pandas as pd

"""Test something"""
test_id = 1

condition_df = pd.DataFrame(data={
    CONDITION_ID: ['c0', 'c1'],
    'a0': [2, 3],
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
    NOMINAL_VALUE: [1] * 3,
    ESTIMATE: [1] * 3,
})

write_files(test_id=test_id,
            condition_dfs=[condition_df],
            measurement_dfs=[measurement_df],
            observable_dfs=[observable_df],
            parameter_df=parameter_df)

# TODO: write test results
