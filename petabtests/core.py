import importlib
import logging
import os
import re
import sys

from petab.calculate import calculate_chi2, calculate_llh

from .C import CASES_DIR
from .file import (PetabTestCase, write_info, write_problem, write_solution,
                   test_id_str)

__all__ = ['get_cases', 'create', 'clear']

logger = logging.getLogger("petab_test_suite")


def get_cases(format: str):
    return sorted(f.name for f in os.scandir(CASES_DIR / format) if f.is_dir()
                  and re.match(r'^\d+$', f.name))


def create():
    """Create all test files."""
    formats = ('sbml', 'pysb')

    for format in formats:
        case_list = get_cases(format=format)
        toc = ""

        for case_id in case_list:
            case_dir = CASES_DIR / format / case_id
            logger.info('# ', format, case_id, case_dir)

            # load test case module
            #  directory needs to be removed from path again and the module
            #  has to be unloaded, as modules from different model format
            #  suites have the same name
            sys.path.append(str(case_dir))
            case_module = importlib.import_module(case_id)
            sys.path.pop()
            # noinspection PyUnresolvedReferences
            case: PetabTestCase = case_module.case
            del sys.modules[case_id]

            id_str = test_id_str(case.id)
            toc += f"# [{id_str}]({id_str}/)\n\n{case.brief}\n\n"

            write_info(case, format)

            write_problem(test_id=case.id,
                          parameter_df=case.parameter_df,
                          condition_dfs=case.condition_dfs,
                          observable_dfs=case.observable_dfs,
                          measurement_dfs=case.measurement_dfs,
                          model_files=case.model,
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

        toc_path = CASES_DIR / format / "README.md"
        with open(toc_path, "w") as f:
            f.write(toc)


def clear():
    """Clear all model folders."""

    case_list = os.scandir(CASES_DIR)
    for case in case_list:
        case_dir = os.path.join(CASES_DIR, case)
        for file_ in os.scandir(case_dir):
            if file_.name.startswith('_') and not file_.is_dir():
                os.remove(file_.path)
