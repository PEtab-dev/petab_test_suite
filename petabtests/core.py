import importlib
import logging
import os
import re
import sys

from petab.calculate import calculate_chi2, calculate_llh

from .C import CASES_DIR
from .file import PetabTestCase, write_info, write_problem, write_solution

logger = logging.getLogger("petab_test_suite")


def create():
    """Create all test files."""

    case_list = os.scandir(CASES_DIR)
    case_list = sorted(f.name for f in case_list
                       if f.is_dir() and re.match(r'^\d+$', f.name))

    for case_id in case_list:
        case_dir = os.path.join(CASES_DIR, case_id)
        logger.info('# ', case_id, case_dir)

        sys.path.append(case_dir)
        case_module = importlib.import_module(case_id)

        for format in ['sbml', 'pysb']:
            case: PetabTestCase = case_module.case
            if format == 'sbml':
                model_file = case.model
            else:
                model_file = case.model.replace('.xml', '_pysb.py')

            write_info(case, format)

            write_problem(test_id=case.id,
                          parameter_df=case.parameter_df,
                          condition_dfs=case.condition_dfs,
                          observable_dfs=case.observable_dfs,
                          measurement_dfs=case.measurement_dfs,
                          model_files=model_file,
                          format_=format)

            chi2 = calculate_chi2(
                case.measurement_dfs, case.simulation_dfs, case.observable_dfs,
                case.parameter_df
            )

            llh = calculate_llh(
                case.measurement_dfs, case.simulation_dfs, case.observable_dfs,
                case.parameter_df
            )
            write_solution(test_id=case.id,
                           chi2=chi2,
                           llh=llh,
                           simulation_dfs=case.simulation_dfs,
                           format=format)


def clear():
    """Clear all model folders."""

    case_list = os.scandir(CASES_DIR)
    for case in case_list:
        case_dir = os.path.join(CASES_DIR, case)
        for file_ in os.scandir(case_dir):
            if file_.name.startswith('_') and not file_.is_dir():
                os.remove(file_.path)
