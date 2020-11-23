"""Constants."""

import os
import re

# paths

BASE_DIR = os.path.dirname(__file__)

CASES_DIR = os.path.join(BASE_DIR, 'cases')
SBML_DIR = os.path.join(CASES_DIR, 'sbml')
PYSB_DIR = os.path.join(CASES_DIR, 'pysb')

CASES_LIST = sorted(f.name for f in os.scandir(CASES_DIR) if f.is_dir()
                    and re.match(r'^\d+$', f.name))

DEFAULT_SBML_FILE = os.path.join(BASE_DIR, 'conversion.xml')
DEFAULT_PYSB_FILE = os.path.join(BASE_DIR, 'conversion_pysb.pysb')

# constants

LLH = 'llh'
CHI2 = 'chi2'
SIMULATION_DFS = 'simulation_dfs'
SIMULATION_FILES = 'simulation_files'

TOL_SIMULATIONS = 'tol_simulations'
TOL_CHI2 = 'tol_chi2'
TOL_LLH = 'tol_llh'
