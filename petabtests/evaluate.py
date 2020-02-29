import numpy as np
import pandas as pd
from .C import *


def evaluate_simulations(
        simulations_df: pd.DataFrame,
        gt_simulations_df: pd.DataFrame,
        tol: float = 1e-3):
    simulations = simulations
