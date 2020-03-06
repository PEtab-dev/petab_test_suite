"""File input and output."""

from typing import Callable, List, Union
import pandas as pd
import petab
from petab.C import *  # noqa: F403
import yaml
from shutil import copyfile

from .C import *  # noqa: F403


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
        sbml_files: Union[List[str], str] = None,
        ) -> None:
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
    print(f"Writing case {test_id}...")
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

    # copy models
    if sbml_files is None:
        sbml_files = [DEFAULT_MODEL_FILE]
    copied_sbml_files = []
    for i_sbml, sbml_file in enumerate(sbml_files):
        if len(sbml_files) == 1:
            copied_sbml_file = '_model.xml'
        else:
            copied_sbml_file = f'_model{i_sbml}.xml'
        copyfile(os.path.join(dir_, sbml_file),
                 os.path.join(dir_, copied_sbml_file))
        copied_sbml_files.append(copied_sbml_file)
    config[PROBLEMS][0][SBML_FILES] = copied_sbml_files

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

    # validate petab yaml
    petab.validate(config, path_prefix=dir_)

    # write yaml
    yaml_file = problem_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

    # validate written PEtab files
    problem = petab.Problem.from_yaml(os.path.join(dir_, yaml_file))
    petab.lint_problem(problem)


def write_solution(
        test_id: int,
        simulation_dfs: List[pd.DataFrame],
        chi2: float,
        llh: float,
        tol_simulations: float = 1e-3,
        tol_chi2: float = 1e-3,
        tol_llh: float = 1e-3):
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
        TOL_SIMULATIONS: float(tol_simulations),
        TOL_CHI2: float(tol_chi2),
        TOL_LLH: float(tol_llh)
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


def load_solution(test_id: Union[int, str]):
    id_str = test_id_str(test_id)
    dir_ = os.path.join(CASES_DIR, id_str)

    # load yaml
    yaml_file = solution_yaml_name(id_str)
    with open(os.path.join(dir_, yaml_file)) as f:
        config = yaml.full_load(f)

    # load data
    simulation_dfs = [
        pd.read_csv(os.path.join(dir_, simulation_file), sep='\t')
        for simulation_file in config[SIMULATION_FILES]]

    config.pop(SIMULATION_FILES)
    config[SIMULATION_DFS] = simulation_dfs

    return config
