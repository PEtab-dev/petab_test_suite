import importlib
import itertools
import logging
import os
import re
import sys
from pathlib import Path
from collections.abc import Iterable

from petab.v1.calculate import calculate_chi2, calculate_llh

from .C import CASES_DIR
from .file import (
    PetabTestCase,
    get_case_dir,
    test_id_str,
    write_info,
    write_problem,
    write_solution,
)

__all__ = ["get_cases", "create_all", "clear", "get_cases_dir"]

test_formats = ("sbml", "pysb")
test_versions = ("v1.0.0", "v2.0.0")

logger = logging.getLogger("petab_test_suite")


def get_cases_dir(format_: str, version: str) -> Path:
    """Get the directory of the test cases for the given PEtab version and
    model format."""
    return CASES_DIR / version / format_


def get_cases(format_: str, version: str) -> Iterable[str]:
    """Get the list of test case IDs for the given PEtab version and model
    format."""
    cases_dir = get_cases_dir(format_=format_, version=version)
    if not cases_dir.exists():
        return []
    return sorted(
        f.name
        for f in os.scandir(cases_dir)
        if f.is_dir() and re.match(r"^\d+$", f.name)
    )


def create_all():
    """Create all test files."""
    for version, format_ in itertools.product(test_versions, test_formats):
        case_list = get_cases(format_=format_, version=version)
        if not case_list:
            continue

        # Table of contents markdown string for the current format x version
        #  directory README
        toc = ""

        for case_id in case_list:
            case_dir = get_case_dir(
                format_=format_, version=version, id_=case_id
            )
            logger.info(
                f"Processing {version}/{format_} #{case_id} at {case_dir}"
            )

            case = load_case(case_dir, case_id)

            id_str = test_id_str(case.id)
            toc += f"# [{id_str}]({id_str}/)\n\n{case.brief}\n\n"

            create_case(format_, version, case_id)

        toc_path = (
            get_cases_dir(format_=format_, version=version) / "README.md"
        )
        with open(toc_path, "w") as f:
            f.write(toc)


def load_case(case_dir: Path, case_id: str) -> PetabTestCase:
    """Load a test case definition module."""
    sys.path.append(str(case_dir))
    case_module = importlib.import_module(case_id)
    sys.path.pop()
    # noinspection PyUnresolvedReferences
    case: PetabTestCase = case_module.case
    del sys.modules[case_id]
    return case


def create_case(format_: str, version: str, id_: str) -> None:
    """Create a single test case."""
    case_dir = get_case_dir(format_=format_, version=version, id_=id_)
    case = load_case(case_dir, id_)

    write_info(case, format_, version=version)

    write_problem(
        test_id=case.id,
        parameter_df=case.parameter_df,
        condition_dfs=case.condition_dfs,
        experiment_dfs=case.experiment_dfs,
        observable_dfs=case.observable_dfs,
        measurement_dfs=case.measurement_dfs,
        model_files=case.model,
        format_=format_,
        version=version,
        mapping_df=case.mapping_df,
    )

    chi2 = calculate_chi2(
        case.measurement_dfs,
        case.simulation_dfs,
        case.observable_dfs,
        case.parameter_df,
    )
    llh = calculate_llh(
        case.measurement_dfs,
        case.simulation_dfs,
        case.observable_dfs,
        case.parameter_df,
    )
    write_solution(
        test_id=case.id,
        chi2=chi2,
        llh=llh,
        simulation_dfs=case.simulation_dfs,
        format_=format_,
        version=version,
    )


def clear() -> None:
    """Clear all model folders."""
    for version, format_ in itertools.product(test_versions, test_formats):
        case_list = get_cases(format_=format_, version=version)

        for case_id in case_list:
            case_dir = get_case_dir(
                format_=format_, version=version, id_=case_id
            )

            for file_ in os.scandir(case_dir):
                if file_.name.startswith("_") and not file_.is_dir():
                    os.remove(file_.path)


def _cli_create():
    """`petabtests_create` entry point."""
    # initialize logging
    logging.basicConfig(level=logging.INFO)
    create_all()
