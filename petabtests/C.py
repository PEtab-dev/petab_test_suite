"""Constants."""

from pathlib import Path

# paths
BASE_DIR = Path(__file__).parent

CASES_DIR = BASE_DIR / "cases"

DEFAULT_SBML_FILE = BASE_DIR / "conversion.xml"
DEFAULT_PYSB_FILE = BASE_DIR / "conversion_pysb.py"

# constants

LLH = "llh"
CHI2 = "chi2"
SIMULATION_DFS = "simulation_dfs"
SIMULATION_FILES = "simulation_files"

TOL_SIMULATIONS = "tol_simulations"
TOL_CHI2 = "tol_chi2"
TOL_LLH = "tol_llh"
