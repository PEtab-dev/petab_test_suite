"""File input and output."""

from __future__ import annotations
import os
from dataclasses import dataclass
from shutil import copyfile, SameFileError
from collections.abc import Callable
from pathlib import Path
import pandas as pd
from petab import v1
from petab import v2
import yaml
import petab.v1.C as C1
import petab.v2.C as C2
from .C import *  # noqa: F403
import logging
from petab.v1.lint import lint_problem as lint_problem_v1
from petab.v2.lint import lint_problem as lint_problem_v2
import importlib
import sys

logger = logging.getLogger("petab_test_suite")


__all__ = [
    "get_case_dir",
    "load_solution",
    "PetabV1TestCase",
    "PetabV2TestCase",
    "problem_yaml_name",
    "solution_yaml_name",
    "test_id_str",
    "write_info",
    "write_solution",
]


@dataclass
class PetabV1TestCase:
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

    @staticmethod
    def load(case_dir: Path, case_id: str) -> PetabV1TestCase:
        """Load a test case definition module."""
        sys.path.append(str(case_dir))
        case_module = importlib.import_module(case_id)
        sys.path.pop()
        # noinspection PyUnresolvedReferences
        case: PetabV1TestCase = case_module.case
        del sys.modules[case_id]
        return case

    def write(self, version: str, format_: str):
        """Write the test case to files."""
        from petab.v1.calculate import calculate_chi2, calculate_llh

        self.write_problem(
            format_=format_,
        )

        chi2 = calculate_chi2(
            self.measurement_dfs,
            self.simulation_dfs,
            self.observable_dfs,
            self.parameter_df,
        )
        llh = calculate_llh(
            self.measurement_dfs,
            self.simulation_dfs,
            self.observable_dfs,
            self.parameter_df,
        )

        write_solution(
            test_id=self.id,
            simulation_dfs=self.simulation_dfs,
            chi2=chi2,
            llh=llh,
            version=version,
            format_=format_,
        )

    def write_problem(
        self,
        format_: str = "sbml",
    ) -> None:
        """Write the PEtab problem for a given test to files.

        Parameters
        ----------
        format_: Model format (SBML/PySB)
        """
        test_id = self.id
        version = "v1.0.0"
        format_version = 1
        petab = v1

        print(f"Writing case {version} {format_} {test_id}...")
        # convenience
        condition_dfs = (
            [self.condition_dfs]
            if isinstance(self.condition_dfs, pd.DataFrame)
            else self.condition_dfs
        )
        observable_dfs = (
            [self.observable_dfs]
            if isinstance(self.observable_dfs, pd.DataFrame)
            else self.observable_dfs
        )
        measurement_dfs = (
            [self.measurement_dfs]
            if isinstance(self.measurement_dfs, pd.DataFrame)
            else self.measurement_dfs
        )
        model_files = (
            [self.model] if isinstance(self.model, Path | str) else self.model
        )
        parameter_df = self.parameter_df

        # id to string
        dir_ = get_case_dir(id_=test_id, format_=format_, version=version)

        # petab yaml
        config = {
            C1.FORMAT_VERSION: format_version,
            C1.PROBLEMS: [
                {
                    C1.CONDITION_FILES: [],
                    C1.MEASUREMENT_FILES: [],
                    C1.OBSERVABLE_FILES: [],
                },
            ],
        }

        # copy models
        suffix = ".xml"
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

        config[C1.PROBLEMS][0][C1.SBML_FILES] = copied_model_files

        # write parameters
        parameters_file = "_parameters.tsv"
        petab.write_parameter_df(
            parameter_df, os.path.join(dir_, parameters_file)
        )
        config[C1.PARAMETER_FILE] = parameters_file

        # write conditions
        _write_dfs_to_files(
            dir_,
            "conditions",
            petab.write_condition_df,
            condition_dfs,
            config[C1.PROBLEMS][0][C1.CONDITION_FILES],
        )

        # write observables
        _write_dfs_to_files(
            dir_,
            "observables",
            petab.write_observable_df,
            observable_dfs,
            config[C1.PROBLEMS][0][C1.OBSERVABLE_FILES],
        )

        # write measurements
        _write_dfs_to_files(
            dir_,
            "measurements",
            petab.write_measurement_df,
            measurement_dfs,
            config[C1.PROBLEMS][0][C1.MEASUREMENT_FILES],
        )

        # validate petab yaml
        v1.validate(config, path_prefix=dir_)

        # write yaml
        yaml_file = problem_yaml_name(test_id)
        yaml_path = os.path.join(dir_, yaml_file)
        with open(yaml_path, "w") as outfile:
            yaml.dump(config, outfile, default_flow_style=False)

        # validate written PEtab files
        problem = petab.Problem.from_yaml(yaml_path)
        if lint_problem_v1(problem):
            raise RuntimeError("Invalid PEtab problem, see messages above.")


@dataclass
class PetabV2TestCase:
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

    @staticmethod
    def from_problem(
        id: int,
        problem: v1.Problem,
        model: Path,
        brief: str,
        description: str,
        simulation_df: pd.DataFrame,
    ) -> PetabV2TestCase:
        """Create a PEtab test case from a PEtab problem."""
        return PetabV2TestCase(
            id=id,
            brief=brief,
            description=description,
            model=model,
            experiment_dfs=[df]
            if (df := problem.experiment_df) is not None and not df.empty
            else [],
            condition_dfs=[df]
            if (df := problem.condition_df) is not None and not df.empty
            else [],
            observable_dfs=[df]
            if not (df := problem.observable_df).empty
            else [],
            measurement_dfs=[df]
            if not (df := problem.measurement_df).empty
            else [],
            simulation_dfs=[simulation_df],
            mapping_df=df
            if (df := problem.mapping_df) is not None and not df.empty
            else None,
            parameter_df=problem.parameter_df,
        )

    @staticmethod
    def load(case_dir: Path, case_id: str) -> PetabV2TestCase:
        """Load a test case definition module."""
        sys.path.append(str(case_dir))
        case_module = importlib.import_module(case_id)
        sys.path.pop()
        # noinspection PyUnresolvedReferences
        case: PetabV2TestCase = case_module.case
        del sys.modules[case_id]
        return case

    def write(self, version: str, format_: str):
        """Write the test case to files."""
        from petab.v2.calculate import calculate_chi2, calculate_llh

        self.write_problem(
            format_=format_,
        )

        chi2 = calculate_chi2(
            self.measurement_dfs,
            self.simulation_dfs,
            self.observable_dfs,
            self.parameter_df,
        )
        llh = calculate_llh(
            self.measurement_dfs,
            self.simulation_dfs,
            self.observable_dfs,
            self.parameter_df,
        )

        write_solution(
            test_id=self.id,
            simulation_dfs=self.simulation_dfs,
            chi2=chi2,
            llh=llh,
            version=version,
            format_=format_,
        )

    def write_problem(
        self,
        format_: str = "sbml",
    ) -> None:
        """Write the PEtab problem for a given test to files.

        Parameters
        ----------
        format_: Model format (SBML/PySB)
        """
        version = "v2.0.0"
        format_version = version[1:]
        test_id = self.id
        print(f"Writing case {version} {format_} {test_id}...")
        # convenience
        condition_dfs = (
            [self.condition_dfs]
            if isinstance(self.condition_dfs, pd.DataFrame)
            else self.condition_dfs
        )
        observable_dfs = (
            [self.observable_dfs]
            if isinstance(self.observable_dfs, pd.DataFrame)
            else self.observable_dfs
        )
        measurement_dfs = (
            [self.measurement_dfs]
            if isinstance(self.measurement_dfs, pd.DataFrame)
            else self.measurement_dfs
        )
        experiment_dfs = (
            [self.experiment_dfs]
            if isinstance(self.experiment_dfs, pd.DataFrame)
            else self.experiment_dfs
        )
        mapping_df = self.mapping_df
        model_files = (
            [self.model] if isinstance(self.model, Path) else self.model
        )
        parameter_dfs = [self.parameter_df]

        # id to string
        dir_ = get_case_dir(id_=test_id, format_=format_, version=version)

        # petab yaml
        config = {
            C2.FORMAT_VERSION: format_version,
            C2.PARAMETER_FILES: [],
            C2.CONDITION_FILES: [],
            C2.MEASUREMENT_FILES: [],
            C2.OBSERVABLE_FILES: [],
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

        petab = v2
        config[C2.MODEL_FILES] = {}
        config[C2.EXPERIMENT_FILES] = []
        for model_idx, model_file in enumerate(copied_model_files):
            config[C2.MODEL_FILES][f"model_{model_idx}"] = {
                C2.MODEL_LANGUAGE: format_,
                C2.MODEL_LOCATION: model_file,
            }

        # write parameters
        _write_dfs_to_files(
            dir_,
            "parameters",
            petab.write_parameter_df,
            parameter_dfs,
            config[C2.PARAMETER_FILES],
        )

        # write conditions
        _write_dfs_to_files(
            dir_,
            "conditions",
            petab.write_condition_df,
            condition_dfs,
            config[C2.CONDITION_FILES],
            skip_empty=True,
        )

        # write observables
        _write_dfs_to_files(
            dir_,
            "observables",
            petab.write_observable_df,
            observable_dfs,
            config[C2.OBSERVABLE_FILES],
        )

        # write measurements
        _write_dfs_to_files(
            dir_,
            "measurements",
            petab.write_measurement_df,
            measurement_dfs,
            config[C2.MEASUREMENT_FILES],
        )

        # write experiments
        if experiment_dfs is not None:
            config.setdefault(C2.EXPERIMENT_FILES, [])
            _write_dfs_to_files(
                dir_,
                "experiments",
                v2.write_experiment_df,
                experiment_dfs,
                config[C2.EXPERIMENT_FILES],
            )

        if mapping_df is not None:
            # write mapping table
            mappings_file = "_mapping.tsv"
            petab.write_mapping_df(
                mapping_df, os.path.join(dir_, mappings_file)
            )
            config[C2.MAPPING_FILES] = [mappings_file]

        # write yaml
        yaml_file = problem_yaml_name(test_id)
        yaml_path = os.path.join(dir_, yaml_file)
        with open(yaml_path, "w") as outfile:
            yaml.dump(config, outfile, default_flow_style=False)

        # validate written PEtab files
        if validation_results := lint_problem_v2(yaml_path):
            logger.critical(f"Invalid PEtab problem generated for {dir_}.")
            validation_results.log(logger=logger)


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


def write_info(
    case: PetabV1TestCase | PetabV2TestCase, format_: str, version: str
) -> None:
    """Write test info markdown file"""
    # id to string
    dir_ = get_case_dir(id_=case.id, format_=format_, version=version)
    id_str = test_id_str(case.id)
    filename = dir_ / "README.md"
    with open(filename, "w") as f:
        f.write(f"# PEtab test case {id_str}\n\n")
        f.write(case.description)
        f.write("\n")


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
    skip_empty: bool = False,
):
    """Write data frames to files and add them to config."""
    dfs = [
        df for df in dfs if df is not None and (not skip_empty or not df.empty)
    ]
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
