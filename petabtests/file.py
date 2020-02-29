"""File input and output."""

from typing import Callable, List, Union
import pandas as pd
import petab
import os
from petab.C import *
import yaml
from shutil import copyfile

from .C import *


def problem_yaml_name(_id: Union[int, str]) -> str:
    return '_' + test_id_str(_id) + '.yaml'


def solution_yaml_name(_id: Union[int, str]) -> str:
    return '_' + test_id_str(_id) + '_solution.yaml'


def test_id_str(_id: str) -> str:
    return f"{_id:0>4}"


def write_problem(
        test_id: int,
        parameter_df: pd.DataFrame,
        condition_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        observable_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        measurement_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        sbml_files: Union[List[str], str] = None) -> None:
    """Write problem to files.

    Parameters
    ----------
    test_id: Identifier of the test.
    parameter_df: PEtab parameter table.
    condition_dfs: PEtab condition tables.
    observable_dfs: PEtab observable tables.
    measurement_dfs: PEtab measurement tables.
    sbml_files: PEtab SBML files. If None, then the default
        petabtests.DEFAULT_MODEL_FILE is used.
    """
    # convenience
    if isinstance(condition_dfs, pd.DataFrame):
        condition_dfs = [condition_dfs]
    if isinstance(observable_dfs, pd.DataFrame):
        observable_dfs = [observable_dfs]
    if isinstance(measurement_dfs, pd.DataFrame):
        measurement_dfs = [measurement_dfs]
    if isinstance(sbml_files, str):
        sbml_files = [sbml_files]

    # id to string
    id_str = test_id_str(test_id)
    dir_ = os.path.join(CASES_DIR, id_str)

    # petab yaml
    config = {
        FORMAT_VERSION: petab.__format_version__,
        PROBLEMS: [
            {
                SBML_FILES: [],
                CONDITION_FILES: [],
                MEASUREMENT_FILES: [],
                OBSERVABLE_FILES: [],
            },
        ]
    }

    # maybe copy models
    if sbml_files is None:
        # use default model
        sbml_files = ['_model.xml']
        copyfile(DEFAULT_MODEL_FILE, os.path.join(dir_, sbml_files[0]))
    config[PROBLEMS][0][SBML_FILES] = sbml_files

    # write parameters
    parameters_file = '_parameters.tsv'
    petab.write_parameter_df(parameter_df,
                             os.path.join(dir_, parameters_file))
    config[PARAMETER_FILE] = parameters_file

    # write conditions
    _write_dfs_to_files(id_str, 'conditions',
                        petab.write_condition_df, condition_dfs,
                        config[PROBLEMS][0][CONDITION_FILES])

    # write observables
    _write_dfs_to_files(id_str, 'observables',
                        petab.write_observable_df, observable_dfs,
                        config[PROBLEMS][0][OBSERVABLE_FILES])

    # write measurements
    _write_dfs_to_files(id_str, 'measurements',
                        petab.write_measurement_df, measurement_dfs,
                        config[PROBLEMS][0][MEASUREMENT_FILES])

    # validate petab
    petab.validate(config, path_prefix=dir_)

    # write yaml
    yaml_file = problem_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def write_solution(
        test_id: int,
        simulation_dfs: List[pd.DataFrame],
        chi2: float,
        llh: float):
    """Write solution to files.

    Parameters
    ----------
    test_id: Identifier of the test.
    simulation_dfs: PEtab simulation tables.
    chi2: True chi square value.
    llh: True log likelihood value.
    """
    # id to string
    id_str = test_id_str(test_id)
    dir_ = os.path.join(CASES_DIR, id_str)

    # solution yaml
    config = {
        SIMULATION_FILES: [],
        CHI2: float(chi2),
        LLH: float(llh),
    }

    # write simulations
    _write_dfs_to_files(id_str, "simulations",
                        petab.write_measurement_df, simulation_dfs,
                        config[SIMULATION_FILES])

    # write yaml
    yaml_file = solution_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def _write_dfs_to_files(
        id_str: str, name: str, writer: Callable,
        dfs: List[pd.DataFrame], config_list: List[str] = None):
    """Write data frames to files and add them to config."""
    for idx, df in enumerate(dfs):
        if len(dfs) == 1:
            idx = ''
        fname = f"_{name}{idx}.tsv"
        writer(df, os.path.join('cases', id_str, fname))
        if config_list is not None:
            config_list.append(fname)