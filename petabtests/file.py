"""File input and output."""

import os
from dataclasses import dataclass
from shutil import copyfile, SameFileError
from collections.abc import Callable
from pathlib import Path
import pandas as pd
from petab import v1
from petab import v2
import yaml
from petab.v1.C import *  # noqa: F403
from .C import *  # noqa: F403
from pprint import pprint
import logging
from petab.v2.C import EXPERIMENT_FILES
from petab.v1.lint import lint_problem as lint_problem_v1
from petab.v2.lint import lint_problem as lint_problem_v2

logger = logging.getLogger("petab_test_suite")


__all__ = [
    "get_case_dir",
    "load_solution",
    "PetabTestCase",
    "problem_yaml_name",
    "solution_yaml_name",
    "test_id_str",
    "write_info",
    "write_problem",
    "write_solution",
]


@dataclass
class PetabTestCase:
    """A PEtab test case"""

    id: int
    brief: str
    description: str
    model: Path
    condition_dfs: list[pd.DataFrame]
    observable_dfs: list[pd.DataFrame]
    measurement_dfs: list[pd.DataFrame]
    simulation_dfs: list[pd.DataFrame]
    parameter_df: pd.DataFrame
    mapping_df: pd.DataFrame = None
    experiment_dfs: list[pd.DataFrame] = None


def get_case_dir(id_: int | str, format_: str, version: str) -> Path:
    """Get the directory of a test case."""
    id_str = test_id_str(id_)
    dir_ = CASES_DIR / version / format_ / id_str
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_


def problem_yaml_name(_id: int | str) -> str:
    """Get the name of the problem yaml file."""
    return "_" + test_id_str(_id) + ".yaml"


def solution_yaml_name(_id: int | str) -> str:
    """Get the name of the solution yaml file."""
    return "_" + test_id_str(_id) + "_solution.yaml"


def test_id_str(_id: int | str) -> str:
    """Get the test id as a string."""
    return f"{_id:0>4}"


def write_info(case: PetabTestCase, format_: str, version: str) -> None:
    """Write test info markdown file"""
    # id to string
    dir_ = get_case_dir(id_=case.id, format_=format_, version=version)
    id_str = test_id_str(case.id)
    filename = dir_ / "README.md"
    with open(filename, "w") as f:
        f.write(f"# PEtab test case {id_str}\n\n")
        f.write(case.description)
        f.write("\n")


def write_problem(
    test_id: int,
    parameter_df: pd.DataFrame,
    condition_dfs: list[pd.DataFrame] | pd.DataFrame,
    experiment_dfs: list[pd.DataFrame] | pd.DataFrame,
    observable_dfs: list[pd.DataFrame] | pd.DataFrame,
    measurement_dfs: list[pd.DataFrame] | pd.DataFrame,
    model_files: list[Path] | Path,
    version: str,
    mapping_df: pd.DataFrame = None,
    format_: str = "sbml",
) -> None:
    """Write the PEtab problem for a given test to files.

    Parameters
    ----------
    test_id: Identifier of the test.
    parameter_df: PEtab parameter table.
    condition_dfs: PEtab condition tables.
    experiment_dfs: PEtab experiment tables.
    observable_dfs: PEtab observable tables.
    measurement_dfs: PEtab measurement tables.
    model_files: PEtab SBML/PySB files.
    format_: Model format (SBML/PySB)
    mapping_df: PEtab mapping table
    version: PEtab version
    """
    print(f"Writing case {version} {format_} {test_id}...")
    # convenience
    if isinstance(condition_dfs, pd.DataFrame):
        condition_dfs = [condition_dfs]
    if isinstance(observable_dfs, pd.DataFrame):
        observable_dfs = [observable_dfs]
    if isinstance(measurement_dfs, pd.DataFrame):
        measurement_dfs = [measurement_dfs]
    if isinstance(model_files, str | Path):
        model_files = [model_files]

    # id to string
    dir_ = get_case_dir(id_=test_id, format_=format_, version=version)
    if (
        version == "v1.0.0"
        or SIMULATION_CONDITION_ID in measurement_dfs[0]
        and not (version == "v2.0.0" and test_id == 19)
    ):
        format_version = 1
    else:
        assert version[0] == "v"
        format_version = version[1:]

    # petab yaml
    config = {
        FORMAT_VERSION: format_version,
        PROBLEMS: [
            {
                CONDITION_FILES: [],
                MEASUREMENT_FILES: [],
                OBSERVABLE_FILES: [],
            },
        ],
    }

    if format_ == "sbml":
        suffix = ".xml"
    else:
        suffix = ".py"

    # copy models
    copied_model_files = []
    for i_sbml, model_file in enumerate(model_files):
        if len(model_files) == 1:
            copied_model_file = f"_model{suffix}"
        else:
            copied_model_file = f"_model{i_sbml}{suffix}"
        try:
            copyfile(
                dir_ / model_file,
                dir_ / copied_model_file,
            )
        except SameFileError:
            pass
        copied_model_files.append(copied_model_file)

    if (
        version == "v1.0.0"
        or SIMULATION_CONDITION_ID in measurement_dfs[0]
        and not (version == "v2.0.0" and test_id == 19)
    ):
        petab = v1
        config[PROBLEMS][0][SBML_FILES] = copied_model_files
    else:
        petab = v2
        config[PROBLEMS][0][MODEL_FILES] = {}
        config[PROBLEMS][0][EXPERIMENT_FILES] = []
        for model_idx, model_file in enumerate(copied_model_files):
            config[PROBLEMS][0][MODEL_FILES][f"model_{model_idx}"] = {
                MODEL_LANGUAGE: format_,
                MODEL_LOCATION: model_file,
            }

    # write parameters
    parameters_file = "_parameters.tsv"
    petab.write_parameter_df(parameter_df, os.path.join(dir_, parameters_file))
    config[PARAMETER_FILE] = parameters_file

    # write conditions
    _write_dfs_to_files(
        dir_,
        "conditions",
        petab.write_condition_df,
        condition_dfs,
        config[PROBLEMS][0][CONDITION_FILES],
    )

    # write observables
    _write_dfs_to_files(
        dir_,
        "observables",
        petab.write_observable_df,
        observable_dfs,
        config[PROBLEMS][0][OBSERVABLE_FILES],
    )

    # write measurements
    _write_dfs_to_files(
        dir_,
        "measurements",
        petab.write_measurement_df,
        measurement_dfs,
        config[PROBLEMS][0][MEASUREMENT_FILES],
    )

    # write experiments
    if experiment_dfs is not None:
        _write_dfs_to_files(
            dir_,
            "experiments",
            v2.write_experiment_df,
            experiment_dfs,
            config[PROBLEMS][0][EXPERIMENT_FILES],
        )

    if format_version != 1 and mapping_df is not None:
        # write mapping table
        mappings_file = "_mapping.tsv"
        petab.write_mapping_df(mapping_df, os.path.join(dir_, mappings_file))
        config[PROBLEMS][0][MAPPING_FILES] = [mappings_file]

    # validate petab yaml
    v1.validate(config, path_prefix=dir_)

    # write yaml
    yaml_file = problem_yaml_name(test_id)
    yaml_path = os.path.join(dir_, yaml_file)
    with open(yaml_path, "w") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

    # FIXME: Until the tests are proper v2 problems, we just auto-upgrade
    #  to a temp directory and copy the files back
    if (
        version == "v2.0.0"
        and SIMULATION_CONDITION_ID in measurement_dfs[0]
        and not (version == "v2.0.0" and test_id == 19)
    ):
        from petab.v2.petab1to2 import petab1to2

        # delete previously auto-generated experiments.tsv
        exp_file = Path(dir_, "_experiments.tsv")
        if exp_file.exists():
            exp_file.unlink()
        petab1to2(yaml_path, dir_)
        # rename auto-generated experiments.tsv
        tmp_exp_file = Path(dir_, "experiments.tsv")
        if tmp_exp_file.exists():
            tmp_exp_file.rename(exp_file)
            # update in yaml
            with open(yaml_path) as f:
                config = yaml.safe_load(f)
            config[PROBLEMS][0][EXPERIMENT_FILES] = ["_experiments.tsv"]
            with open(yaml_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
        format_version = 2

    # validate written PEtab files
    if format_version == 1:
        # PEtab v1
        problem = petab.Problem.from_yaml(yaml_path)
        if lint_problem_v1(problem):
            raise RuntimeError("Invalid PEtab problem, see messages above.")
    else:
        # v2
        validation_results = lint_problem_v2(yaml_path)
        if validation_results:
            logger.error(f"Validation failed for {dir_}:")
            for issue in validation_results:
                pprint(issue)
            raise RuntimeError("Invalid PEtab problem, see messages above.")


def write_solution(
    test_id: int,
    simulation_dfs: list[pd.DataFrame] | pd.DataFrame,
    chi2: float,
    llh: float,
    version: str,
    format_: str = "sbml",
    tol_simulations: float = 1e-3,
    tol_chi2: float = 1e-3,
    tol_llh: float = 1e-3,
):
    """Write solution to files.

    Parameters
    ----------
    test_id: Identifier of the test.
    simulation_dfs: PEtab simulation tables.
    chi2: True chi square value.
    llh: True log likelihood value.
    format_: Model format (SBML/PySB)
    """

    if isinstance(simulation_dfs, pd.DataFrame):
        simulation_dfs = [simulation_dfs]

    # id to string
    dir_ = get_case_dir(id_=test_id, format_=format_, version=version)

    # solution yaml
    config = {
        SIMULATION_FILES: [],
        # round to 14 significant digits, as the last 0 tend to be different
        #  across different systems. avoid repeated modifications of otherwise
        #  unrelated test cases
        CHI2: round(float(chi2), 14),
        LLH: round(float(llh), 14),
        # TODO: add log-prior, log-posterior
        TOL_SIMULATIONS: float(tol_simulations),
        TOL_CHI2: float(tol_chi2),
        TOL_LLH: float(tol_llh),
    }

    # write simulations
    _write_dfs_to_files(
        dir_,
        "simulations",
        # TODO v2
        v1.write_measurement_df,
        simulation_dfs,
        config[SIMULATION_FILES],
    )

    # write yaml
    yaml_file = solution_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file), "w") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def _write_dfs_to_files(
    dir_: Path | str,
    name: str,
    writer: Callable,
    dfs: list[pd.DataFrame],
    config_list: list[str] = None,
):
    """Write data frames to files and add them to config."""
    dfs = [df for df in dfs if df is not None]
    for idx, df in enumerate(dfs):
        if len(dfs) == 1:
            idx = ""
        fname = f"_{name}{idx}.tsv"
        writer(df, Path(dir_, fname))
        if config_list is not None:
            config_list.append(fname)


def load_solution(test_id: int | str, format: str, version: str):
    dir_ = get_case_dir(test_id, format, version=version)

    # load yaml
    yaml_file = solution_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file)) as f:
        config = yaml.full_load(f)

    # load data
    simulation_dfs = [
        pd.read_csv(os.path.join(dir_, simulation_file), sep="\t")
        for simulation_file in config[SIMULATION_FILES]
    ]

    config.pop(SIMULATION_FILES)
    config[SIMULATION_DFS] = simulation_dfs

    return config
