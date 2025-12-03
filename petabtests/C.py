"""Constants."""

from pathlib import Path
import sys

# paths
BASE_DIR = Path(__file__).parent

CASES_DIR = BASE_DIR / "cases"

DEFAULT_SBML_FILE = BASE_DIR / "conversion.xml"
DEFAULT_PYSB_FILE = BASE_DIR / "conversion_pysb.py"

# constants

LLH = "llh"
CHI2 = "chi2"
LOG_PRIOR = "log_prior"

SIMULATION_DFS = "simulation_dfs"
SIMULATION_FILES = "simulation_files"
UNNORM_LOG_POSTERIOR = "unnorm_log_posterior"
TOL_SIMULATIONS = "tol_simulations"
TOL_CHI2 = "tol_chi2"
TOL_LLH = "tol_llh"
TOL_LOG_PRIOR = "tol_log_prior"
TOL_UNNORM_LOG_POSTERIOR = "tol_unnorm_log_posterior"

__all__ = [
    x
    for x in dir(sys.modules[__name__])
    if not x.startswith("_") and x not in {"sys", "Path"}
]
