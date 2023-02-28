import importlib
import itertools
import logging
import os
import re
import sys
from pathlib import Path

from petab.calculate import calculate_chi2, calculate_llh

from .C import CASES_DIR
from .file import (PetabTestCase, get_case_dir, test_id_str, write_info,
                   write_problem, write_solution)

__all__ = ['get_cases', 'create', 'clear', 'get_cases_dir']

test_formats = ('sbml', 'pysb')
test_versions = ('v1.0.0', "v2.0.0")

logger = logging.getLogger("petab_test_suite")


def get_cases_dir(format_: str, version: str) -> Path:
    return CASES_DIR / version / format_


def get_cases(format_: str, version: str):
    cases_dir = get_cases_dir(format_=format_, version=version)
    if not cases_dir.exists():
        return []
    return sorted(f.name for f in os.scandir(cases_dir)
                  if f.is_dir()
                  and re.match(r'^\d+$', f.name))


def create():
    """Create all test files."""
    for version, format_ in itertools.product(test_versions, test_formats):
        case_list = get_cases(format_=format_, version=version)
        if not case_list:
            continue

        toc = ""

        for case_id in case_list:
            case_dir = get_case_dir(format_=format_, version=version,
                                    id_=case_id)
            logger.info('# ', format_, version, case_id, case_dir)

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

            write_info(case, format_, version=version)

            write_problem(
                test_id=case.id,
                parameter_df=case.parameter_df,
                condition_dfs=case.condition_dfs,
                observable_dfs=case.observable_dfs,
                measurement_dfs=case.measurement_dfs,
                model_files=case.model,
                format_=format_,
                version=version,
                mapping_df=case.mapping_df
            )

            chi2 = calculate_chi2(
                case.measurement_dfs, case.simulation_dfs, case.observable_dfs,
                case.parameter_df
            )
            llh = calculate_llh(
                case.measurement_dfs, case.simulation_dfs, case.observable_dfs,
                case.parameter_df
            )
            write_solution(
                test_id=case.id,
                chi2=chi2,
                llh=llh,
                simulation_dfs=case.simulation_dfs,
                format_=format_,
                version=version,
            )

        toc_path = get_cases_dir(format_=format_, version=version) \
            / "README.md"
        with open(toc_path, "w") as f:
            f.write(toc)


def clear():
    """Clear all model folders."""
    for version, format_ in itertools.product(test_versions, test_formats):
        case_list = get_cases(format_=format_, version=version)

        for case_id in case_list:
            case_dir = get_case_dir(format_=format_, version=version,
                                    id_=case_id)

            for file_ in os.scandir(case_dir):
                if file_.name.startswith('_') and not file_.is_dir():
                    os.remove(file_.path)
