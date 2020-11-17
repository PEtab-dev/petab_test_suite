"""File input and output."""

from typing import Callable, List, Union
import pandas as pd
import petab
from petab.C import *  # noqa: F403
import yaml
from shutil import copyfile

from .C import *  # noqa: F403


def case_dir(_id: Union[int, str], format: str) -> str:
    id_str = test_id_str(_id)
    if format == 'sbml':
        dir_ = os.path.join(CASES_DIR, id_str)
    else:
        dir_ = os.path.join(CASES_DIR, format, id_str)
    os.makedirs(dir_, exist_ok=True)
    return dir_


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
        model_files: Union[List[str], str],
        format_: str = 'sbml'
        ) -> None:
    """Write problem to files.

    Parameters
    ----------
    test_id: Identifier of the test.
    parameter_df: PEtab parameter table.
    condition_dfs: PEtab condition tables.
    observable_dfs: PEtab observable tables.
    measurement_dfs: PEtab measurement tables.
    model_files: PEtab SBML/PySB files.
    format: Model format (SBML/PySB)
    """
    print(f"Writing case {test_id} {format_} ...")
    # convenience
    if isinstance(condition_dfs, pd.DataFrame):
        condition_dfs = [condition_dfs]
    if isinstance(observable_dfs, pd.DataFrame):
        observable_dfs = [observable_dfs]
    if isinstance(measurement_dfs, pd.DataFrame):
        measurement_dfs = [measurement_dfs]
    if isinstance(model_files, str):
        model_files = [model_files]

    # id to string
    dir_ = case_dir(test_id, format_)

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

    if format_ == 'sbml':
        suffix = '.xml'
    else:
        suffix = '.py'

    # copy models
    copied_model_files = []
    for i_sbml, model_file in enumerate(model_files):
        if len(model_files) == 1:
            copied_model_file = f'_model{suffix}'
        else:
            copied_model_file = f'_model{i_sbml}{suffix}'
        copyfile(os.path.join(dir_, model_file),
                 os.path.join(dir_, copied_model_file))
        copied_model_files.append(copied_model_file)
    config[PROBLEMS][0][SBML_FILES] = copied_model_files

    # write parameters
    parameters_file = '_parameters.tsv'
    petab.write_parameter_df(parameter_df,
                             os.path.join(dir_, parameters_file))
    config[PARAMETER_FILE] = parameters_file

    # write conditions
    _write_dfs_to_files(dir_, 'conditions',
                        petab.write_condition_df, condition_dfs,
                        config[PROBLEMS][0][CONDITION_FILES])

    # write observables
    _write_dfs_to_files(dir_, 'observables',
                        petab.write_observable_df, observable_dfs,
                        config[PROBLEMS][0][OBSERVABLE_FILES])

    # write measurements
    _write_dfs_to_files(dir_, 'measurements',
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
        simulation_dfs: Union[List[pd.DataFrame], pd.DataFrame],
        chi2: float,
        llh: float,
        format: str = 'sbml',
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
    format: Model format (SBML/PySB)
    """

    if isinstance(simulation_dfs, pd.DataFrame):
        simulation_dfs = [simulation_dfs]

    # id to string
    dir_ = case_dir(test_id, format)

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
    _write_dfs_to_files(dir_, "simulations",
                        petab.write_measurement_df, simulation_dfs,
                        config[SIMULATION_FILES])

    # write yaml
    yaml_file = solution_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def _write_dfs_to_files(
        dir_: str, name: str, writer: Callable,
        dfs: List[pd.DataFrame], config_list: List[str] = None):
    """Write data frames to files and add them to config."""
    for idx, df in enumerate(dfs):
        if len(dfs) == 1:
            idx = ''
        fname = f"_{name}{idx}.tsv"
        writer(df, os.path.join(dir_, fname))
        if config_list is not None:
            config_list.append(fname)


def load_solution(test_id: Union[int, str], format: str):
    dir_ = case_dir(test_id, format)

    # load yaml
    yaml_file = solution_yaml_name(test_id)
    with open(os.path.join(dir_, yaml_file)) as f:
        config = yaml.full_load(f)

    # load data
    simulation_dfs = [
        pd.read_csv(os.path.join(dir_, simulation_file), sep='\t')
        for simulation_file in config[SIMULATION_FILES]]

    config.pop(SIMULATION_FILES)
    config[SIMULATION_DFS] = simulation_dfs

    return config
