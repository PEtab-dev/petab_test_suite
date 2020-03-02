"""Constants."""

import os


# paths

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

CASES_DIR = os.path.join(BASE_DIR, 'cases/')
REPO_DIR = os.path.join(BASE_DIR, 'petabtests')

CASES_LIST = sorted(f.name for f in os.scandir(CASES_DIR) if f.is_dir())

DEFAULT_MODEL_FILE = os.path.join(REPO_DIR, 'conversion.xml') 

# constants

LLH = 'llh'
CHI2 = 'chi2'
SIMULATION_DFS = 'simulation_dfs'
SIMULATION_FILES = 'simulation_files'

TOL_SIMULATIONS = 'tol_simulations'
TOL_CHI2 = 'tol_chi2'
TOL_LLH = 'tol_llh'
