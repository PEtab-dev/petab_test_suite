from petabtests import evaluate_simulations
from petab.C import *
import pandas as pd


def test_evaluate_simulations():
    simulations_df = pd.DataFrame(data={
        OBSERVABLE_ID: ['obs_a', 'obs_a'],
        SIMULATION_CONDITION_ID: ['c0', 'c1'],
        TIME: [0, 10],
        SIMULATION: [0.7, 0.1]
    })

    gt_simulations_df = pd.DataFrame(data={
        OBSERVABLE_ID: ['obs_a', 'obs_a'],
        SIMULATION_CONDITION_ID: ['c0', 'c1'],
        TIME: [0, 10],
        SIMULATION: [0.700001, 0.099999]
    })

    assert evaluate_simulations(simulations_df, gt_simulations_df)
