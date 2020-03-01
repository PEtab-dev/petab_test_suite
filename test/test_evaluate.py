from petabtests import evaluate_simulations, evaluate_chi2, evaluate_llh
from petab.C import *
import pandas as pd


def test_evaluate_chi2():
    assert evaluate_chi2(0.5, 0.5001)
    assert not evaluate_chi2(0.5, 0.501)


def test_evaluate_llh():
    assert evaluate_llh(0.5, 0.5001)
    assert not evaluate_llh(0.5, 0.501)


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

    gt_simulations_df = pd.DataFrame(data={
        OBSERVABLE_ID: ['obs_a', 'obs_a'],
        SIMULATION_CONDITION_ID: ['c0', 'c1'],
        TIME: [0, 10],
        SIMULATION: [0.71, 0.099999]
    })

    assert not evaluate_simulations(simulations_df, gt_simulations_df)
