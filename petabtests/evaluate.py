from typing import List, Union
import numpy as np
import pandas as pd
from petab.C import *
from .C import *  # noqa: F403


def evaluate_chi2(chi2: float, gt_chi2: float, tol: float = 1e-3):
    """Evaluate whether chi square values match."""
    if chi2 is None:
        return False
    return abs(chi2 - gt_chi2) < tol


def evaluate_llh(llh: float, gt_llh: float, tol: float = 1e-3):
    """Evaluate whether log likelihoods match."""
    if llh is None:
        return False
    return abs(llh - gt_llh) < tol


def evaluate_simulations(
        simulation_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        gt_simulation_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        tol: float = 1e-3):
    """Evaluate whether simulations match."""
    return absolute_simulations_distance_for_tables(
        simulation_dfs, gt_simulation_dfs) < tol


def absolute_simulations_distance_for_tables(
        simulation_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        gt_simulation_dfs: Union[List[pd.DataFrame], pd.DataFrame]):
    """Compute absolute normalized distance between simulations.

    Parameters
    ----------
    simulation_dfs: PEtab simulation tables proposed by the tool under review.
    gt_simulation_dfs: Ground truth simulation tables.

    Returns
    -------
    distance: The normalized absolute distance.
    """
    # convenience
    if isinstance(simulation_dfs, pd.DataFrame):
        simulation_dfs = [simulation_dfs]
    if isinstance(gt_simulation_dfs, pd.DataFrame):
        gt_simulation_dfs = [gt_simulation_dfs]

    distances = []
    for simulation_df, gt_simulation_df in zip(
            simulation_dfs, gt_simulation_dfs):
        distance = absolute_simulations_distance_for_table(
            simulation_df, gt_simulation_df)
        distances.append(distance)

    distance = sum(distances) / len(distances)
    return distance


def absolute_simulations_distance_for_table(
        simulations: pd.DataFrame,
        gt_simulations: pd.DataFrame):
    """Compute absolute normalized distance between simulations."""
    # gropuing columns
    grouping_cols = [OBSERVABLE_ID, SIMULATION_CONDITION_ID, TIME]
    if PREEQUILIBRATION_CONDITION_ID in simulations:
        grouping_cols.append(PREEQUILIBRATION_CONDITION_ID)
    relevant_cols = grouping_cols.copy()
    # append simulation columng last for correct sorting
    relevant_cols.append(SIMULATION)

    # restrict tables
    simulations = simulations[relevant_cols]
    gt_simulations = gt_simulations[relevant_cols]

    # sort both in the same way to enable direct comparison
    # and to get the smallest distance
    simulations = simulations.sort_values(by=relevant_cols)
    gt_simulations = gt_simulations.sort_values(by=relevant_cols)

    # check if equal grouping is applied
    for col in grouping_cols:
        vals, gt_vals = simulations[col], gt_simulations[col]
        if col == TIME:
            vals, gt_vals = vals.astype(float), gt_vals.astype(float)
            matches = np.isclose(vals, gt_vals).all()
        else:
            vals, gt_vals = vals.astype(str), gt_vals.astype(str)
            matches = (vals == gt_vals).all()
        if not matches:
            raise AssertionError(
                "Simulation dataframes do not match.")

    # compute distance
    return absolute_simulations_distance_for_array(
        np.array(simulations[SIMULATION]),
        np.array(gt_simulations[SIMULATION]))


def absolute_simulations_distance_for_array(
        simulations: np.ndarray,
        gt_simulations: np.ndarray):
    """Compute absolute normalized distance between simulations."""
    return np.abs(simulations - gt_simulations).sum() / len(simulations)
